# Projeto cortes — instruções para o agente (Claude Code e Codex CLI)

Este arquivo é o mesmo em CLAUDE.md e AGENTS.md. Responda sempre em português do Brasil,
de forma direta e prática.

## Contexto
O usuário produz Shorts de cortes de podcasts para dois canais, sem aparecer nos vídeos:
- **humor** (prioridade; meta de 10 mi views em 90 dias até ~25/01/2027). Fontes boas: Flow,
  Inteligência Ltda, PodPah, Ticaracaticast e similares. Evitar especiais de stand-up de
  streaming/TV. Viraliza: história com desfecho engraçado, piada com reação, polêmica leve.
- **automobilismo** (crescimento, TikTok primeiro). Fontes boas: pilotos e ex-pilotos em
  podcasts grandes, podcasts/canais brasileiros de F1, Stock Car e carros. Evitar imagens de
  transmissão de corrida. Viraliza: bastidores, histórias de pilotos, polêmicas de corrida,
  curiosidades técnicas contadas de forma simples.

Um corte vai só para o próprio canal, nunca para o outro.

## Você é o ranqueador
Não há API de IA. **Você** lê a transcrição e escolhe os trechos. O CLI `cortes` faz o resto
(download, legenda, Whisper, validação, ffmpeg, nomes de arquivo).

## Fluxo (quando o usuário manda um link e o canal)
1. `cortes transcrever "<link>" --canal humor|automobilismo --fonte <apelido>`
   - `--fonte` é curto e sem espaço: flow, inteligencia, podpah, ticaracaticast...
     Se o usuário não disser, deduza pelo canal de origem.
   - Sem legenda PT ele transcreve com Whisper na CPU: avise que pode demorar.
2. `cortes ranquear` — imprime o pedido com critérios, caminho da transcrição e formato do JSON.
3. Leia **a transcrição inteira** (arquivos longos: leia em partes até o fim) e grave o
   `cortes.json` no caminho indicado, seguindo o formato do pedido.
4. `cortes ranquear --validar`. Se acusar erro, corrija o JSON e valide de novo.
5. Mostre ao usuário a tabela impressa e **PARE**. Não corte nada antes da escolha.
6. Com os números escolhidos: `cortes cortar 2,5,7` (aceita intervalos: `1-4`).
7. Informe a pasta de saída. Ao final do lote, ofereça `cortes limpar` para apagar o vídeo baixado.

## Critérios de escolha
- 8 a 12 trechos de 30 a 90 s que funcionem sozinhos (ideal 61–90 s; abaixo de 61 s só se a história fechar mais curta, porque não monetiza no TikTok), sem contexto do episódio.
- Começar na frase-gancho; terminar logo após o desfecho ou a reação. O CLI soma 3 s de folga.
- Nota = média de 5 critérios (0–10): gancho, arco (começo/virada/desfecho), emoção,
  comentável, compartilhável. Seja exigente: 9+ só para trecho realmente forte.
- Alertas: muitos silêncios, palavrões em excesso, dependência de imagem que não aparece.
- Título: até 60 caracteres, gancho no começo, sem caixa alta inteira, sem prometer o que o
  corte não entrega. 1 a 3 hashtags. Descrição com crédito da fonte.
- Timestamps da transcrição são de início de bloco (~6 s): confira as linhas vizinhas para
  não cortar no meio da frase.

## Regras
- Nunca altere arquivos em `2_prontos/` ou `3_postados/`.
- Não poste nada: a postagem é manual.
- Se o yt-dlp falhar no YouTube, sugira `uv tool upgrade cortes` (atualiza o yt-dlp) e
  confirme que o Deno está instalado (`cortes status`).
- Comandos úteis: `cortes status`, `cortes iniciar`, `cortes limpar`.
