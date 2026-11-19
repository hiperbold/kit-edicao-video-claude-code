# Exemplo mínimo

Um Reel de 8 segundos com três cenas (texto grande em tela cheia, painel com um número, selo "link da bio") mais o cartão final. O texto é inventado só para o exemplo (organizar a agenda). Serve para conferir que a instalação funciona e como modelo para os seus vídeos.

O kit não traz nenhum arquivo de vídeo, áudio ou imagem. Você gera um vídeo de teste com o FFmpeg em poucos segundos.

Todos os comandos abaixo rodam **na raiz do kit** (a pasta que tem o `package.json`). Antes: `INSTALACAO.md` feito, até o passo 2 pelo menos (`npm install` e `npx hyperframes browser ensure`).

## 1. Gerar a mídia de teste

Uma imagem de teste colorida de 8 s em 1080x1920 a 30 qps, uma voz de mentira (um tom) e uma imagem para a capa. Nos arquivos `corte.json` e `gerar.mjs` o tempo de cada palavra já está escrito para 8 s.

```bash
mkdir -p exemplo/composicao/assets/vid exemplo/composicao/assets/img exemplo/composicao/assets/sfx
ffmpeg -y -f lavfi -i "testsrc2=size=1080x1920:rate=30:duration=8" -an -c:v libx264 -pix_fmt yuv420p -g 30 -keyint_min 30 -crf 20 exemplo/composicao/assets/vid/base.mp4
ffmpeg -y -f lavfi -i "sine=frequency=220:sample_rate=48000:duration=8" -ac 2 exemplo/composicao/assets/voz.wav
ffmpeg -y -ss 3 -i exemplo/composicao/assets/vid/base.mp4 -frames:v 1 -q:v 2 exemplo/composicao/assets/img/capa-rosto.jpg
```

No PowerShell do Windows, o mesmo, com `New-Item -ItemType Directory -Force` no lugar do `mkdir -p` (crie as três pastas `vid`, `img` e `sfx`) e os três comandos `ffmpeg` iguais.

Efeitos sonoros (sintetizados pelo kit):

```bash
ferramentas/sfx.sh exemplo/composicao/assets/sfx
```

Windows: `pwsh -File ferramentas\sfx.ps1 exemplo\composicao\assets\sfx`

## 2. Montar a composição

```bash
node exemplo/composicao/gerar.mjs
```

Escreve `exemplo/composicao/index.html` e diz "ok ... 8 efeitos". Ele lê as cores, as fontes, o logo e o texto do cartão final do `marca.json` (ou do `marca.exemplo.json`, se você ainda não criou o seu).

## 3. Conferir

```bash
cd exemplo/composicao
npx hyperframes check --json
npx hyperframes snapshot --at 1.0,3.5,6.8,9.3 --no-end
```

- O `check` tem de terminar com **zero erro**. Alguns avisos são normais neste exemplo: o vídeo de teste é uma imagem colorida (o aviso de contraste vem dela) e há dois vídeos iguais de propósito (um em tela cheia e outro na metade de baixo).
- O `snapshot` grava quadros em `.hyperframes/artifacts/snapshots/`. Abra e veja: texto grande na abertura, painel com o "3", selo de link da bio e cartão final com o logo.

## 4. Renderizar (opcional)

```bash
npx hyperframes render --quality draft --output ../trabalho/render.mp4
```

Use `--quality delivery` para a versão final. O arquivo vai para `exemplo/trabalho/` (pasta que não vai para o git, criada sozinha).

## 5. Gerar a capa

De volta à raiz do kit:

```bash
node ferramentas/capa.mjs exemplo --guia
node ferramentas/capa.mjs exemplo
```

O primeiro comando grava `exemplo/final/capa-exemplo-guia.jpg` com duas linhas vermelhas que marcam a faixa de 1350 px (y 285 a 1635): título, foto e logo têm de ficar entre elas. O segundo grava a capa limpa, `exemplo/final/capa-exemplo.jpg`.

## O que olhar nos arquivos

- `composicao/gerar.mjs`: as cenas. É o modelo para o seu vídeo (`P.faixa`, `P.painel`, `P.linkBio`; também existem `P.manchete` e `P.ilustracao`).
- `composicao/corte.json`: o tempo de cada palavra (aqui inventado). No seu vídeo, sai do `ferramentas/palavras.py` depois do corte.
- `composicao/capa.json`: título, foto e nome do arquivo da capa.
- `storyboard.md`: o roteiro de cenas que o Claude escreve e você aprova antes de renderizar.
- `composicao/hyperframes.json`: configuração do HyperFrames; copie junto ao criar um vídeo novo.

## Limpeza

Para voltar ao estado original: apague `exemplo/composicao/assets/`, `exemplo/composicao/index.html`, `exemplo/composicao/.hyperframes/`, `exemplo/trabalho/` e `exemplo/final/`.
