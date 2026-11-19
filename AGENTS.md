# Kit de edição de vídeo vertical

Esta pasta é um kit para editar vídeos verticais (Reels, Shorts, vídeos de LinkedIn) com o Claude Code e o HyperFrames. Quem usa pode não ser programador: fale como editor de vídeo (cortes, ritmo, cena, legenda), explique em frases simples e não peça decisões técnicas; escolha a opção que você recomenda e diga em uma linha o que escolheu e por quê. Pergunte só o que é do usuário: texto do vídeo, aparência, gasto, publicação.

Leia também `README.md` (visão geral) e `INSTALACAO.md` (ambiente). Este arquivo é a fonte das regras.

## O que você faz e o que não faz

- Faz: transcreve, corta, monta a composição, renderiza, mede o volume, gera a capa, organiza as pastas.
- Não publica nada em rede social.
- Não instala nada global sem necessidade. Se faltar um programa, diga qual e como instalar (`INSTALACAO.md`).
- Não mexe em arquivos fora desta pasta, a não ser em temporários (abaixo).

## Estrutura de pastas

```
marca.json                  a marca do usuário (cores, fontes, logo, cartão final); modelo em marca.exemplo.json
nomes.txt                   nomes e siglas que o Whisper erra (opcional; modelo em nomes.exemplo.txt)
marca/                      logo e fontes da marca
ferramentas/                scripts do kit (não editar para um vídeo só)
guias/                      motion-regras.md e estilo-tela-dividida.md
skills/video-cut/           skill de corte (a cópia ativa fica em ~/.claude/skills/)
exemplo/                    vídeo mínimo de exemplo (modelo para criar outros)
videos/
  _entrada/                 caixa de entrada: o usuário solta aqui o vídeo bruto
  <AAAA-MM-DD>-<assunto>/
    bruto/                  gravação original (fora do git)
    trabalho/               intermediários: cortes, áudios, renders de teste, quadros (fora do git)
    final/                  vídeo exportado, .srt e capa (fora do git)
    composicao/             projeto HyperFrames: gerar.mjs, corte.json, capa.json, hyperframes.json, assets/
    storyboard.md           cenas, tempos, texto, movimento, som e pedidos do usuário
```

Nome de pasta de vídeo: data em que começou + assunto em minúsculas com hífen, sem acentos.

**Regra fixa: nenhum caminho absoluto** em arquivo do projeto (nada que comece pela letra do disco no Windows ou pela pasta do usuário no Mac). Escreva caminhos a partir da pasta do projeto (`videos/<pasta>/final/`). O que fica fora da pasta (temporários, chaves, caches) se cita pelo nome.

## Fluxo de um vídeo

1. **Pauta.** O roteiro ou a ideia vem do usuário. Anote em `storyboard.md` o que tem de ser dito.
2. **Bruto.** O usuário solta o arquivo em `videos/_entrada/`. Ao abrir o vídeo, crie `videos/<pasta>/` e mova o bruto para `bruto/`. Confira com `ffprobe` (receita 1 de `ferramentas/ffmpeg-receitas.md`): tamanho, taxa de quadros, HDR, rotação.
3. **Transcrever.** Windows: `pwsh -File ferramentas\transcrever.ps1 "videos/<pasta>/bruto/<arquivo>"`. Mac: `ferramentas/transcrever.sh "videos/<pasta>/bruto/<arquivo>"`. Saem `<nome>.srt` e `<nome> - transcricao.txt` ao lado do arquivo. Copie para `trabalho/`. **Releia a transcrição inteira**: o Whisper erra siglas, nomes de marca e de produto (acrescente-os ao `nomes.txt` e transcreva de novo se forem muitos).
4. **Cortar.** Pausas, erros e repetições saem, sempre em fronteira de palavra (skill `video-cut`; `ferramentas/palavras.py` dá o tempo de cada palavra; receitas em `ferramentas/ffmpeg-receitas.md`). Sempre recodificar, nunca `-c copy` para cortar. Resultado em `trabalho/`. Depois do corte, gere de novo o tempo das palavras do vídeo cortado e grave `composicao/corte.json` no formato `{"dur": <segundos>, "palavras": [{"w","s","e"}]}` (veja `exemplo/composicao/corte.json`).
5. **Estilo.** Escolha o estilo (`guias/estilo-tela-dividida.md` é o que o `ferramentas/reels.mjs` monta pronto). Por cima valem as regras de `guias/motion-regras.md` (tamanho de plano, transições, ritmo, texto, fundo, som), com a lista de conferência no fim.
6. **Storyboard, ANTES de renderizar.** Escreva `storyboard.md` (uma linha por cena: tempo, formato de tela, texto, movimento, som; veja `exemplo/storyboard.md`) e mostre ao usuário. **Não renderize antes do "pode" dele.** Pode mostrar a prévia (`npx hyperframes preview`, dentro de `composicao/`).
7. **Compor.** Crie `composicao/` copiando de `exemplo/composicao/` o `hyperframes.json` e o `gerar.mjs` (ajuste as cenas; no `gerar.mjs` copiado, troque o import para `../../../ferramentas/reels.mjs`, porque a pasta do vídeo fica um nível mais fundo que a do exemplo). Coloque o vídeo cortado em `composicao/assets/vid/base.mp4` e a voz em `composicao/assets/voz.wav`; gere os efeitos com `pwsh -File ferramentas\sfx.ps1 videos/<pasta>/composicao/assets/sfx` (Mac: `ferramentas/sfx.sh <pasta>`). Rode `node videos/<pasta>/composicao/gerar.mjs`, que escreve o `index.html`. Para algo que o `reels.mjs` não cobre, use as skills do HyperFrames (`hyperframes`, `motion-graphics`, `graphic-overlays`, `embedded-captions`).
8. **Conferir.** Dentro de `composicao/`: `npx hyperframes check --json` (zero erro; avisos, leia e decida) e `npx hyperframes snapshot --at <tempos>`. **Olhe os quadros** de verdade (abra as imagens), não confie só no `check`.
9. **Exportar.** Sempre 1080x1920, 30 qps, H.264 + AAC, áudio em -14 LUFS. Dentro de `composicao/`: `npx hyperframes render --quality delivery --output ../trabalho/render.mp4`. Depois, de dentro da pasta do vídeo: `ffmpeg -i trabalho/render.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:v copy -c:a aac -b:a 192k final/<nome>.mp4` (para melhor precisão, loudnorm em duas passadas: receita 8 do `ffmpeg-receitas.md`). Grave também o `.srt` revisado em `final/`.
10. **Revisão.** O usuário pede ajustes; cada pedido entra em `storyboard.md` (seção "Pedidos do usuário") e, se valer para os próximos vídeos, em `guias/`.
11. **Capa.** Todo Reel tem a sua (regra abaixo).
12. **Aprovação e faxina.** Com o "aprovado" do usuário, aplique a faxina (abaixo) e, se o usuário usa git, faça o commit.

## Legenda: revisar palavra por palavra

O Whisper erra siglas, nomes próprios e termos técnicos, e junta ou separa palavras de um jeito estranho. A legenda do vídeo sai dessas palavras. Antes de renderizar, **leia a legenda palavra por palavra** contra o que a pessoa disse e corrija no `corte.json` (campo `w`). Um erro de grafia numa marca ou numa sigla é o defeito mais comum e o mais visível.

## Regras de conteúdo

- Português do Brasil, frases curtas, sem emoji em excesso.
- **Nunca inventar número, caso, resultado ou depoimento.** Todo número na tela tem de ter sido dito ou ter fonte; com fonte, ela aparece na tela ("Fonte: ...").
- Nada de nome de cliente ou empresa real em vídeo, a não ser que o usuário peça.
- Nunca dado real de cliente em tela de produto.

## Área segura do Instagram (1080x1920)

- Não pôr nada em: topo y 0 a 137; rodapé y 1501 a 1920; coluna direita x 943 a 1080.
- Área de conteúdo: x 137 a 942, y 264 a 1495. Faixas: rosto e título y 264 a 1044; legenda y 1044 a 1285; apoio e CTA y 1285 a 1495.

## Capa

Todo Reel tem a sua capa. Arquivo 1080x1920, mas texto, logo e foto ficam **todos dentro da faixa central de 1350 px (y 285 a 1635)**, que é o que a grade do Instagram mostra; acima e abaixo dela só fundo.

- Gerador: `node ferramentas/capa.mjs videos/<pasta>` lê `composicao/capa.json` e grava em `final/` (nome em `saida`). `--guia` desenha as linhas da faixa e grava um arquivo `-guia.jpg` para conferir. **Abra e olhe a imagem.**
- Rosto: um quadro do próprio vídeo (`ffmpeg -ss <tempo> -i <video> -frames:v 1 -q:v 2 composicao/assets/img/capa-rosto.jpg`), em janela com cantos arredondados (nunca recortado flutuando).
- O gerador usa o Chrome do HyperFrames; se faltar, `npx hyperframes browser ensure`.

## Marca

Cores, fontes, logo e texto do cartão final vêm do `marca.json` da raiz (se não existir, do `marca.exemplo.json`, e avise o usuário de que ainda está usando o modelo). O `reels.mjs` e o `capa.mjs` copiam logo e fontes para `composicao/assets/marca/` sozinhos. Fonte que não existe vira aviso no terminal e o vídeo sai com Arial: avise o usuário.

## Som

- Trilha de fundo leve e original: `ferramentas/trilha_leve.py` (sintetizada, sem direito autoral de terceiros), por baixo da voz com `sidechaincompress` (receita 6 do `ffmpeg-receitas.md`), cerca de 20 dB abaixo da voz, **sempre audível**. Trilha de batidas sincronizada com os cortes: `ferramentas/batidas.py`.
- Efeitos: `ferramentas/sfx.ps1` ou `sfx.sh` (sintetizados). Para publicação, prefira biblioteca com licença.
- Voz com ruído: `ferramentas/voz/clearvoice_limpar.py` (precisa do ambiente do passo 6 do `INSTALACAO.md`). Depois, EQ suave sem reforço de agudo, de-esser e loudnorm em duas passadas.
- Vídeo de celular em HDR: converter para SDR antes de tudo (receita 3 do `ffmpeg-receitas.md`) e conferir um quadro.

## Gasto e chaves

- Qualquer serviço pago (geração de vídeo ou avatar com IA, voz, banco de imagens): **diga antes quantas gerações e o custo estimado e espere o "pode"** do usuário. Nada é contratado ou gasto sem isso.
- **Chaves de API ficam só num arquivo `.env` fora da pasta do projeto** (por exemplo, na pasta `.claude` do usuário). Nunca no repositório, no `storyboard.md`, no `marca.json` nem no chat. O `.gitignore` já ignora `.env`, mas não conte só com ele.
- Material gerado por IA entra em `videos/<pasta>/bruto/gerado/<nn>-<tipo>.mp4`, com um `<nn>-<tipo>.md` ao lado (serviço, modelo, instrução usada, duração, custo cobrado).

## Faxina depois da aprovação

Depois que o usuário aprova um vídeo, apague o que sobrou:

- `videos/<pasta>/trabalho/` inteiro;
- dentro de `composicao/`: `.hyperframes/` (relatórios, snapshots), `renders/`, `assets/marca/` (é regerado), `node_modules/` se houver, e qualquer cache.

Ficam: o vídeo e a capa em `final/`, o código da composição (`gerar.mjs`, `corte.json`, `capa.json`, `index.html`, `assets/` com a mídia usada), o `storyboard.md` e o `bruto/` (nunca se apaga o bruto: serve para reeditar). O `node_modules/` e o `.venv/` da raiz são as ferramentas: não se apagam. O Chrome do HyperFrames fica no cache do usuário e também não se apaga.

## Temporários

Script descartável, JSON de teste, render de rascunho e qualquer coisa que não seja entregável vai numa **pasta temporária fora do projeto** (combine com o usuário qual), nunca dentro da pasta do projeto, para não ir para o git por engano.

## Ferramentas (versões usadas no desenvolvimento do kit)

| Ferramenta | Versão | Observação |
|---|---|---|
| HyperFrames CLI | 0.9.16 | fixado no `package.json`; atualizar só de propósito, e avisar o usuário |
| Node | 24.x | |
| Python | 3.12 | ambientes `.venv/` (Whisper, numpy) e `ferramentas/voz/.venv/` (limpeza de voz) |
| FFmpeg / FFprobe | 8.1 (Windows, build completo da Gyan) | no Mac, o do Homebrew pode vir sem o filtro `drawtext`: texto na tela vai sempre pela composição do HyperFrames |
| faster-whisper | `large-v3` | placa NVIDIA se houver, senão processador |
| GSAP | 3.12.5, da CDN jsdelivr | o render precisa de internet |

Decisões do kit:
- Texto na tela só pelo HyperFrames, nunca pelo `drawtext` do ffmpeg, para o resultado sair igual em qualquer computador.
- Sem TTS nem música gerada por modelo de IA no kit; trilha e efeitos são sintetizados pelos scripts.
- Skills `hyperframes-*`, `motion-graphics`, `graphic-overlays`, `embedded-captions` e `media-use` são do ecossistema do HyperFrames (`npx hyperframes skills`); a `video-cut` é deste kit.
