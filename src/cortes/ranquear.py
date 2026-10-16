"""cortes ranquear: prepara o pedido para o agente (Claude Code/Codex) e valida a resposta.

Sem API: quem lê a transcrição e escolhe os trechos é o agente que está rodando
o CLI. Este módulo gera o prompt, valida o cortes.json que o agente escreveu,
ordena pela nota, numera e monta a tabela.
"""
from __future__ import annotations

from pathlib import Path

from .util import Config, ErroCortes, gravar_json, hms_para_seg, ler_json, seg_para_hms

CRITERIOS = ("gancho", "arco", "emocao", "comentavel", "compartilhavel")

PERFIL = {
    "humor": "histórias com desfecho engraçado, piada com reação, polêmica leve que gera comentário",
    "automobilismo": "bastidores, histórias de pilotos, polêmicas de corrida, curiosidades técnicas "
                     "contadas de forma simples",
}

PROMPT = """# Pedido de ranqueamento de cortes

Canal: **{canal}** (o que viraliza aqui: {perfil}).
Vídeo: {titulo} ({link})
Transcrição com timestamps: `{transcricao}`

## Tarefa
1. Leia a transcrição inteira.
2. Escolha de 8 a 12 trechos de {dmin:.0f} a {dmax:.0f} segundos que funcionem sozinhos,
   sem contexto do episódio. Prefira começar exatamente na frase-gancho e terminar logo
   após o desfecho/reação (o CLI ainda soma {folga:.0f} s de folga em cada ponta).
3. Dê nota de 0 a 10 para cada critério; a nota final é a média dos 5:
   - gancho: os 3 primeiros segundos prendem sozinhos?
   - arco: tem começo, virada e desfecho dentro do tempo?
   - emocao: riso, choque, curiosidade ou indignação claros?
   - comentavel: gera opinião ou debate nos comentários?
   - compartilhavel: alguém mandaria para um amigo?
4. Em "alertas", indique muitos silêncios, palavrões em excesso ou dependência de imagem
   que não aparece no vídeo (vazio se não houver).
5. Título: até 60 caracteres, gancho no começo, sem caixa alta inteira, sem prometer o que
   o corte não entrega. 1 a 3 hashtags. Descrição: 1 a 2 frases + crédito da fonte.
6. Grave o resultado em `{saida}` exatamente neste formato (UTF-8):

```json
{{
  "cortes": [
    {{
      "inicio": "00:12:03",
      "fim": "00:13:20",
      "gancho": "primeira frase do trecho",
      "criterios": {{"gancho": 9, "arco": 8, "emocao": 9, "comentavel": 7, "compartilhavel": 8}},
      "porque": "por que pode viralizar, em uma frase",
      "titulo": "Título com gancho no começo",
      "titulo_curto": "piada-do-aeroporto",
      "descricao": "Descrição curta. Corte do {canal_origem}.",
      "hashtags": ["#humor", "#podcast"],
      "alertas": ""
    }}
  ]
}}
```

7. Depois rode `cortes ranquear --validar` e mostre ao usuário a tabela que ele imprimir.
   Se der erro, corrija o JSON e valide de novo. Então PARE e espere o usuário escolher os números.
"""


def preparar(sessao: Path, cfg: Config) -> None:
    meta = ler_json(sessao / "meta.json")
    texto = PROMPT.format(
        canal=meta["canal"], perfil=PERFIL.get(meta["canal"], ""),
        titulo=meta.get("titulo_original"), link=meta["link"],
        transcricao=sessao / "transcricao.txt", saida=sessao / "cortes.json",
        dmin=cfg.duracao_min, dmax=cfg.duracao_max, folga=cfg.folga_s,
        canal_origem=meta.get("canal_origem") or meta["fonte"],
    )
    (sessao / "pedido_ranqueamento.md").write_text(texto, encoding="utf-8")
    print(texto)


def _validar_um(i: int, c: dict, cfg: Config, dur_video: float | None) -> list[str]:
    erros = []
    obrig = ("inicio", "fim", "gancho", "criterios", "porque", "titulo", "hashtags")
    for campo in obrig:
        if campo not in c:
            erros.append(f"corte {i}: falta '{campo}'")
    if erros:
        return erros
    try:
        ini, fim = hms_para_seg(c["inicio"]), hms_para_seg(c["fim"])
    except ErroCortes as e:
        return [f"corte {i}: {e}"]
    dur = fim - ini
    if not cfg.duracao_min <= dur <= cfg.duracao_max:
        erros.append(f"corte {i}: duração {dur:.0f}s fora de {cfg.duracao_min:.0f}-{cfg.duracao_max:.0f}s")
    if dur_video and fim > dur_video:
        erros.append(f"corte {i}: fim {c['fim']} passa do fim do vídeo")
    crit = c["criterios"]
    falt = [k for k in CRITERIOS if k not in crit]
    if falt:
        erros.append(f"corte {i}: critérios faltando {falt}")
    elif not all(0 <= float(crit[k]) <= 10 for k in CRITERIOS):
        erros.append(f"corte {i}: critérios devem ficar entre 0 e 10")
    t = c["titulo"]
    if len(t) > 60:
        erros.append(f"corte {i}: título com {len(t)} caracteres (máx. 60)")
    if t.isupper():
        erros.append(f"corte {i}: título todo em caixa alta")
    if not 1 <= len(c["hashtags"]) <= 3:
        erros.append(f"corte {i}: use de 1 a 3 hashtags")
    return erros


def _celula(txt: str) -> str:
    return str(txt).replace("|", "/").replace("\n", " ").strip()


def validar(sessao: Path, cfg: Config) -> None:
    arq = sessao / "cortes.json"
    if not arq.is_file():
        raise ErroCortes(f"Não achei {arq}. O agente precisa gravá-lo antes de validar.")
    meta = ler_json(sessao / "meta.json")
    try:
        dados = ler_json(arq)
    except ValueError as e:
        raise ErroCortes(f"cortes.json não é um JSON válido: {e}") from None
    cortes = dados.get("cortes", [])
    erros = []
    if not 8 <= len(cortes) <= 12:
        erros.append(f"são {len(cortes)} cortes; o padrão é de 8 a 12")
    for i, c in enumerate(cortes, 1):
        erros += _validar_um(i, c, cfg, meta.get("duracao_s"))
    if erros:
        raise ErroCortes("Problemas no cortes.json:\n- " + "\n- ".join(erros))

    for c in cortes:
        c["nota"] = round(sum(float(c["criterios"][k]) for k in CRITERIOS) / 5, 1)
        c["inicio"] = seg_para_hms(hms_para_seg(c["inicio"]))
        c["fim"] = seg_para_hms(hms_para_seg(c["fim"]))
    cortes.sort(key=lambda c: c["nota"], reverse=True)
    for n, c in enumerate(cortes, 1):
        c["n"] = n
    gravar_json(arq, {"cortes": cortes})

    cab = ("| Nº | Início | Fim | Duração | Gancho (primeira frase) | Nota | "
           "Por que pode viralizar | Título sugerido | Hashtags |")
    linhas = [cab, "|" + "---|" * 9]
    for c in cortes:
        dur = hms_para_seg(c["fim"]) - hms_para_seg(c["inicio"])
        porque = c["porque"] + (f" ⚠️ {c['alertas']}" if c.get("alertas") else "")
        linhas.append(
            f"| {c['n']} | {c['inicio']} | {c['fim']} | {dur:.0f}s | {_celula(c['gancho'])} | "
            f"{c['nota']} | {_celula(porque)} | {_celula(c['titulo'])} | "
            f"{' '.join(c['hashtags'])} |")
    tabela = "\n".join(linhas)
    (sessao / "tabela.md").write_text(tabela, encoding="utf-8")
    print(tabela)
    print("\nEscolha os números e rode: cortes cortar 1,3,5")
