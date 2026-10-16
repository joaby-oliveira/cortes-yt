---
name: cortes
description: Garimpa cortes de Shorts de um vídeo longo (podcast, entrevista) para os canais humor ou automobilismo usando o CLI `cortes`. Use quando o usuário mandar um link de vídeo com o canal, pedir para ranquear cortes ou passar números de cortes escolhidos.
---

# Garimpo de cortes

Você orquestra o CLI `cortes` (instalado no PC do usuário) e faz o ranqueamento você mesmo.
Responda em português do Brasil.

## Entrada
- Link do vídeo + canal (`humor` ou `automobilismo`). Sem canal: pergunte, porque um corte
  nunca vai para o canal errado.
- Fonte (apelido curto: flow, podpah...). Se não vier, deduza pelo nome do canal de origem.

## Passos
1. Rode `cortes transcrever "<link>" --canal <canal> --fonte <fonte>`.
   Se cair no Whisper, avise que vai demorar (CPU) e aguarde.
2. Rode `cortes ranquear` e siga o pedido que ele imprimir.
3. Leia a transcrição inteira, em partes se for longa. Escolha de 8 a 12 trechos de 30 a 90 s
   que funcionem sozinhos (ideal 61–90 s; menos de 61 s só se a história fechar mais curta,
   porque não monetiza no TikTok). Para cada um, dê nota de 0 a 10 nos 5 critérios (gancho, arco,
   emoção, comentável, compartilhável), escreva o porquê, os alertas, o título (até 60
   caracteres), o titulo_curto, a descrição e de 1 a 3 hashtags.
4. Grave o `cortes.json` no caminho do pedido e rode `cortes ranquear --validar` até passar.
5. Mostre a tabela e **pare**. Pergunte: "Quais números eu corto?"

## Depois da escolha
6. Rode `cortes cortar <números>` (ex.: `2,5,7` ou `1-4`).
7. Responda com a pasta de saída e os nomes dos arquivos, em poucas linhas.
   Ofereça `cortes limpar` quando o lote acabar.

## Não faça
- Não corte antes da escolha do usuário.
- Não invente trecho que não esteja na transcrição.
- Não poste em nenhuma plataforma.
