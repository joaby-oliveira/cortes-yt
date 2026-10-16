# cortes-cli

CLI para garimpar, ranquear (via Claude Code/Codex) e cortar Shorts de podcasts.

## Instalação no Windows

Abra o **PowerShell** (não precisa ser como administrador) e siga na ordem.

## 1. Programas base
```powershell
winget install Python.Python.3.12
winget install Gyan.FFmpeg
winget install DenoLand.Deno
winget install astral-sh.uv
```
Feche e abra o PowerShell de novo para o PATH atualizar. Confira:
```powershell
python --version; ffmpeg -version; deno --version; uv --version
```

## 2. Projeto
Descompacte o `cortes-cli.zip` em, por exemplo, `C:\Users\<você>\Projetos\cortes-cli`. Depois:
```powershell
cd $HOME\Projetos\cortes-cli
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
No Claude Code, use `/cortes <link> humor` ou só cole o link e diga o canal.

## 5. Manutenção
- yt-dlp quebrou no YouTube? `uv tool upgrade cortes --reinstall-package yt-dlp`
- Primeira transcrição com Whisper baixa o modelo (~500 MB para `small`), só uma vez.

## Uso rápido (manual, sem agente)
```powershell
cortes transcrever "https://youtu.be/XXXX" --canal humor --fonte flow
cortes ranquear            # pedido para o agente
cortes ranquear --validar  # depois que o cortes.json existir
cortes cortar 1,3,5
cortes limpar
```
