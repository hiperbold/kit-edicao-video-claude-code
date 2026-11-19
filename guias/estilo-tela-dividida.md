# Estilo: tela dividida explicativa

Estrutura de Reel falado em que a pessoa aparece embaixo e uma explicação visual aparece em cima. É o estilo que o `ferramentas/reels.mjs` monta pronto. As cores, a fonte e o logo vêm do seu `marca.json`.

## Para que serve

Reel falado de 45 a 90 s que ensina um passo a passo (como funciona um processo, como montar algo, o que uma ferramenta resolve). A pessoa grava falando para a câmera; a edição põe a explicação visual em cima.

## Formatos de tela (usar os 5, alternando)

| Código | Formato | Quando |
|---|---|---|
| R | Rosto cheio, título fixo no topo | gancho (primeiros 3 a 10 s) e falas de opinião |
| D | Tela dividida: ilustração em cima, rosto embaixo | cada passo do tutorial |
| I | Ilustração cheia | quando a ilustração tem muitos elementos (árvore, diagrama, tela de produto) |
| C | Cartão sobre o rosto | prompt, lista curta, comentário, print de resultado |
| J | Janela escura | mostrar uma tela de produto (um app, um painel) |

No `reels.mjs`: `cam` com modo `'cheia'` é o formato R (com `P.faixa` para o texto grande), `'div'` é o D (com `P.painel`, `P.manchete` ou `P.ilustracao` em cima). Os outros formatos (I, C, J) são camadas próprias que você escreve no `cenas(ctx)` do `gerar.mjs`.

Regra de ritmo: um formato dura de 2 a 13 s; dentro dele, algo novo aparece a cada 1 a 2 s. O rosto nunca some por mais de 13 s.

## Cores (papéis no `marca.json`)

| Papel | Cor do `marca.json` | Uso |
|---|---|---|
| Papel | `creme`, com quadriculado de 40 px em `marinho` a 5% | fundo das metades D e das telas I (quando o estilo é claro) |
| Texto | `marinho` | títulos e rótulos sobre fundo claro |
| Número do passo e destaque | `acao` | "Passo 1." e o rótulo que está sendo dito |
| Janela escura | `marinho`, com borda um tom mais claro | formato J |
| Destaque em janela escura | `acento` | palavra-chave dentro da janela |
| Marca-texto | `acento` a 20% atrás do texto | trecho a preencher num prompt |

O `reels.mjs` usa o fundo escuro (`fundo`) com o destaque em `acento`. Para um visual claro, escreva o CSS das cenas no `css` do `gerar.mjs`.

## Tipografia

- Títulos e rótulos: a fonte de título da marca, peso 700 a 800. Texto corrido em cartão: a fonte de texto da marca.
- Título do passo: 56 px, "Passo N." na cor de destaque, resto na cor de texto, no topo da metade de cima (y ≈ 160 a 220, dentro da área segura).
- Título fixo do formato R: 64 px, branco com sombra, 2 linhas, no topo (y ≈ 270).

## Legenda

- Palavra por palavra (1 a 3), a palavra que está sendo dita.
- Fonte de título pesada, 72 px, branca, caixa baixa, contorno na cor `marinho` de 6 px (o `reels.mjs` usa a fonte de texto, 64 px, com sombra; ajuste no `css` se quiser o contorno).
- Palavra-chave do trecho (nome de produto, número dito) na cor de `acento`.
- Posição: R e C a y ≈ 1300 (zona de legenda do guia de posições: y 1044 a 1285, no limite de baixo); D na emenda das metades; I a y ≈ 1400.
- Feita com a skill `embedded-captions` do HyperFrames (identidade `anchor` como base, ajustada às cores da marca) ou como camada HTML própria (é o que o `reels.mjs` faz).

## Ilustração

- Ícones planos e simples, em vetor, desenhados no HTML (nada de imagem de banco).
- Telas de produto: redesenhadas em vetor limpo ou print real com moldura de janela; nunca print com dado de cliente.
- Movimento: entrada com pulo (escala 0,8 para 1, com leve passada de 1,05), linhas que se desenham, rótulo que muda de cor quando é dito. Saída: corte seco.

## Corte e som

- Cortar pausas e erros (jump cut), com leve mudança de enquadramento (zoom de 1,0 para 1,08) a cada 2 ou 3 cortes para esconder o pulo.
- Trilha instrumental baixa o vídeo todo (cerca de -28 LUFS por baixo da voz); voz final em -14 LUFS integrado.
- Um "pop" curto quando um ícone entra; nada de efeito em toda palavra.

## Fechamento

- CTA no formato C: caixa de comentário com a palavra que a pessoa deve comentar, digitada letra a letra; ou o selo de link da bio (`P.linkBio`) seguido do cartão final com o logo.
- Sem logo cheio no meio do vídeo; se a pauta pedir, o logo pequeno no canto da última cena.
