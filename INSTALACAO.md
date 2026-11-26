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
- **Placa NVIDIA (opcional):** instale o driver mais recente (nvidia.com/drivers) e reinicie. Com ela, a transcrição e a limpeza de voz ficam muito mais rápidas. Sem ela, tudo funciona no processador, só mais devagar. Cada família (GTX 10xx, GTX 16xx, RTX 20xx a 40xx, RTX 50xx) tem um ajuste próprio: veja `guias/placa-de-video.md`. Placa AMD ou Intel: o kit usa o processador.
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

**Só no Windows com placa NVIDIA**, acrescente as bibliotecas de GPU e rode o diagnóstico:

```powershell
.venv\Scripts\python.exe -m pip install nvidia-cublas-cu12 nvidia-cudnn-cu12
.venv\Scripts\python.exe ferramentas\placa.py
```

O `placa.py` mostra a placa, a memória de vídeo, a família e o modelo e a precisão que o kit vai usar. Tem de aparecer "faster-whisper enxerga a placa: sim". Com menos de 4 GB de memória de vídeo, use `-Modelo medium` ou `-Modelo small` no `transcrever.ps1`. Tabela completa em `guias/placa-de-video.md`.

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

Edite o `marca.json` (nome, cores, fontes, logo, texto do cartão final). Se você já tem um design system pronto (ou várias marcas), use a pasta `design-systems/` em vez disso: o `marca.json` da raiz fica só com `{"designSystem": "<nome>"}` (e o que quiser trocar por cima), porque tudo o que estiver nele vale sobre o design system. `design-systems/LEIA.md` explica. Ponha o logo (SVG branco, para fundo escuro) e as fontes na pasta `marca/`. O exemplo usa Assistant e Inter, gratuitas em fonts.google.com: baixe e coloque os arquivos em `marca/fontes/` com os nomes que estão no `marca.json`. Sem os arquivos de fonte, o vídeo sai com Arial e o gerador avisa no terminal.

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

Com placa NVIDIA no Windows, troque o torch pelo da mesma versão com CUDA. Abra pytorch.org, escolha a versão 2.15.0 e o CUDA certo para a sua placa:

- **RTX 20xx a 40xx e GTX 16xx:** o CUDA mais novo da lista.
- **RTX 50xx:** CUDA 12.8 ou mais novo.
- **GTX 10xx:** o CUDA mais novo; se o teste abaixo der aviso "sm_61 is not compatible", troque por uma opção de CUDA mais antiga (12.6 ou anterior) ou use a limpeza de voz no processador.

Copie o endereço do `--index-url` que a página mostrar e rode:

```powershell
ferramentas\voz\.venv\Scripts\python.exe -m pip install --force-reinstall torch==2.15.0 --index-url <endereço do pytorch.org>
ferramentas\voz\.venv\Scripts\python.exe -c "import torch; print(torch.cuda.is_available())"
```

Tem de imprimir `True`. Se imprimir `False` ou um aviso como "sm_XX is not compatible", o CUDA escolhido não serve para a sua placa: veja `guias/placa-de-video.md`. Uso:

```powershell
ferramentas\voz\.venv\Scripts\python.exe ferramentas\voz\clearvoice_limpar.py entrada.wav saida.wav
```

Na primeira vez o modelo (cerca de 211 MB) baixa sozinho para `~/.cache/clearvoice`.

## 7. Conferir que ficou pronto

Siga o `exemplo/README.md`: ele gera um vídeo de teste com o FFmpeg, monta a composição, roda o `check` e gera a capa. Se o `check` terminar com zero erro, o ambiente está pronto.

## 8. Magnific: locução e imagens com IA (opcional)

Para gerar locução ou imagens. É pago, com os créditos da **sua** conta do Magnific; o kit não traz conta nem chave. Conecte uma vez, no terminal:

```bash
claude mcp add --transport http magnific https://mcp.magnific.com
```

Na primeira geração, o navegador abre para você entrar na sua conta. Não há chave para copiar. Quem prefere a API com chave própria: guarde `MAGNIFIC_API_KEY` num arquivo `.env` **fora** desta pasta (por exemplo, na pasta `.claude` do seu usuário), nunca dentro do projeto. Tudo em `guias/magnific.md`. O Claude só gera algo pago depois de dizer o custo e você responder "pode".

Outros serviços com chave (vídeo com IA, avatar): a mesma regra, chave só no `.env` fora da pasta.

## Problemas comuns

- **`npx` ou `node` não encontrado:** feche e abra o terminal depois de instalar o Node.
- **`pwsh` não encontrado (Windows):** feche e abra o terminal depois do `winget install Microsoft.PowerShell`.
- **Falta de Chrome no render ou na capa:** rode `npx hyperframes browser ensure` de novo.
- **Transcrição lenta:** conferir se aparece "em cuda". Sem placa NVIDIA, é normal ser lenta; use `--modelo medium` ou `--modelo small`.
- **Erro com a placa NVIDIA (Windows):** atualize o driver, confira o `pip install nvidia-cublas-cu12 nvidia-cudnn-cu12` do passo 4 e rode o `placa.py`. Para seguir sem placa: `-Device cpu` no `transcrever.ps1`.
- **Transcrição com texto repetido ou vazio numa GTX:** `$env:KIT_WHISPER_TIPO="int8"` e transcreva de novo (`guias/placa-de-video.md`).
- **`bash: \r: command not found` no Mac:** o arquivo `.sh` foi salvo com fim de linha do Windows. Baixe o kit de novo pelo `git clone` (o `.gitattributes` corrige) em vez de copiar a pasta do Windows.
