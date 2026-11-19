# Regras de motion (base de todos os estilos)

Regras gerais de motion graphics que valem para qualquer vídeo vertical do kit, por cima do estilo escolhido.

- Fonte: skill [bangtutorial/bang-motion](https://github.com/bangtutorial/bang-motion) v1.19.0 (licença MIT, Copyright (c) 2026 Bang Tutorial), traduzida do indonésio e adaptada. A skill não foi instalada: ela tem render próprio (não é HyperFrames), é 16:9 por padrão, não cobre pessoa falando e proíbe legenda.
- O que mudou na adaptação: vertical 1080x1920 é o padrão; legenda é obrigatória em Reels (pessoa assiste sem som); tudo vira HTML + GSAP dentro do contrato do HyperFrames; as cores e fontes são as da sua marca (`marca.json`); acrescentada a parte de talking-head e a de som, que a skill não tem.
- Onde houver conflito, vale nesta ordem: pedido do dono do vídeo, estilo aprovado do vídeo, este arquivo.

## 1. O princípio: é vídeo, não slide

O erro mais comum é montar cada cena como slide: título + subtítulo + texto + selos, trocados por fade. Isso lê como apresentação e é rejeitado.

- **Uma cena, uma afirmação.** Frase de até 5 palavras vence frase completa. Ideia que precisa de mais de 6 palavras vira duas cenas, ou vira visual (ícone, número, tela).
- **No máximo dois níveis de texto por cena**: uma frase ou número grande + um rótulo. Cabeçalho ("01 — RECURSO") + título + texto = três níveis = slide.
- **Ordem de atenção**: a frase primeiro, o objeto principal depois, o detalhe por último. Nunca o selo antes da frase.
- **Informação nova = resposta visual nova.** Se a fala muda de assunto, algo muda na tela (enquadramento, objeto, fundo).
- **Metadado não é conteúdo**: URL longa, versão, nota de rodapé saem.
- **Fio condutor**: algo atravessa o vídeo inteiro (a pessoa, um objeto, o mundo por onde a câmera anda) por mais de 60% do tempo. Imagens cheias trocando sem nada em comum = slideshow.

**Teste rápido** num quadro parado:
- Este quadro viraria um slide de empresa sem mudar nada? Então refazer.
- O olho sabe para onde olhar em 0,2 s? Se não, tirar elementos.
- Escondendo todo o texto, o fundo continua interessante mas calmo? Os dois têm de ser sim.
- Em cada transição, algo se mexe por causa da câmera, e não só porque o elemento se anima sozinho?

## 2. Câmera: tamanho de plano, não "respiração"

"Zoom in e out" em motion é **troca de tamanho de plano**: a câmera chega perto do elemento que está contando a história e depois volta. A respiração de poucos por cento quase não aparece: é só a camada de base.

- **Planos**: aberto (a composição inteira), médio (o elemento principal ocupa de um terço a metade do quadro), fechado (um elemento ou detalhe ocupa a maior parte).
- **Alvo**: o centro do elemento que está falando agora (texto que acabou de entrar, objeto que chegou, botão clicado, detalhe citado na frase). A câmera recebe o elemento, não corre atrás dele.
- **Ritmo**: o plano troca na batida do conteúdo. Padrão comum: perto do elemento A, volta ao aberto quando a composição precisa do quadro todo, perto do elemento B. **Dois planos do mesmo tamanho seguidos ficam chatos.**
- **Dois tempos de movimento**: a troca de plano (curta, `power2.inOut`, 0,6 a 0,9 s) e o avanço lento enquanto segura (`sine.inOut`), para o plano parado não morrer.
- No corte a câmera pode já nascer fechada, sem animação, e então abrir. O vídeo pode começar fechado.
- Fechamento parado (logo, CTA) ganha avanço lento; nunca congela.
- Não ir e voltar mais rápido que a leitura (menos de ~1,5 s): dá enjoo. **O texto entra depois que a câmera chega**, nunca no meio do movimento.
- **Respiração de base**: zoom lento contínuo de ±4 a 5% por cena, `sine.inOut`, alternando o sentido, encadeado sem saltos. A câmera nunca para e nunca dá tranco.
- **Camadas**: o que é parte do mundo entra no "rig" da câmera e escala junto. Legenda, rótulos e interface de tela ficam numa camada fora do rig, para não crescer nem ser cortada. Tremor de impacto vai num invólucro separado.
- O mundo é maior que o quadro (sobra nas bordas), para a câmera nunca revelar a borda.

No HyperFrames: a câmera é um invólucro (`div`) em volta da cena com `scale` e `x/y` animados no GSAP; nunca CSS `transform` no mesmo elemento que o GSAP anima (contrato, item 6). Ver a receita na seção 9.

### Em talking-head (depoimento, Reel falado)

- O vídeo da pessoa é o "mundo": o punch-in é troca de plano. Plano aberto (corpo e contexto), médio (peito para cima) e fechado (rosto) alternando nas frases-chave; nunca dois iguais seguidos.
- Corte de pausa (jump cut) sempre com mudança de plano, para esconder o pulo. Na frase de impacto, fechar no rosto.
- Entre os cortes, avanço lento de 1,00 a 1,04 no plano, para a imagem não ficar parada.
- O zoom vai no invólucro do `<video>`, nunca no `<video>` direto (contrato, item 8).
- Escala de até 1,35 no vídeo em 1080p ainda fica nítida; acima disso, usar a fonte 4K.

## 3. Transições

Duas transições que parecem baratas: o whip que arrasta o mundo e revela a borda preta ("virou a página") e o giro ou zoom de susto com desfoque em todo corte ("efeito pronto de editor"). A ordem certa, do mais simples ao mais forte:

1. **Câmera respirando** (base, sempre ligada).
2. **Coreografia sobreposta**: os elementos da cena velha saem (rápido, `power2.in`, com desfoque no sentido do movimento) **enquanto** os da cena nova entram. É a sobreposição no tempo que dá vida, não o efeito de câmera.
3. **Objeto que cobre a lente**: um elemento da marca passa bem perto da câmera, cobre o quadro no ponto de corte e a cena troca por trás dele. Trajeto diagonal ~1 s `power1.inOut`, escala máxima no corte, sentido alternado a cada uso.
4. **Zoom motivado**: mergulhar pela tela de um celular, entrar no furo do logo. No máximo uma vez por vídeo, e só com motivo.

**Cardápio** (num vídeo: pelo menos dois tipos, pelo menos um com profundidade 3D, no máximo dois wipes):

| # | Transição | Como | Sensação |
|---|---|---|---|
| 1 | Mergulho 3D (push-through) | câmera acelera para dentro do texto que sai (`power2.in`), corte, a cena nova nasce grande e assenta (`power3.out`); camadas em profundidades diferentes (`perspective` 1400 px) | entrar no mundo |
| 2 | Cartão girando de dentro | o próximo objeto vem do fundo girando (`rotateY` -35° para 0), o velho sai ao contrário | premium, tátil |
| 3 | Objeto com espessura passando pela lente | logo, cartão de vidro, bloco 3D (nunca retângulo chapado) cresce de 1 a 2,5x com desfoque, cobre o quadro um instante | cinema |
| 4 | Vazamento de luz | bola de luz suave entra pela borda e cobre 40 a 60% do quadro no corte (nunca 100%); cor do acento da marca | suave |
| 5 | Máscara com a forma da marca | a cena nova aparece por um furo com a forma do logo ou de uma letra que cresce (`clip-path` ou `mask`) | marca forte |
| 6 | Whip com desfoque | o mundo desliza 120 a 200 px com desfoque de 18 px em 0,3 s, sentido alternado, sem revelar borda | energia |
| 7 | Foco de profundidade | a cena velha desfoca e encolhe para trás, a nova chega nítida da frente | narrativa |
| 8 | Sobreposição sem corte | elementos velhos saem enquanto os novos já entram; câmera respira | fluxo |
| 9 | Troca de fundo por trás de 1 a 5 | a troca escuro ↔ claro ou de cor acontece enquanto o quadro está coberto | segmento novo |

- **Proibido como padrão**: faixa de cor chapada gigante varrendo o quadro, linha fina varrendo, e o mesmo tipo de transição em todos os cortes.
- Vazamento de luz é para um momento especial, não para todo corte.
- Transição não é obrigatória em todo corte: corte seco no tempo certo também é escolha. Escolher onde a transição faz sentido (troca de assunto, virada da história).
- Antes de montar uma à mão, procurar no registro do HyperFrames (`npx hyperframes catalog --json`, skill `hyperframes-registry`).

## 4. Ritmo de entrada e saída

- **Assimétrico**: entrada mais lenta e firme (0,7 a 1,3 s, `power4.out`), saída rápida (0,35 a 0,55 s, `power2.in`). Entrada e saída iguais parecem mecânicas.
- **Desfoque no sentido do movimento** em todo texto que entra ou sai: `feGaussianBlur` do SVG com `stdDeviation="x y"` separados (horizontal: `v v*0.08`), de 30 para 0 na entrada e de 0 para 50 na saída. `filter: blur()` do CSS desfoca para todos os lados e parece fora de foco. Abrir a caixa do filtro (`x/y` -70%, `width/height` 240%) senão o rastro é cortado; tirar o filtro quando a animação acaba. (Em vídeo de pessoa, desfoque e cor passam por `npx hyperframes media-treatment`, contrato item 11; o desfoque de texto é livre.)
- **Momento especial**: o efeito mais caro (texto percorrido em 3D, logo se montando) aparece uma ou duas vezes por vídeo. Em todo lugar, deixa de ser especial.
- **O movimento também é frase**: zoom para dentro = ênfase; pan percorrendo = revelação aos poucos; recuo = revelação do todo; quique pequeno = leveza. Escolher o movimento que combina com a frase.

## 5. Texto vivo

- **Caixa de frase** (só a primeira maiúscula), peso 500 a 600. CAIXA ALTA + peso 800 só numa cena de ênfase, não em todas.
  - Exceção: legenda palavra por palavra e estilos de tipografia cinética podem usar a fonte de título pesada em caixa baixa; vale o que o estilo escolhido diz.
- **Título sem ponto final** por padrão, sobretudo frase de até 4 palavras ou de uma linha. `?` só em pergunta de verdade; `!` muito raro. Se houver pontuação, ela entra por último, separada.
- **Toda frase tem ênfase.** Formas (escolher uma por vídeo; "nenhuma" é válida):

| Forma | Sensação |
|---|---|
| nenhuma: palavra por palavra de apagada para cheia, tamanho, pausa, ou ícone ao lado | calma, o produto fala |
| pílula: bloco de cor que cresce da esquerda atrás da palavra | firme, digital |
| sublinhado grosso que se desenha da esquerda | editorial |
| marca-texto inclinado, meio transparente | humano, quente |
| caixa de linha fina que se desenha em volta | técnico |
| só a cor da palavra muda | sóbrio |
| riscado e a palavra nova aparece | antes e depois ("não é X, é Y") |

  Uma forma por vídeo, não em toda frase. Sequência com ênfase: a frase entra; 0,4 a 0,6 s depois a ênfase se desenha (0,5 s `power3.out`); a pontuação, se houver, 0,25 s depois.
- **Duas cenas seguidas nunca iguais** em tamanho do texto, sentido de entrada e posição (centro, perto do objeto, canto de cima).
- Frase longa: duas linhas com pesos diferentes (500 e 600), ou a segunda linha entra depois.
- Texto que pertence a um objeto (tela, cartão) fica do lado dele, não forçado no centro.
- **Títulos limpos**: branco cheio + sombra fina (`0 4px 28px rgba(0,0,0,.5)`). Brilho (glow) só em objeto (cartão, ícone, barra), nunca em título; elemento realista (botão, linha de app) sem brilho nenhum.
- **Tamanho mínimo no celular** (quadro de 1080 de largura): texto corrido 44 px, rótulo 34 px, crédito 30 px. Nada abaixo de 30 px.
- Números que mudam a cada quadro (contador): `font-variant-numeric: tabular-nums` + `min-width`, senão a caixa treme.
- Esperar as fontes carregarem antes de dividir o texto em letras (`document.fonts.ready`).

## 6. Fundo: sempre vivo, sempre abaixo do texto

- **Bolsão do texto**: na área do texto, o fundo é escuro (luminância até 25%) para texto branco ou claro (80% ou mais) para texto marinho; nunca "meio-termo movimentado". Fundo agitado: pôr um bolsão (gradiente radial escuro de 55% para transparente) atrás do texto, entrando junto com ele.
- Elementos de fundo (partículas, formas, linhas) com cor do lado escuro da paleta, opacidade até 0,35 no bolsão, no máximo 40 elementos claros visíveis.
- **Teste**: quadro com o título cheio, em tons de cinza; se alguma parte do fundo é tão clara quanto as letras, o fundo está forte demais.
- **Fora do bolsão, o fundo é rico**: pelo menos duas camadas (base + luz, textura ou mancha de cor), cores da paleta, nunca preto ou branco puros, nunca cor chapada única. Opções (com as cores do `marca.json`):
  - brilho no horizonte: `fundo` em cima, `marinho` no meio, brilho radial da cor de `acento` a 30% embaixo;
  - spot + tom: radial da cor de `acao` a 18% sobre `marinho`;
  - papel claro: `creme` com 2 ou 3 manchas radiais da cor de acento a 15–25%, derivando ±60 px;
  - grão: textura fina por cima de tudo (seção 7).
- **O fundo nunca está parado.** Escolher uma linguagem de movimento por vídeo (duas se o fundo troca entre segmentos):

| # | Movimento de fundo | Sensação |
|---|---|---|
| 1 | textura + câmera respirando + um movimento sutil (tom, luz ou grão andando devagar) | calmo, caro |
| 2 | gradiente grande girando ou deslizando devagar (8 a 15 s) | moderno |
| 3 | 2 a 4 manchas de cor desfocadas flutuando (±60 px, 4 a 6 s) | leve |
| 4 | grão vivo | orgânico |
| 5 | uma varredura de luz por segmento (não contínua) | premium |
| 6 | forma geométrica grande (do logo) girando 20 a 40 s por volta, 2 camadas de paralaxe | marca |
| 7 | partículas subindo devagar | quente |
| 8 | grade que respira (escala 1,00 ↔ 1,04, 6 a 10 s) | técnico |
| 9 | texto fantasma gigante deslizando atrás, contraste baixo | editorial |
| 10 | foto com Ken Burns + paralaxe de 2 camadas | narrativa |
| 11 | fluxo horizontal (riscos, faixas) | só se o tema for velocidade |

- **Troca de fundo** (escuro ↔ claro, cor nova) quando o segmento muda de clima (problema → solução, fala → CTA), sempre com um gatilho visível: no corte, na batida, atrás de um objeto que cobre a lente, ou por uma ação na tela. Nunca fade cruzado sem motivo (parece troca de slide). No fundo claro o texto vira marinho e o bolsão escuro sai.
- Alternar cenas escuras e claras dá mais contraste que qualquer efeito dentro da cena.

## 7. Grão (gradiente granulado)

Gradiente saturado de 2 ou 3 cores com grão fino por cima: dá aspecto analógico e evita o "degrau" de cor quando o vídeo é comprimido.

```html
<svg width="0" height="0" style="position:absolute"><filter id="grain" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="3" stitchTiles="stitch"/>
  <feColorMatrix type="saturate" values="0"/></filter></svg>
<div class="grain" id="grain"></div>
```
```css
.grain{position:absolute;inset:-60px;pointer-events:none;filter:url(#grain);opacity:.22;mix-blend-mode:overlay}
```
```js
// grão vivo e determinístico: a posição pula 12 vezes por segundo a partir do tempo, nunca Math.random
const grainAt = k => `translate(${k*37%60-30}px,${k*61%60-30}px)`;
for (let k = 0; k < Math.ceil(DUR*12); k++) tl.set('#grain', {transform: grainAt(k)}, k/12);
```

- Fundo escuro: `overlay`, opacidade 0,15 a 0,3. Fundo claro: `multiply`, 0,08 a 0,15.
- O grão some na compressão: na entrega, `-crf 12 -tune grain` no libx264 e conferir o MP4, não só a prévia. O Instagram recomprime: grão um pouco maior resiste melhor.
- Grão em cima de vídeo de pessoa vai pelo `media-treatment` do HyperFrames (contrato, item 11).

## 8. Objetos, telas e números

- **Uma família de render por vídeo**: plano chapado, 3D macio (argila), 3D brilhante, vidro, isométrico, linha neon, ilustração plana. Misturar sem motivo parece banco de imagem.
- **Tela de produto** (um app, um painel, um site): montada de novo a partir dos componentes reais, com a fonte e as cores do produto (não a fonte de título), sendo usada (cursor clicando, dado preenchendo). Print parado com zoom não vale. Nunca dado real de cliente.
- **Câmera segue o clique** quando ele importa: 0,3 a 0,5 s antes do cursor chegar, aproxima (escala 1,4 a 2,2, 0,6 a 0,9 s `power2.inOut`), alvo um pouco acima do centro; o cursor para ~0,2 s e o botão afunda (0,92 para 1); depois a câmera recua ou desliza para o resultado (0,7 a 1 s). Só 1 a 3 cliques por bloco; o cursor fica dentro do invólucro que escala.
- **Digitação e contador** pelo tempo da timeline, nunca por `setInterval`: `tl.fromTo(o,{i:0},{i:n,ease:'none',onUpdate:()=>el.textContent=str.slice(0,Math.round(o.i))})`.
- **Nenhum número que a pessoa não disse ou que não tenha fonte** (`AGENTS.md`, regra "Escrita na tela").

## 9. Receitas para o HyperFrames

Câmera com tamanho de plano (vale para a cena de motion e para o invólucro do vídeo de pessoa):

```js
// #cam envolve tudo o que é "mundo"; legenda e rótulos ficam fora dele
// Os valores são calculados antes e animados com fromTo direto no #cam (contrato do HyperFrames).
// Testado em 06/11/2026: o mesmo instante dá o mesmo quadro indo e voltando na timeline.
const W = 1080, H = 1920;
const frame = (s, fx, fy) => {                       // s = escala; fx, fy = ponto que vai para o centro
  let x = W/2 - fx*s, y = H/2 - fy*s;
  x = Math.min(0, Math.max(W - W*s, x)); y = Math.min(0, Math.max(H - H*s, y)); // nunca revela a borda
  return { x, y, scale: s };
};
let cur = frame(1, W/2, H/2);
tl.set('#cam', { transformOrigin: '0 0', ...cur }, 0);
const shot  = (at, dur, s, fx, fy, ease='power2.inOut') => { const nx = frame(s, fx, fy);
  tl.fromTo('#cam', { ...cur }, { ...nx, duration: dur, ease, immediateRender: false }, at); cur = nx; };
const cutTo = (at, s, fx, fy) => { cur = frame(s, fx, fy); tl.set('#cam', { ...cur }, at); };
// chamar shot/cutTo em ordem de tempo
// exemplo: fechar no rosto (y ~ 560) por 0,8 s, depois voltar ao aberto
// shot(4.2, .8, 1.25, 540, 560); shot(7.0, .7, 1, 540, 960);
```

Mergulho 3D (push-through) no corte:

```js
const camThrough = (atCut, { push=2.0, from=1.5, inDur=.5, outDur=.95 } = {}) => {
  tl.to('#cam', { scale: push, duration: inDur, ease: 'power2.in' }, atCut - inDur);
  tl.set('#cam', { scale: from }, atCut);
  tl.to('#cam', { scale: 1, duration: outDur, ease: 'power3.out' }, atCut);
};
// transformOrigin aponta para o texto (centro, ou '50% 30%' se o texto está em cima)
```

Lembretes do contrato: `fromTo` em vez de `from`; nada de `Date.now()`/`Math.random()` sem semente; toda animação depende só do tempo da timeline; não animar `display`/`visibility` num `.clip`.

## 10. Som (a skill de origem não cobre; regras do kit)

- Trilha instrumental o vídeo todo, abaixando sozinha sob a voz (receita 6 de `ferramentas/ffmpeg-receitas.md`).
- Efeito sonoro casado com o que se vê: whoosh na transição (o pico no corte), pop ou clique quando um gráfico entra, impacto na palavra-chave, tique no contador. Um efeito por evento visual, não em toda palavra.
- Cortes e trocas de plano na batida da trilha quando não há fala por cima.

## 11. Lista de conferência antes de mostrar o vídeo ao dono

- [ ] Nenhuma cena com três níveis de texto; nenhuma cena que viraria slide sem mudança.
- [ ] Tamanho de plano trocando nas frases-chave; nunca dois planos iguais seguidos; texto entra depois da câmera.
- [ ] Pelo menos dois tipos de transição, um com profundidade; no máximo dois wipes; nenhuma faixa chapada varrendo; nenhuma transição repetida em todos os cortes.
- [ ] Entrada lenta, saída rápida; desfoque no sentido do movimento nos textos.
- [ ] Ênfase em toda frase, com uma única forma no vídeo; sem ponto final automático; tamanho, sentido e posição variando entre cenas.
- [ ] Bolsão do texto escuro ou claro (teste em tons de cinza); fundo com duas camadas e sempre em movimento; troca de fundo com gatilho visível.
- [ ] Brilho só em objeto; títulos limpos com sombra fina.
- [ ] Nada abaixo de 30 px; tudo dentro da área segura do Instagram (`AGENTS.md`).
- [ ] Efeitos sonoros casados com cortes e gráficos; trilha abaixando sob a voz.
- [ ] `npx hyperframes check --json` sem erro e quadros olhados com `snapshot`.
