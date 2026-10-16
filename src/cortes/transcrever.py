"""cortes transcrever: legendas automáticas PT via yt-dlp; senão faster-whisper."""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import yt_dlp

from .util import (CANAIS, Config, ErroCortes, definir_sessao_atual, garantir_pastas,
                   gravar_json, info, seg_para_hms, slug)

LINGUAS = ["pt-orig", "pt", "pt-BR"]
BLOCO_S = 6.0  # junta as falas em linhas de ~6 s para a transcrição ficar enxuta


def _opts_base() -> dict:
    return {"quiet": True, "no_warnings": True, "noprogress": True}


def _info_video(link: str) -> dict:
    with yt_dlp.YoutubeDL(_opts_base() | {"skip_download": True}) as ydl:
        return ydl.extract_info(link, download=False)


def _escolher_lingua(meta: dict) -> tuple[str, bool] | None:
    """Prefere legenda manual em PT; depois automática."""
    manuais = meta.get("subtitles") or {}
    autos = meta.get("automatic_captions") or {}
    for lang in LINGUAS:
        if lang in manuais:
            return lang, False
    for lang in LINGUAS:
        if lang in autos:
            return lang, True
    return None


def _baixar_legenda(link: str, pasta: Path, lang: str, auto: bool) -> Path | None:
    opts = _opts_base() | {
        "skip_download": True,
        "writesubtitles": not auto,
        "writeautomaticsub": auto,
        "subtitleslangs": [lang],
        "subtitlesformat": "json3",
        "outtmpl": str(pasta / "legenda.%(ext)s"),
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([link])
    achados = list(pasta.glob("legenda*.json3"))
    return achados[0] if achados else None


def _segmentos_json3(arq: Path) -> list[tuple[float, float, str]]:
    dados = json.loads(arq.read_text(encoding="utf-8"))
    segs = []
    for ev in dados.get("events", []):
        if "segs" not in ev:
            continue
        txt = "".join(s.get("utf8", "") for s in ev["segs"]).replace("\n", " ").strip()
        if not txt:
            continue
        ini = ev.get("tStartMs", 0) / 1000
        segs.append((ini, ini + ev.get("dDurationMs", 0) / 1000, txt))
    return segs


def _whisper(link: str, pasta: Path, cfg: Config) -> list[tuple[float, float, str]]:
    from faster_whisper import WhisperModel  # import pesado: só quando precisa

    info("Sem legenda em português. Baixando o áudio para transcrever com Whisper...")
    opts = _opts_base() | {"format": "bestaudio/best",
                           "outtmpl": str(pasta / "audio.%(ext)s")}
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([link])
    audio = next(pasta.glob("audio.*"))
    tipo = "int8" if cfg.whisper_dispositivo == "cpu" else "float16"
    info(f"Transcrevendo com o modelo '{cfg.whisper_modelo}' ({cfg.whisper_dispositivo}). "
         "Isso pode demorar...")
    modelo = WhisperModel(cfg.whisper_modelo, device=cfg.whisper_dispositivo, compute_type=tipo)
    segmentos, _ = modelo.transcribe(str(audio), language="pt", vad_filter=True)
    saida = []
    for s in segmentos:
        saida.append((s.start, s.end, s.text.strip()))
        if len(saida) % 50 == 0:
            info(f"  ... {seg_para_hms(s.end)}")
    audio.unlink(missing_ok=True)
    return saida


def _agrupar(segs: list[tuple[float, float, str]]) -> list[tuple[float, str]]:
    linhas, ini, buf = [], None, []
    for s_ini, _, txt in segs:
        if ini is None:
            ini = s_ini
        buf.append(txt)
        if s_ini - ini >= BLOCO_S:
            linhas.append((ini, " ".join(buf)))
            ini, buf = None, []
    if buf:
        linhas.append((ini or 0, " ".join(buf)))
    return linhas


def executar(link: str, canal: str, fonte: str | None, cfg: Config) -> Path:
    if canal not in CANAIS:
        raise ErroCortes(f"Canal deve ser um de: {', '.join(CANAIS)}")
    garantir_pastas(cfg)
    info("Lendo informações do vídeo...")
    meta = _info_video(link)
    vid = meta.get("id", "video")
    fonte = slug(fonte or meta.get("channel") or meta.get("uploader") or "fonte", 20)
    hoje = dt.date.today().isoformat()
    pasta = cfg.pasta_trabalho / f"{hoje}_{canal}_{fonte}_{vid}"
    pasta.mkdir(parents=True, exist_ok=True)

    escolha = _escolher_lingua(meta)
    segs, origem = [], ""
    if escolha:
        lang, auto = escolha
        info(f"Baixando legenda {'automática' if auto else 'manual'} ({lang})...")
        arq = _baixar_legenda(link, pasta, lang, auto)
        if arq:
            segs = _segmentos_json3(arq)
            origem = f"legenda {'automática' if auto else 'manual'} {lang}"
    if not segs:
        segs = _whisper(link, pasta, cfg)
        origem = f"whisper {cfg.whisper_modelo}"
    if not segs:
        raise ErroCortes("Não consegui obter nenhuma transcrição deste vídeo.")

    linhas = _agrupar(segs)
    txt = "\n".join(f"[{seg_para_hms(t)}] {frase}" for t, frase in linhas)
    (pasta / "transcricao.txt").write_text(txt, encoding="utf-8")
    gravar_json(pasta / "meta.json", {
        "link": link, "id": vid, "titulo_original": meta.get("title"),
        "canal_origem": meta.get("channel") or meta.get("uploader"),
        "duracao_s": meta.get("duration"), "canal": canal, "fonte": fonte,
        "data": hoje, "origem_transcricao": origem,
    })
    definir_sessao_atual(cfg, pasta)
    print(f"Transcrição pronta ({origem}, {len(linhas)} linhas).")
    print(f"Sessão: {pasta}")
    print(f"Arquivo: {pasta / 'transcricao.txt'}")
    print("Próximo passo: cortes ranquear")
    return pasta
