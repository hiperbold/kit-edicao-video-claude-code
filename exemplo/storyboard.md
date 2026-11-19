# Exemplo: organizar a agenda em três tarefas (storyboard)

Texto inventado só para o exemplo. Este é o modelo de storyboard que o Claude escreve e mostra para você **antes** de renderizar.

Pauta: um Reel de 8 s que dá uma dica simples (comece por três tarefas por dia) e chama para o link da bio.
Bruto: `bruto/<arquivo>` (aqui, um vídeo de teste gerado com o FFmpeg).
Corte: sem pausas acima de 0,35 s. Duração: 8,0 s de fala mais 2,6 s de cartão final.
Tempo de cada palavra depois do corte: `composicao/corte.json`.

## Estilo

Tela dividida (`guias/estilo-tela-dividida.md`): gráfico em cima e a pessoa embaixo no plano original; tela cheia no gancho e no fechamento; legenda discreta palavra por palavra, que some quando o texto grande da cena diz a mesma coisa. Cores, fontes e logo do `marca.json`. Corte seco com zoom leve. Trilha leve por baixo da voz; efeitos discretos.

Regra de conteúdo: nenhum número que a pessoa não disse.

## Cenas

| # | Tempo (s) | Fala | Tela | Movimento e som |
|---|---|---|---|---|
| 1 | 0,0 a 2,4 | "Quer organizar a sua agenda?" | Tela cheia, a pessoa. Na faixa de baixo, "Organizar a **agenda**" grande e, depois, "sem complicar". Sem legenda (o texto grande já diz). | Zoom lento de 1,10 para 1,16; impacto quando o texto entra. |
| 2 | 2,4 a 5,9 | "Comece por três tarefas. Só três por dia." | Dividida: em cima, título "Comece pelo **essencial**" e o número "3" grande com "tarefas por dia"; embaixo, a pessoa. Legenda na emenda das metades. | Corte seco; o "3" entra com pulo quando é dito; pop. |
| 3 | 5,9 a 7,9 | "Veja no link da bio." | Tela cheia, a pessoa; selo "Link da bio: seu CTA aqui" com seta que sobe. Sem legenda (o selo já diz). | Selo salta; clique. |
| 4 | 7,9 a 10,6 | (sem fala) | Cartão final com o logo, "Seu CTA aqui" e "no link da bio" (textos do `marca.json`). | Whoosh na entrada; pop no título. |

Entrega: `final/exemplo.mp4` (1080x1920, 30 qps, -14 LUFS), `final/exemplo.srt` e a capa `final/capa-exemplo.jpg`.

## Pedidos do usuário

- (nenhum ainda). Cada ajuste pedido entra aqui, com a data, e vale para os próximos vídeos se o usuário disser.
