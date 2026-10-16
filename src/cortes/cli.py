"""Ponto de entrada: cortes <comando>."""
from __future__ import annotations

import argparse
import shutil
import sys

from . import __version__
from .util import CANAIS, ErroCortes, carregar_config, garantir_pastas, ler_json, sessao_atual


def _status(args, cfg):
    print(f"Pasta dos cortes: {cfg.pasta_cortes}")
    print(f"ffmpeg: {'ok' if shutil.which('ffmpeg') else 'NÃO ENCONTRADO'}")
    print(f"deno (runtime JS do yt-dlp): {'ok' if shutil.which('deno') else 'não encontrado'}")
    try:
        s = sessao_atual(cfg, args.sessao)
    except ErroCortes:
        print("Sessão ativa: nenhuma")
        return
    m = ler_json(s / "meta.json")
    print(f"Sessão ativa: {s.name}")
    print(f"  {m['canal']} | {m['fonte']} | {m.get('titulo_original')}")
    for arq in ("transcricao.txt", "cortes.json", "tabela.md", "video.mp4"):
        print(f"  {arq}: {'sim' if (s / arq).exists() else 'não'}")


def main(argv: list[str] | None = None) -> int:
    for fluxo in (sys.stdout, sys.stderr):  # acentos no terminal do Windows
        try:
            fluxo.reconfigure(encoding="utf-8")
        except AttributeError:
            pass

    p = argparse.ArgumentParser(prog="cortes", description="Garimpo e corte de Shorts.")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("info", help="mostra título, canal de origem, duração e se há legenda PT")
    i.add_argument("link")

    t = sub.add_parser("transcrever", help="baixa legenda PT ou transcreve com Whisper")
    t.add_argument("link")
    t.add_argument("--canal", required=True, choices=CANAIS)
    t.add_argument("--fonte", help="apelido da fonte no nome do arquivo (ex.: flow)")

    r = sub.add_parser("ranquear", help="gera o pedido para o agente ou valida cortes.json")
    r.add_argument("--validar", action="store_true", help="valida, ordena e imprime a tabela")
    r.add_argument("--sessao")

    c = sub.add_parser("cortar", help="corta os números escolhidos (ex.: 2,5,7 ou 1-4)")
    c.add_argument("numeros")
    c.add_argument("--sessao")

    s = sub.add_parser("status", help="mostra configuração e sessão ativa")
    s.add_argument("--sessao")

    l = sub.add_parser("limpar", help="apaga o vídeo baixado da sessão")
    l.add_argument("--sessao")

    sub.add_parser("iniciar", help="cria a estrutura de pastas")

    args = p.parse_args(argv)
    cfg = carregar_config()
    try:
        if args.cmd == "info":
            from .transcrever import mostrar_info
            mostrar_info(args.link)
        elif args.cmd == "transcrever":
            from .transcrever import executar
            executar(args.link, args.canal, args.fonte, cfg)
        elif args.cmd == "ranquear":
            from . import ranquear
            sessao = sessao_atual(cfg, args.sessao)
            (ranquear.validar if args.validar else ranquear.preparar)(sessao, cfg)
        elif args.cmd == "cortar":
            from .cortar import executar
            executar(args.numeros, sessao_atual(cfg, args.sessao), cfg)
        elif args.cmd == "status":
            _status(args, cfg)
        elif args.cmd == "limpar":
            v = sessao_atual(cfg, args.sessao) / "video.mp4"
            v.unlink(missing_ok=True)
            print("Vídeo da sessão apagado.")
        elif args.cmd == "iniciar":
            garantir_pastas(cfg)
            print(f"Pastas criadas em {cfg.pasta_cortes}")
    except ErroCortes as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
