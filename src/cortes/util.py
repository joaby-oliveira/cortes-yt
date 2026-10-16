"""Configuração, sessões e utilidades comuns."""
from __future__ import annotations

import json
import os
import re
import sys
import tomllib
import unicodedata
from dataclasses import dataclass
from pathlib import Path

CANAIS = ("humor", "automobilismo")
SUBPASTAS = ("1_a_editar", "2_prontos", "3_postados")
RAIZ_PROJETO = Path(__file__).resolve().parents[2]


class ErroCortes(Exception):
    """Erro esperado: mostrado ao usuário sem traceback."""


@dataclass
class Config:
    pasta_cortes: Path
    pasta_trabalho: Path
    whisper_modelo: str
    whisper_dispositivo: str
    folga_s: float
    duracao_min: float
    duracao_max: float
    crf: int
    preset: str


def _achar_config() -> Path | None:
    candidatos = []
    if os.environ.get("CORTES_CONFIG"):
        candidatos.append(Path(os.environ["CORTES_CONFIG"]))
    candidatos += [Path.cwd() / "config.toml", RAIZ_PROJETO / "config.toml"]
    return next((c for c in candidatos if c.is_file()), None)


def carregar_config() -> Config:
    caminho = _achar_config()
    dados = tomllib.loads(caminho.read_text(encoding="utf-8")) if caminho else {}
    pasta = Path(os.path.expanduser(dados.get("pasta_cortes", "~/Videos/cortes")))
    trab = dados.get("pasta_trabalho") or ""
    w, c = dados.get("whisper", {}), dados.get("corte", {})
    return Config(
        pasta_cortes=pasta,
        pasta_trabalho=Path(os.path.expanduser(trab)) if trab else pasta / "_trabalho",
        whisper_modelo=w.get("modelo", "small"),
        whisper_dispositivo=w.get("dispositivo", "cpu"),
        folga_s=float(c.get("folga_s", 3)),
        duracao_min=float(c.get("duracao_min", 61)),
        duracao_max=float(c.get("duracao_max", 90)),
        crf=int(c.get("crf", 18)),
        preset=c.get("preset", "medium"),
    )


def garantir_pastas(cfg: Config) -> None:
    for canal in CANAIS:
        for sub in SUBPASTAS:
            (cfg.pasta_cortes / canal / sub).mkdir(parents=True, exist_ok=True)
    cfg.pasta_trabalho.mkdir(parents=True, exist_ok=True)


# ---------- tempo ----------

def seg_para_hms(s: float) -> str:
    s = max(0, int(round(s)))
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def hms_para_seg(txt: str | int | float) -> float:
    if isinstance(txt, (int, float)):
        return float(txt)
    partes = str(txt).strip().replace(",", ".").split(":")
    if not 1 <= len(partes) <= 3:
        raise ErroCortes(f"Tempo inválido: {txt!r} (use HH:MM:SS)")
    try:
        nums = [float(p) for p in partes]
    except ValueError:
        raise ErroCortes(f"Tempo inválido: {txt!r} (use HH:MM:SS)") from None
    total = 0.0
    for n in nums:
        total = total * 60 + n
    return total


# ---------- texto ----------

def slug(txt: str, maximo: int = 40) -> str:
    txt = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode()
    txt = re.sub(r"[^a-zA-Z0-9]+", "-", txt.lower()).strip("-")
    return txt[:maximo].rstrip("-") or "corte"


# ---------- sessão ----------

def arquivo_atual(cfg: Config) -> Path:
    return cfg.pasta_trabalho / "atual.txt"


def definir_sessao_atual(cfg: Config, pasta: Path) -> None:
    arquivo_atual(cfg).write_text(str(pasta), encoding="utf-8")


def sessao_atual(cfg: Config, explicita: str | None = None) -> Path:
    if explicita:
        p = Path(explicita)
        if not p.is_absolute():
            p = cfg.pasta_trabalho / explicita
    else:
        a = arquivo_atual(cfg)
        if not a.is_file():
            raise ErroCortes("Nenhuma sessão ativa. Rode primeiro: cortes transcrever <link> --canal ...")
        p = Path(a.read_text(encoding="utf-8").strip())
    if not (p / "meta.json").is_file():
        raise ErroCortes(f"Sessão inválida: {p}")
    return p


def ler_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def gravar_json(p: Path, dados: dict) -> None:
    p.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def info(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)
