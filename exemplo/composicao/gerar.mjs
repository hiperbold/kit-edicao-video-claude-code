// Exemplo mínimo: Reel de 8 s sobre organizar a agenda (texto inventado só para o exemplo).
// Rodar (de qualquer pasta): node exemplo/composicao/gerar.mjs
// Escreve exemplo/composicao/index.html. Cores, fontes, logo e cartão final vêm do marca.json da raiz.
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { build, P, COR } from '../../ferramentas/reels.mjs';

const dir = path.dirname(fileURLToPath(import.meta.url));
const { palavras, dur } = JSON.parse(fs.readFileSync(path.join(dir, 'corte.json'), 'utf8'));
const VID = dur;          // duração do vídeo falado (a mesma do assets/vid/base.mp4)
const TOTAL = VID + 2.6;  // mais 2,6 s de cartão final (o check pede 2 s de leitura na última frase)

build({
  dir, VID, TOTAL, palavras,
  rosto: [540, 880],      // onde fica o rosto no quadro (para onde o zoom aponta)
  baixoTop: -560,         // deslocamento do vídeo na metade de baixo, na tela dividida
  // câmera: [início, modo, zoomInicial, zoomFinal]; 'cheia' = pessoa em tela cheia, 'div' = tela dividida
  cam: [
    [0, 'cheia', 1.1, 1.16],
    [2.4, 'div', 1, 1],
    [5.9, 'cheia', 1.06, 1.1],
  ],
  semLegenda: [[0.1, 2.4], [5.85, 99]], // sem legenda onde o texto grande já diz a mesma coisa (cena 1 e selo final)
  chave: ['agenda', 'três'],       // palavras que ficam na cor de acento
  css: `
.big-num{top:430px;font-size:300px;color:${COR.acento};}
.big-leg{position:absolute;left:0;right:0;top:730px;text-align:center;font-weight:700;font-size:54px;color:${COR.creme};}
`,
  cenas(ctx) {
    const { at, f2, sfx } = ctx;
    // 1. abertura em tela cheia: texto grande na faixa de baixo
    P.faixa(ctx, 'f1', at('organizar') - 0.05, 2.4, 'Organizar a <b>agenda</b>', 'sem complicar', at('agenda') );
    // 2. painel com um número grande, que aparece quando ele é dito
    const t3 = at('três');
    P.painel(ctx, 'p1', 2.4, 5.9, 'Comece pelo <b>essencial</b>',
      `<div class="big-num" id="n1">3</div><div class="big-leg" id="n1l">tarefas por dia</div>`,
      `tl.fromTo("#n1",{scale:1.6,opacity:0},{scale:1,opacity:1,duration:0.35,ease:"back.out(2)"},${f2(t3)});
tl.fromTo("#n1l",{y:24,opacity:0},{y:0,opacity:1,duration:0.3,ease:"power3.out"},${f2(t3 + 0.25)});\n`,
      '');
    sfx('pop', t3, 0.26);
    // 3. chamada final: selo "link da bio" (texto vem de cartaoFinal.selo no marca.json)
    P.linkBio(ctx, 'f2', at('Veja'), VID - 0.1);
  },
});
