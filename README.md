# cortes-cli

CLI para garimpar, ranquear (via Claude Code/Codex) e cortar Shorts de podcasts.

Dois canais: **humor** (prioridade) e **automobilismo** (crescimento, TikTok primeiro).
Cada corte vai para YouTube, TikTok, Instagram e Facebook do próprio canal, nunca do outro.

## Metas e estimativas

**Objetivo:** mais de **R$ 1.000/mês** somando YouTube, TikTok e Facebook. Primeiro passo: monetizar o YouTube.

### Prazo crítico do YouTube
| Período | Requisito para entrar no YPP pelos Shorts |
|---|---|
| Até 31/01/2027 | 1.000 inscritos + **10 mi** views de Shorts em 90 dias |
| A partir de 01/02/2027 | 1.000 inscritos + **20 mi** views de Shorts em 90 dias |
| Piso depois de fev/2027 | Receita de Shorts só acima de 10 mi views em 90 dias (~3,4 mi/mês por canal) |

**Meta:** canal de humor com 10 mi views em 90 dias até **~25/01/2027**.

### Premissas de receita (estimativas)
| Plataforma | Paga por mil views | Para R$ 1.000/mês |
|---|---|---|
| YouTube Shorts (Brasil) | R$ 0,05 a 0,21 (uso **R$ 0,10**) | ~10 mi views/mês |
| TikTok | R$ 0,30 a 0,60 (estimativa) | ~1,7 a 3,3 mi views/mês |
| Facebook | por convite | bônus |
| Instagram | não paga por views | afiliados/patrocínio no futuro |

### Requisitos das plataformas
| Plataforma | Requisito para ganhar | Observação |
|---|---|---|
| YouTube | ver tabela do prazo acima | só monetiza corte com edição própria significativa |
| TikTok | 18+, conta no Brasil, 10 mil seguidores, 100 mil views em 30 dias, vídeos com **mais de 1 min** | exportar sem marca d'água; o CLI avisa cortes < 61 s |
| Facebook | monetização de conteúdo por convite | bônus |
| Instagram | não paga por views | — |

Política de conteúdo reutilizado do YouTube avalia o canal todo: corte precisa de edição própria
significativa; conteúdo produzido em massa é considerado inautêntico.

### Ritmo
| | Humor | Automobilismo |
|---|---|---|
| Frequência | 1 corte/dia | 4 a 5/semana; 1/dia em fim de semana de GP |
| Horário | 12h ou 19h30 | 19h; domingo logo após o GP |

Disponibilidade: 14 a 19 h/semana, edição em lote no sábado e domingo.

### Marcos
- [ ] Fim do 1º mês: um corte de humor acima de 500 mil views
- [ ] Meados de janeiro de 2027: humor acima de 7 mi views em 90 dias
- [ ] Até 25/01/2027: humor com 10 mi views em 90 dias e 1.000 inscritos
- [ ] TikTok dos dois canais com 10 mil seguidores
- [ ] Todo mês depois de fevereiro de 2027: humor acima de 3,4 mi views


## Instalação no Windows

Abra o **PowerShell** (não precisa ser como administrador) e siga na ordem.

## 1. Programas base
```powershell
winget install Python.Python.3.12
winget install Gyan.FFmpeg
winget install DenoLand.Deno
winget install astral-sh.uv
winget install Git.Git
```
Feche e abra o PowerShell de novo para o PATH atualizar. Confira:
```powershell
python --version; ffmpeg -version; deno --version; uv --version
```

## 2. Projeto
```powershell
mkdir $HOME\Projetos -Force; cd $HOME\Projetos
git clone https://github.com/joaby-oliveira/cortes-yt.git cortes-cli
cd cortes-cli
uv tool install --editable .
cortes iniciar
cortes status
```
`cortes iniciar` cria `Videos\cortes\humor` e `Videos\cortes\automobilismo`, cada uma com
`1_a_editar`, `2_prontos` e `3_postados`. Para mudar a pasta, edite `config.toml`.

Com `--editable`, alterações no código valem na hora, sem reinstalar.

## 3. Instruções para os agentes
- **Claude Code** lê o `CLAUDE.md` da pasta do projeto: abra o Claude Code dentro de `cortes-cli`.
- **Codex CLI** lê `AGENTS.md`. Crie a cópia:
  ```powershell
  Copy-Item CLAUDE.md AGENTS.md
  ```
  Ao editar um, copie de novo para o outro.

## 4. Skill do Claude Code
```powershell
New-Item -ItemType Directory -Force $HOME\.claude\skills | Out-Null
Copy-Item -Recurse -Force skill\cortes $HOME\.claude\skills\
```
No Claude Code, digite `/cortes` e responda as perguntas (link, canal, quais cortes).

## 5. Manutenção
- Atualizar o projeto: `git pull` dentro de `cortes-cli` (e copie a Skill de novo se ela mudou)
- yt-dlp quebrou no YouTube? `uv tool upgrade cortes --reinstall-package yt-dlp`
- Primeira transcrição com Whisper baixa o modelo (~500 MB para `small`), só uma vez.

## Uso rápido (manual, sem agente)
```powershell
cortes transcrever "https://youtu.be/XXXX" --canal humor
cortes ranquear            # pedido para o agente
cortes ranquear --validar  # depois que o cortes.json existir
cortes cortar 1,3,5
cortes limpar
```
