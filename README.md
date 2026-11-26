# Kit de edição de vídeo vertical com o Claude Code

Um kit para qualquer pessoa editar **Reels, Shorts e vídeos verticais** conversando com o Claude Code, sem precisar saber programar. Você grava o vídeo falando para a câmera, o Claude corta as pausas e os erros, monta a legenda palavra por palavra, os gráficos e o cartão final com a sua marca, e entrega o MP4 pronto (1080x1920, 30 quadros por segundo) mais a capa.

Funciona igual no **Windows e no Mac**. No Windows, aproveita a placa de vídeo NVIDIA (GTX ou RTX) quando houver (`guias/placa-de-video.md`).

Tudo roda no seu computador. Nenhuma ferramenta daqui cobra assinatura. O único gasto possível é opcional: gerar locução e imagens com IA no Magnific, com a sua própria conta, e isso só acontece se você autorizar.

## O que vem no kit

```
README.md              este arquivo
INSTALACAO.md          instalação passo a passo (Windows e Mac)
AGENTS.md / CLAUDE.md  as instruções que o Claude Code lê sozinho ao abrir esta pasta
marca.exemplo.json     modelo da sua marca (cores, fontes, logo, texto do cartão final)
package.json           trava o HyperFrames na versão 0.9.16
ferramentas/           scripts: transcrição, gerador de Reels, capa, trilha, efeitos, limpeza de voz, receitas de ffmpeg
guias/                 regras de motion, estilo "tela dividida", placa de vídeo (Windows) e Magnific
skills/video-cut/      skill de corte e junção de takes (copiar para ~/.claude/skills/)
marca/                 logo de exemplo; coloque aqui o seu logo e as suas fontes
design-systems/        design systems prontos, um por pasta (para quem tem uma ou várias marcas)
exemplo/               um vídeo mínimo de exemplo, para conferir que tudo funcionou
videos/                seus vídeos (um por pasta, criada pelo Claude)
```

## Os motores (o que faz o trabalho pesado)

| Peça | Para quê | Observação |
|---|---|---|
| [HyperFrames](https://github.com/heygen-com/hyperframes) (da HeyGen, licença Apache-2.0) | Transforma uma página HTML em vídeo: texto, gráficos, legenda e animação | Versão **0.9.16** fixada no `package.json`. Atualizar só de propósito |
| GSAP | Animações dentro do HyperFrames | Carregado da internet (CDN jsdelivr, versão 3.12.5 escrita nos arquivos gerados): o render precisa de internet |
| Chrome Headless Shell | O "navegador invisível" que o HyperFrames usa para desenhar cada quadro | Instalado por `npx hyperframes browser ensure` (cerca de 190 MB) |
| FFmpeg | Corta, junta, converte, mede o volume e cola áudio e vídeo | Instalado no sistema |
| faster-whisper (modelo large-v3) | Transcreve a fala e dá o tempo de cada palavra | Usa a placa NVIDIA se houver; senão o processador (mais lento) |
| ClearerVoice (MossFormer2) | Limpa ruído de voz | Opcional. Só se a gravação tiver chiado |
| [Magnific](https://www.magnific.com) (MCP) | Locução (vozes da ElevenLabs) e imagens com IA | Opcional e pago, com a sua conta. Veja `guias/magnific.md` |
| Node.js e Python | Rodam os scripts do kit | Node 24; Python 3.12 |

## As skills

Skill é um pacote de instruções que o Claude Code carrega quando precisa.

- **As do HyperFrames:** `npx hyperframes skills` instala o pacote do HyperFrames (por exemplo `hyperframes`, `hyperframes-cli`, `hyperframes-registry`, `media-use`, `style-sampling`, `slideshow`, `figma`). Elas ensinam o Claude a compor, animar e renderizar. Para conferir se estão em dia: `npx hyperframes skills check`.
- **A do kit:** `video-cut`, em `skills/video-cut/`. Junta partes e takes brutos e remove gaguejos, takes repetidos e pausas longas, sempre cortando em fronteira de palavra. Copie a pasta para `~/.claude/skills/` (detalhes no `INSTALACAO.md`).

## O fluxo de um vídeo

O Claude segue estes passos (estão também no `AGENTS.md`):

1. **Pauta.** O que o vídeo precisa dizer: um roteiro seu ou uma ideia. Vira o começo do `storyboard.md`.
2. **Bruto.** Você grava e solta o arquivo em `videos/_entrada/`. O Claude cria a pasta `videos/<AAAA-MM-DD>-<assunto>/` e move o bruto para `bruto/`.
3. **Transcrever.** O Whisper gera a legenda (`.srt`) e o texto, e o tempo de cada palavra.
4. **Cortar.** Pausas, erros e repetições saem, sempre em fronteira de palavra (skill `video-cut`, FFmpeg).
5. **Storyboard aprovado ANTES de renderizar.** O Claude escreve uma linha por cena (tempo, tipo de tela, texto, movimento, som) e mostra para você. Só renderiza depois do seu "pode". É aqui que se evita refazer o vídeo.
6. **Compor.** O Claude monta a composição do HyperFrames: tela dividida, tela cheia, legenda palavra por palavra, cartão final.
7. **Conferir.** `npx hyperframes check` (tem de dar zero erro) e `npx hyperframes snapshot` (quadros de verdade, que o Claude olha e você também pode olhar).
8. **Exportar.** `npx hyperframes render` e depois o volume em **-14 LUFS** (padrão das redes). Resultado: 1080x1920, 30 qps, H.264 + AAC.
9. **Revisão.** Você pede ajustes; cada pedido é anotado no `storyboard.md`.
10. **Capa.** Uma capa 1080x1920 por vídeo, com tudo dentro da faixa central que a grade do Instagram mostra.
11. **Faxina.** Com o seu "aprovado", o Claude apaga os arquivos intermediários e deixa só o vídeo final, a composição, o storyboard e o bruto.

## Como começar

1. Siga o `INSTALACAO.md` (Windows ou Mac).
2. Copie `marca.exemplo.json` para `marca.json` e troque nome, cores, fontes e texto do cartão final. Ponha o seu logo (SVG branco) e as suas fontes na pasta `marca/`. Já tem um design system? Use a pasta `design-systems/` (`design-systems/LEIA.md`).
3. Rode o `exemplo/` (o `exemplo/README.md` explica) para conferir que tudo funciona.
4. Abra o Claude Code dentro desta pasta e peça, por exemplo: "Vou gravar um Reel sobre X. Me ajude a montar o storyboard."

## Segurança e custos

- O vídeo, a voz e as imagens ficam no seu computador (o `.gitignore` impede de irem para o git).
- O Magnific se conecta com a sua conta (login no navegador, sem chave). Se usar chave de API, ela fica só num arquivo `.env` fora desta pasta. Nunca dentro do projeto.
- Qualquer gasto com serviço externo só acontece depois do seu "pode", com o valor dito antes.

## Créditos e licenças

Kit criado pela Hiperbold a partir do fluxo de edição de vídeo da agência. Licença MIT (arquivo `LICENSE`).

- HyperFrames: HeyGen, Apache-2.0.
- `guias/motion-regras.md` é adaptado de [bangtutorial/bang-motion](https://github.com/bangtutorial/bang-motion) (MIT, Copyright (c) 2026 Bang Tutorial).
- `ferramentas/ffmpeg-receitas.md` usa trechos adaptados de [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) (MIT, Copyright (c) 2026 kajisho5).
- As fontes Assistant e Inter, usadas no exemplo, são gratuitas (Google Fonts) e não vêm no kit.
