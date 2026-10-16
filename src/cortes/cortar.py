"""cortes cortar: baixa em 1080p, corta com ffmpeg e gera o .txt de cada corte."""
from __future__ import annotations

import datetime as dt
import shutil
import subprocess
from pathlib import Path

import yt_dlp

from .util import Config, ErroCortes, garantir_pastas, hms_para_seg, info, ler_json, slug


def _baixar(link: str, sessao: Path) -> Path:
    existente = next(iter(sessao.glob("video.mp4")), None)
    if existente:
        info("Vídeo já baixado nesta sessão, reaproveitando.")
        return existente
    info("Baixando o vídeo em até 1080p...")
    opts = {
        "format": "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/bv*[height<=1080]+ba/b[height<=1080]",
        "merge_output_format": "mp4",
        "outtmpl": str(sessao / "video.%(ext)s"),
        "quiet": True, "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([link])
    video = sessao / "video.mp4"
    if not video.is_file():
        raise ErroCortes("O download terminou mas não achei video.mp4 na sessão.")
    return video


def _numeros(escolha: str) -> list[int]:
    nums = []
    for parte in escolha.replace(" ", "").split(","):
        if "-" in parte:
            a, b = parte.split("-", 1)
            nums += range(int(a), int(b) + 1)
        elif parte:
            nums.append(int(parte))
    return list(dict.fromkeys(nums))


def _texto_txt(c: dict, meta: dict, inicio: float, fim: float) -> str:
    return (
        f"TÍTULO:\n{c['titulo']} {' '.join(c['hashtags'])}\n\n"
        f"DESCRIÇÃO:\n{c.get('descricao', '')}\n\n"
        f"HASHTAGS:\n{' '.join(c['hashtags'])}\n\n"
        f"---\nNota: {c.get('nota')} | {c.get('porque', '')}\n"
        f"Alertas: {c.get('alertas') or 'nenhum'}\n"
        f"Fonte: {meta.get('titulo_original')} ({meta['link']})\n"
        f"Trecho original: {c['inicio']} a {c['fim']} (arquivo com folga: {inicio:.0f}s a {fim:.0f}s)\n"
    )


def executar(escolha: str, sessao: Path, cfg: Config) -> None:
    if not shutil.which("ffmpeg"):
        raise ErroCortes("ffmpeg não encontrado no PATH. Instale com: winget install Gyan.FFmpeg")
    meta = ler_json(sessao / "meta.json")
    arq = sessao / "cortes.json"
    if not arq.is_file():
        raise ErroCortes("Sem cortes.json validado. Rode o ranqueamento antes.")
    cortes = {c["n"]: c for c in ler_json(arq)["cortes"] if "n" in c}
    if not cortes:
        raise ErroCortes("cortes.json ainda não foi validado. Rode: cortes ranquear --validar")
    nums = _numeros(escolha)
    faltando = [n for n in nums if n not in cortes]
    if faltando:
        raise ErroCortes(f"Números inexistentes na tabela: {faltando}")

    garantir_pastas(cfg)
    destino = cfg.pasta_cortes / meta["canal"] / "1_a_editar"
    video = _baixar(meta["link"], sessao)
    hoje = dt.date.today().isoformat()
    dur_video = meta.get("duracao_s") or 10**9

    for n in nums:
        c = cortes[n]
        ini = max(0.0, hms_para_seg(c["inicio"]) - cfg.folga_s)
        fim = min(float(dur_video), hms_para_seg(c["fim"]) + cfg.folga_s)
        curto = slug(c.get("titulo_curto") or c["titulo"], 40)
        nome = f"{hoje}_{meta['canal']}_{meta['fonte']}_{n:02d}_{curto}"
        saida = destino / f"{nome}.mp4"
        info(f"Cortando {n:02d}: {c['inicio']} a {c['fim']} -> {saida.name}")
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{ini:.2f}", "-i", str(video),
               "-t", f"{fim - ini:.2f}", "-c:v", "libx264", "-preset", cfg.preset,
               "-crf", str(cfg.crf), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
               "-movflags", "+faststart", str(saida)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise ErroCortes(f"ffmpeg falhou no corte {n}:\n{r.stderr[-1500:]}")
        (destino / f"{nome}.txt").write_text(_texto_txt(c, meta, ini, fim), encoding="utf-8")
        print(f"OK {saida}")

    print(f"\n{len(nums)} corte(s) em {destino}")
    print("Para apagar o vídeo baixado desta sessão quando terminar: cortes limpar")
