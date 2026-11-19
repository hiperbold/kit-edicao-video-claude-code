# Instalação

Passo a passo para **Windows 11** e **Mac**. Faça uma vez. Se algum passo falhar, copie a mensagem de erro para o Claude Code e peça ajuda: ele resolve a maioria.

Tempo estimado: 30 a 60 minutos, a maior parte esperando downloads.

## 1. Programas

### Windows

Abra o PowerShell (o `winget` já vem no Windows 11) e rode:

```powershell
winget install Git.Git
winget install Gyan.FFmpeg
winget install Python.Python.3.12
winget install Microsoft.PowerShell
```

- **Node.js 24:** baixe o instalador em nodejs.org (versão 24.x).
- **Placa NVIDIA (opcional):** instale o driver mais recente. Com ela, a transcrição e a limpeza de voz ficam muito mais rápidas. Sem ela, tudo funciona no processador, só mais devagar.
- Feche e abra o PowerShell e confira: `git --version`, `node --version`, `ffmpeg -version`, `python --version`.

### Mac

Com o [Homebrew](https://brew.sh) instalado, no Terminal:

```bash
brew install git ffmpeg python@3.12
```

- **Node.js 24:** baixe o instalador em nodejs.org (versão 24.x).
- Confira: `git --version`, `node --version`, `ffmpeg -version`, `python3.12 --version`.
- No Mac a transcrição roda no processador (o faster-whisper não usa a placa de vídeo do Mac). Para vídeos longos, um modelo menor (`--modelo medium`) é mais rápido, com menos precisão.

### Claude Code

Instale e entre na sua conta seguindo as instruções oficiais em docs.claude.com (Claude Code).

## 2. Baixar o kit e instalar o HyperFrames

Baixe o kit (botão verde "Code" > "Download ZIP" no GitHub, ou `git clone`) para uma pasta sua, por exemplo `Documentos/edicao-video`. Todos os comandos abaixo rodam **dentro dessa pasta**.

```bash
npm install
npx hyperframes --version
npx hyperframes browser ensure
```

- `npm install` instala o HyperFrames **0.9.16** (a versão fixada no `package.json`) na pasta `node_modules` do kit.
- `npx hyperframes --version` tem de mostrar `0.9.16`.
- `browser ensure` baixa o Chrome que o HyperFrames usa para desenhar os quadros (cerca de 190 MB, numa pasta de cache do seu usuário). O render precisa dele.

## 3. Skills do Claude Code

As skills ficam na pasta `.claude/skills` do seu usuário: `%USERPROFILE%\.claude\skills` no Windows, `~/.claude/skills` no Mac.

```bash
npx hyperframes skills
```

Isso instala as skills do HyperFrames (a CLI avisa onde instalou). Para conferir ou atualizar depois: `npx hyperframes skills check` e `npx hyperframes skills update`.

Depois copie a skill do kit:

```powershell
# Windows (PowerShell)
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force skills\video-cut "$HOME\.claude\skills\"
```

```bash
# Mac
mkdir -p ~/.claude/skills && cp -R skills/video-cut ~/.claude/skills/
```

**Reinicie o Claude Code** depois de copiar, para ele enxergar as skills novas.

## 4. Transcrição (Whisper local)

Crie um ambiente Python só para o kit, na raiz da pasta (ele se chama `.venv` e não vai para o git):

```powershell
# Windows
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install faster-whisper numpy
```

```bash
# Mac
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install faster-whisper numpy
```

**Só no Windows com placa NVIDIA**, acrescente as bibliotecas de GPU:

```powershell
.venv\Scripts\python.exe -m pip install nvidia-cublas-cu12 nvidia-cudnn-cu12
```

Na primeira transcrição, o modelo `large-v3` baixa sozinho (alguns GB). Depois fica guardado no computador.

Conferir (grave um áudio curto qualquer, ou use um vídeo seu):

```powershell
pwsh -File ferramentas\transcrever.ps1 meu-audio.wav pt
```

```bash
ferramentas/transcrever.sh meu-audio.wav pt
```

Saem, ao lado do arquivo, `meu-audio.srt` e `meu-audio - transcricao.txt`. A saída mostra "em cuda" (placa) ou "em cpu" (processador).

Os scripts procuram o Python do kit em `.venv`. Para usar outro, defina a variável de ambiente `KIT_PYTHON` com o caminho dele.

**Nomes e siglas:** o Whisper erra nomes de marca, produtos e siglas. Copie `nomes.exemplo.txt` para `nomes.txt` e liste os seus. As correções entram sozinhas na transcrição e no tempo das palavras.

## 5. Fontes e marca

```bash
cp marca.exemplo.json marca.json      # Windows: copy marca.exemplo.json marca.json
```

Edite o `marca.json` (nome, cores, fontes, logo, texto do cartão final). Ponha o logo (SVG branco, para fundo escuro) e as fontes na pasta `marca/`. O exemplo usa Assistant e Inter, gratuitas em fonts.google.com: baixe e coloque os arquivos em `marca/fontes/` com os nomes que estão no `marca.json`. Sem os arquivos de fonte, o vídeo sai com Arial e o gerador avisa no terminal.

## 6. Limpeza de voz (opcional)

Só se a sua gravação tiver chiado ou ruído de fundo. Ambiente separado, dentro de `ferramentas/voz/`:

```powershell
# Windows
python -m venv ferramentas\voz\.venv
ferramentas\voz\.venv\Scripts\python.exe -m pip install -r ferramentas\voz\requirements.txt
```

```bash
# Mac
python3.12 -m venv ferramentas/voz/.venv
ferramentas/voz/.venv/bin/python -m pip install -r ferramentas/voz/requirements.txt
```

Com placa NVIDIA no Windows, troque o torch pelo da mesma versão com CUDA: abra pytorch.org, escolha a versão 2.15.0 e o CUDA mais novo da lista, copie o endereço do `--index-url` que a página mostrar e rode:

```powershell
ferramentas\voz\.venv\Scripts\python.exe -m pip install --force-reinstall torch==2.15.0 --index-url <endereço do pytorch.org>
ferramentas\voz\.venv\Scripts\python.exe -c "import torch; print(torch.cuda.is_available())"
```

Tem de imprimir `True`. Uso:

```powershell
ferramentas\voz\.venv\Scripts\python.exe ferramentas\voz\clearvoice_limpar.py entrada.wav saida.wav
```

Na primeira vez o modelo (cerca de 211 MB) baixa sozinho para `~/.cache/clearvoice`.

## 7. Conferir que ficou pronto

Siga o `exemplo/README.md`: ele gera um vídeo de teste com o FFmpeg, monta a composição, roda o `check` e gera a capa. Se o `check` terminar com zero erro, o ambiente está pronto.

## 8. Chaves de API (só se for usar)

Só para serviços de vídeo com IA, se um dia você quiser. Guarde as chaves num arquivo `.env` **fora** desta pasta (por exemplo, na pasta `.claude` do seu usuário). Nunca dentro do projeto, porque a pasta pode ir para o git. O Claude só gera algo pago depois de você dizer "pode".

## Problemas comuns

- **`npx` ou `node` não encontrado:** feche e abra o terminal depois de instalar o Node.
- **`pwsh` não encontrado (Windows):** feche e abra o terminal depois do `winget install Microsoft.PowerShell`.
- **Falta de Chrome no render ou na capa:** rode `npx hyperframes browser ensure` de novo.
- **Transcrição lenta:** conferir se aparece "em cuda". Sem placa NVIDIA, é normal ser lenta; use `--modelo medium` ou `--modelo small`.
- **Erro com a placa NVIDIA (Windows):** atualize o driver e confira o `pip install nvidia-cublas-cu12 nvidia-cudnn-cu12` do passo 4. Para seguir sem placa: `--device cpu`.
