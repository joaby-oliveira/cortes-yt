---
name: cortes
description: Assistente interativo de garimpo de cortes de Shorts (canais humor e automobilismo) usando o CLI `cortes`. Use quando o usuário digitar /cortes, mandar um link de vídeo longo para cortar, pedir para ranquear cortes ou passar números de cortes escolhidos.
---

# Assistente de cortes (interativo)

Você conduz o usuário passo a passo, como um assistente. Faça **uma pergunta por vez** com a
ferramenta **AskUserQuestion** (múltipla escolha; o usuário sempre pode digitar "Outro").
Nunca peça para o usuário digitar comandos: você roda o CLI `cortes`. Português do Brasil,
mensagens curtas.

Se o usuário já deu alguma informação (link, canal) junto com /cortes, não pergunte de
novo: pule para o próximo passo que falta.

## 1. Coletar o pedido
1. **Link** — se não veio, peça em texto simples: "Cole o link do vídeo do YouTube."
2. **Canal** — AskUserQuestion, header "Canal":
   - "Humor" / "Automobilismo".
   Se o link for claramente de uma fonte de um canal (Flow → humor; podcast de F1 → automobilismo),
   coloque esse primeiro com "(Recomendado)".
   Antes de perguntar, rode `cortes info "<link>"` e mostre numa linha o título, o canal de
   origem, a duração e se há legenda PT. Use o canal de origem para recomendar o canal.
   A fonte (apelido do programa no nome do arquivo) é automática, tirada do canal do YouTube.
   Não pergunte.

## 2. Transcrever
3. Rode `cortes transcrever "<link>" --canal <canal>`.
   Se cair no Whisper, avise numa linha que vai demorar (CPU) e espere.

## 3. Ranquear
5. Rode `cortes ranquear`, leia o pedido e a transcrição inteira (em partes se for longa).
6. Escolha de 8 a 12 trechos de 30 a 90 s que funcionem sozinhos (ideal 61–90 s; menos de 61 s
   só se a história fechar mais curta, porque não monetiza no TikTok). Notas nos 5 critérios,
   porquê, alertas, título (até 60 caracteres), titulo_curto, descrição, 1 a 3 hashtags.
7. Grave o `cortes.json` e rode `cortes ranquear --validar` até passar.
8. Mostre a tabela impressa.

## 4. Escolher os cortes
9. AskUserQuestion, header "Cortes", pergunta "Quais cortes eu corto?":
   - "Top 3 (1, 2, 3)" — se as notas forem boas, marque "(Recomendado)"
   - "Top 5 (1 a 5)"
   - "Todos com nota ≥ 7" (diga quais números entram na descrição da opção)
   - "Nenhum, quero outro vídeo"
   O usuário pode digitar números em "Outro" (ex.: 2,5,7).
10. Se ele pedir ajustes ("começa 5 s antes", "troca o título do 3"), edite o `cortes.json`,
    valide de novo, mostre a tabela e volte ao passo 9.

## 5. Cortar
11. Rode `cortes cortar <números>`. Responda em poucas linhas: pasta e nomes dos arquivos.

## 6. Próximo passo
12. AskUserQuestion, header "Próximo":
    - "Outro vídeo" → volte ao passo 1 (pergunte o canal de novo; sugira o mesmo como Recomendado)
    - "Cortar mais deste vídeo" → volte ao passo 9
    - "Terminar e apagar o vídeo baixado" → `cortes limpar`
    - "Terminar e manter o vídeo"

## Não faça
- Não corte antes da escolha do usuário.
- Não invente trecho que não esteja na transcrição.
- Não poste em nenhuma plataforma.
- Não faça várias perguntas de uma vez.
