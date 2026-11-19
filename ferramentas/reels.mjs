// Gerador de Reels/Shorts verticais (1080x1920) em tela dividida.
// Estilo: painel gráfico em cima e a pessoa embaixo no plano original; tela cheia nos re-ganchos;
// legenda palavra por palavra; corte seco com zoom; cartão final com logo e chamada.
// Cores, fontes, logo e textos do cartão final vêm do marca.json da raiz do projeto
// (se não existir, do marca.exemplo.json).
//
// Uso: cada vídeo tem composicao/gerar.mjs que chama build(config). Escreve composicao/index.html.
// Veja exemplo/composicao/gerar.mjs.
import fs from 'fs';
import path from 'path';
import { lerMarca, rgba, prepararAssets, pilha } from './_marca.mjs';

const { marca: MARCA, origem: ORIGEM_MARCA } = lerMarca();
const C = MARCA.cores;
// `azul` é apelido de `acento` (nome herdado de quem copia o gerar.mjs de outro projeto)
export const COR = { fundo: C.fundo, marinho: C.marinho, acento: C.acento, azul: C.acento, acao: C.acao, creme: C.creme, cinza: C.cinza };
const FUNDO = a => rgba(COR.fundo, a);
const ACENTO = a => rgba(COR.acento, a);
const f2 = n => (+n).toFixed(2);
const DUR = { whoosh: 0.5, 'whoosh-curto': 0.25, impacto: 1, tique: 0.06, clique: 0.07, pop: 0.14, risco: 0.35 };
const CARTAO = { titulo: 'Seu CTA aqui', subtitulo: 'no link da bio', selo: 'Link da bio', ...(MARCA.cartaoFinal || {}) };

/**
 * cfg:
 *  dir        pasta composicao/ do vídeo (onde escreve o index.html)
 *  VID        duração do vídeo falado, em segundos
 *  TOTAL      duração total (VID + cartão final)
 *  palavras   [{w, s, e}] com o tempo de cada palavra (de corte.json, gerado por ferramentas/palavras.py)
 *  rosto      [x, y] do rosto no quadro de 1080x1920 (para onde o zoom aponta)
 *  baixoTop   deslocamento vertical do vídeo na metade de baixo (padrão -560)
 *  cam        [[início, 'cheia' | 'div', zoomInicial, zoomFinal], ...] a câmera ao longo do vídeo
 *  semLegenda [[de, até], ...] trechos sem legenda (quando o texto grande já diz a mesma coisa)
 *  chave      palavras que ficam na cor de acento
 *  css        CSS próprio das cenas deste vídeo
 *  cenas(ctx) função que monta as cenas usando P.* e ctx
 */
export function build(cfg) {
  const { dir, VID, TOTAL } = cfg;
  const assets = prepararAssets(MARCA, dir);
  const FT = pilha(MARCA, 'titulo'), FX = pilha(MARCA, 'texto');
  // junta pedaços que o Whisper separa ("15" ",5" "%" -> "15,5%"; "meia" "-noite")
  const W = []; cfg.palavras.forEach(x => { if (/^[,%-]/.test(x.w) && W.length) { W.at(-1).w += x.w; W.at(-1).e = x.e; } else W.push({ ...x }); });
  const CARD = VID - 0.1;
  let H = '', J = '', A = '', ti = 10, nfx = 0;
  const clip = (id, s, e, cls, inner, z) => `  <div id="${id}" class="clip ${cls}" data-start="${f2(s)}" data-duration="${f2(e - s)}" data-track-index="${ti++}"${z ? ` style="z-index:${z}"` : ''}>${inner}</div>\n`;
  const sfx = (nome, s, v = 0.22) => { A += `  <audio id="fx${nfx}" class="clip" data-start="${f2(Math.max(0, s))}" data-duration="${DUR[nome]}" data-track-index="${200 + nfx++}" data-volume="${v}" src="assets/sfx/${nome}.wav"></audio>\n`; };
  const ctx = { clip, sfx, f2, COR, add: (h, j = '') => { H += h; J += j; }, at: (txt, n = 0) => { const r = W.filter(x => x.w.replace(/[.,!?%]/g, '') === txt); if (!r[n]) throw new Error('palavra não achada: ' + txt + ' #' + n); return r[n].s; } };

  // ---- câmera: [início, modo, zoomA, zoomB]; modo 'cheia' ou 'div' ----
  const Wd = 1080, Ht = 1920, FX0 = cfg.rosto?.[0] ?? 540, FY0 = cfg.rosto?.[1] ?? 880;
  const frame = s => { let x = Wd / 2 - FX0 * s, y = Ht / 2 - FY0 * s; x = Math.min(0, Math.max(Wd - Wd * s, x)); y = Math.min(0, Math.max(Ht - Ht * s, y)); return { x: +x.toFixed(1), y: +y.toFixed(1), scale: s }; };
  const cam = [...cfg.cam, [VID, 'fim', 1, 1]];
  J += `tl.set("#cam",{transformOrigin:"0 0"},0);\ntl.set("#baixo",{opacity:0},0);\n`;
  cam.slice(0, -1).forEach(([s, modo, a, b], i) => {
    const e = cam[i + 1][0];
    J += `tl.set("#cam",${JSON.stringify(frame(a))},${f2(s)});\n`;
    J += `tl.fromTo("#cam",${JSON.stringify(frame(a))},{...${JSON.stringify(frame(b))},duration:${f2(e - s)},ease:"sine.inOut",immediateRender:false},${f2(s)});\n`;
    J += `tl.set("#baixo",{opacity:${modo === 'div' ? 1 : 0}},${f2(s)});\n`;
    if (modo === 'div') J += `tl.fromTo("#bv",{scale:1},{scale:1.05,duration:${f2(e - s)},ease:"sine.inOut",immediateRender:false},${f2(s)});\n`;
    if (i > 0) sfx('whoosh-curto', s - 0.08, 0.12);
  });
  const modoEm = t => { let m = 'cheia'; cam.forEach(([s, modo]) => { if (t >= s - 0.01) m = modo; }); return m; };

  // ---- cenas próprias do vídeo ----
  cfg.cenas(ctx);

  // ---- legendas palavra por palavra ----
  const ocultar = cfg.semLegenda || [];
  const chave = new Set(cfg.chave || []);
  const ws = W.filter(x => !ocultar.some(([a, b]) => x.s >= a && x.s < b) && x.s < CARD);
  const grupos = []; let g = [];
  ws.forEach((x, i) => {
    g.push(x); const p = ws[i + 1], txt = g.map(y => y.w).join(' ');
    const quebra = !p || (/[.,?]$/.test(x.w) && x.e - g[0].s > 0.5) || (txt + ' ' + p.w).length > 26 || p.s - x.e > 0.3 || modoEm(p.s) !== modoEm(g[0].s) || ocultar.some(([a]) => a > x.s && a <= p.s);
    if (quebra) { grupos.push(g); g = []; }
  });
  grupos.forEach((gr, k) => {
    const s = gr[0].s - 0.04, prox = grupos[k + 1];
    let e = Math.min(gr.at(-1).e + 0.5, prox ? prox[0].s - 0.04 : CARD);
    ocultar.forEach(([a]) => { if (a > s && a < e) e = a; });
    const id = 'lg' + k, emenda = modoEm(gr[0].s) === 'div';
    const limpa = w => w.replace(/[.,]$/, '');
    const spans = gr.map((x, j) => `<span id="${id}w${j}" class="${chave.has(limpa(x.w).replace(/[?!]/g, '')) ? 'k' : ''}">${limpa(x.w)}</span>`).join(' ');
    H += clip(id, s, e, 'lg' + (emenda ? ' emenda' : ''), `<div class="in">${spans}</div>`);
    J += `tl.fromTo("#${id} .in",{y:14,opacity:0},{y:0,opacity:1,duration:0.12,ease:"power2.out"},${f2(s)});\n`;
    gr.forEach((x, j) => {
      J += `tl.fromTo("#${id}w${j}",{color:"#FFFFFF"},{color:"${COR.acento}",duration:0.06},${f2(Math.max(s, x.s))});\n`;
      if (!chave.has(limpa(x.w).replace(/[?!]/g, ''))) J += `tl.to("#${id}w${j}",{color:"#FFFFFF",duration:0.08},${f2(Math.max(s + 0.01, x.e))});\n`;
    });
  });

  // ---- cartão final ----
  const marcaFim = assets.logo ? `<img class="lf" src="${assets.logo}" alt="">` : `<div class="lf-nome">${MARCA.nome || ''}</div>`;
  H += clip('fim', CARD, TOTAL, 'fim', `<div class="fim-box">${marcaFim}<div class="fim-t">${CARTAO.titulo}</div><div class="fim-p">${CARTAO.subtitulo}</div></div>`, 20);
  J += `tl.fromTo("#fim",{opacity:0},{opacity:1,duration:0.3,ease:"power2.out"},${f2(CARD)});
tl.fromTo("#fim .lf, #fim .lf-nome",{scale:0.8,opacity:0},{scale:1,opacity:1,duration:0.5,ease:"back.out(1.6)"},${f2(CARD + 0.15)});
tl.fromTo("#fim .fim-t",{y:30,opacity:0},{y:0,opacity:1,duration:0.4,ease:"power3.out"},${f2(CARD + 0.4)});
tl.fromTo("#fim .fim-p",{y:30,opacity:0},{y:0,opacity:1,duration:0.4,ease:"power3.out"},${f2(CARD + 0.55)});\n`;
  sfx('whoosh', CARD - 0.25, 0.2); sfx('pop', CARD + 0.4, 0.22);

  const html = `<!doctype html>
<html lang="pt-BR">
<head><meta charset="utf-8"><meta name="viewport" content="width=1080, height=1920">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
<style>
${assets.fontFace}html,body{margin:0;background:${COR.fundo};}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;background:${COR.fundo};font-family:${FX};color:#fff;}
#cam{position:absolute;left:0;top:0;width:1080px;height:1920px;z-index:1;}
#vid{position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover;}
#veu{position:absolute;left:0;right:0;bottom:0;height:900px;z-index:2;background:linear-gradient(to bottom,${FUNDO(0)} 0%,${FUNDO(.5)} 50%,${FUNDO(.78)} 100%);}
#baixo{position:absolute;left:0;top:960px;width:1080px;height:960px;overflow:hidden;z-index:4;background:${COR.fundo};}
#bv{position:absolute;left:0;top:${cfg.baixoTop ?? -560}px;width:1080px;height:1920px;object-fit:cover;transform-origin:50% 50%;}
.clip{position:absolute;inset:0;z-index:5;}
.painel{z-index:6;height:960px;bottom:auto;overflow:hidden;background:radial-gradient(circle at 80% 10%,${ACENTO(.22)},${ACENTO(0)} 55%),${COR.fundo};}
.painel .rot{position:absolute;left:137px;right:137px;top:270px;text-align:center;font-family:${FT};font-weight:800;font-size:58px;line-height:1.05;}
.painel .rot b{color:${COR.acento};font-weight:800;}
.painel .fonte{position:absolute;left:137px;right:137px;top:880px;text-align:center;font-weight:500;font-size:28px;color:${COR.cinza};}
.painel .div{position:absolute;left:0;bottom:0;width:1080px;height:8px;background:${COR.acento};}
.card{position:absolute;left:110px;width:860px;border-radius:24px;overflow:hidden;box-shadow:0 18px 50px rgba(0,0,0,.5);background-repeat:no-repeat;}
.ilus{position:absolute;left:50%;width:440px;height:440px;margin-left:-220px;top:425px;border-radius:28px;object-fit:cover;box-shadow:0 18px 50px rgba(0,0,0,.45);}
.marca-txt{position:absolute;height:12px;border-radius:6px;background:${COR.acento};transform-origin:0 50%;mix-blend-mode:screen;opacity:.9;}
.big-num{position:absolute;left:0;right:0;text-align:center;font-family:${FT};font-weight:800;line-height:.9;}
.faixa{display:flex;flex-direction:column;align-items:center;padding-top:1080px;box-sizing:border-box;text-align:center;}
.faixa .t1{font-family:${FT};font-weight:800;font-size:110px;line-height:.95;max-width:900px;text-shadow:0 6px 26px rgba(0,0,0,.6);}
.faixa .t1 b{color:${COR.acento};}
.faixa .t2{font-weight:700;font-size:48px;margin-top:22px;color:${COR.creme};text-shadow:0 3px 14px rgba(0,0,0,.7);}
.selo{display:inline-flex;align-items:center;gap:20px;background:${COR.acento};color:#fff;border-radius:70px;padding:22px 40px;font-weight:800;font-size:44px;box-shadow:0 14px 40px rgba(0,0,0,.45);}
.selo svg{width:56px;height:56px;}
.lg{z-index:8;}
.lg .in{position:absolute;left:137px;right:137px;top:1120px;text-align:center;font-weight:800;font-size:64px;line-height:1.15;text-shadow:0 3px 4px ${FUNDO(.85)},0 6px 22px ${FUNDO(.6)};}
.lg.emenda .in{top:905px;left:50%;right:auto;transform:translateX(-50%);white-space:nowrap;font-size:50px;padding:12px 30px 14px;border-radius:20px;background:${FUNDO(.9)};text-shadow:none;}
.lg .in span{display:inline-block;}
.lg .in .k{color:${COR.acento};}
.fim{background:radial-gradient(circle at 50% 35%,${ACENTO(.35)},${ACENTO(0)} 60%),${COR.fundo};}
.fim-box{position:absolute;left:137px;right:137px;top:660px;display:flex;flex-direction:column;align-items:center;text-align:center;}
.fim .lf{width:560px;}
.fim .lf-nome{font-family:${FT};font-weight:800;font-size:96px;line-height:1;}
.fim-t{font-family:${FT};font-weight:800;font-size:92px;line-height:1;margin-top:70px;white-space:nowrap;}
.fim-p{font-weight:700;font-size:52px;color:${COR.acento};margin-top:10px;}
${cfg.css || ''}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="${TOTAL}" data-width="1080" data-height="1920">
  <div id="cam"><video id="vid" class="clip" data-start="0" data-duration="${VID}" data-track-index="0" muted playsinline src="assets/vid/base.mp4"></video></div>
  <div id="veu"></div>
  <div id="baixo"><video id="bv" class="clip" data-start="0" data-duration="${VID}" data-track-index="1" muted playsinline data-layout-allow-occlusion src="assets/vid/base.mp4"></video></div>
${H}  <audio id="voz" class="clip" data-start="0" data-duration="${VID}" data-track-index="90" data-volume="1" src="assets/voz.wav"></audio>
${A}</div>
<script>
window.__timelines = window.__timelines || {};
const tl = gsap.timeline({ paused: true });
${J}tl.set({}, {}, ${TOTAL});
window.__timelines["main"] = tl;
</script>
</body></html>
`;
  fs.writeFileSync(path.join(dir, 'index.html'), html);
  console.log('ok', path.join(dir, 'index.html'), nfx, 'efeitos (marca: ' + ORIGEM_MARCA + ')');
}

// ---- peças reutilizáveis do painel de cima ----
export const P = {
  painel(ctx, id, a, b, rot, inner, js = '', fonte = '') {
    ctx.add(ctx.clip(id, a, b, 'painel', `<div class="rot">${rot}</div>${inner}${fonte ? `<div class="fonte">${fonte}</div>` : ''}<i class="div"></i>`),
      `tl.fromTo("#${id} .rot",{y:30,opacity:0},{y:0,opacity:1,duration:0.3,ease:"power3.out"},${ctx.f2(a + 0.05)});\n` + js);
  },
  // recorte de uma captura (manchete): src, tamanho original, recorte [x,y,w,h], marca opcional [x,y,w] no recorte
  manchete(ctx, id, a, b, rot, src, [ow], [cx, cy, cw, ch], marca, tMarca, fonte) {
    const k = 860 / cw, h = Math.round(ch * k);
    const top = Math.round(420 + (450 - h) / 2);
    const mk = marca ? `<i class="marca-txt" style="left:${Math.round(110 + marca[0] * k)}px;top:${Math.round(top + marca[1] * k)}px;width:${Math.round(marca[2] * k)}px"></i>` : '';
    P.painel(ctx, id, a, b, rot, `<div class="card" style="top:${top}px;height:${h}px;background-image:url(${src});background-size:${Math.round(ow * k)}px auto;background-position:${-Math.round(cx * k)}px ${-Math.round(cy * k)}px"></div>${mk}`,
      `tl.fromTo("#${id} .card",{scale:0.92,opacity:0},{scale:1,opacity:1,duration:0.45,ease:"power3.out"},${ctx.f2(a)});
tl.fromTo("#${id} .card",{scale:1},{scale:1.05,duration:${ctx.f2(b - a - 0.45)},ease:"sine.inOut",immediateRender:false},${ctx.f2(a + 0.45)});\n` +
      (marca ? `tl.fromTo("#${id} .marca-txt",{scaleX:0},{scaleX:1,duration:0.4,ease:"power2.inOut"},${ctx.f2(tMarca)});\n` : ''), fonte);
    if (marca) ctx.sfx('risco', tMarca, 0.18);
  },
  ilustracao(ctx, id, a, b, rot, src, extraHtml = '', extraJs = '') {
    P.painel(ctx, id, a, b, rot, `<img class="ilus" src="${src}" alt="">${extraHtml}`,
      `tl.fromTo("#${id} .ilus",{scale:0.9,opacity:0},{scale:1,opacity:1,duration:0.4,ease:"power3.out"},${ctx.f2(a)});
tl.fromTo("#${id} .ilus",{scale:1},{scale:1.06,duration:${ctx.f2(b - a - 0.4)},ease:"sine.inOut",immediateRender:false},${ctx.f2(a + 0.4)});\n` + extraJs);
  },
  // texto grande na faixa de baixo, em tela cheia
  faixa(ctx, id, a, b, t1, t2 = '', t2em = null) {
    ctx.add(ctx.clip(id, a, b, 'faixa', `<div class="t1">${t1}</div>${t2 ? `<div class="t2">${t2}</div>` : ''}`),
      `tl.fromTo("#${id} .t1",{scale:1.5,opacity:0},{scale:1,opacity:1,duration:0.35,ease:"back.out(1.8)"},${ctx.f2(a)});\n` +
      (t2 ? `tl.fromTo("#${id} .t2",{y:24,opacity:0},{y:0,opacity:1,duration:0.3,ease:"power3.out"},${ctx.f2(t2em ?? a + 0.4)});\n` : ''));
    ctx.sfx('impacto', a, 0.18);
  },
  // selo de chamada para o link da bio (o texto vem de cartaoFinal.selo no marca.json, ou do argumento texto)
  linkBio(ctx, id, a, b, texto = CARTAO.selo) {
    ctx.add(ctx.clip(id, a, b, 'faixa', `<div class="selo"><svg viewBox="0 0 24 24"><path d="M12 20V6m-6 6 6-6 6 6" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg><span>${texto}</span></div>`),
      `tl.fromTo("#${id} .selo",{y:60,scale:0.7,opacity:0},{y:0,scale:1,opacity:1,duration:0.4,ease:"back.out(1.8)"},${ctx.f2(a)});
tl.fromTo("#${id} .selo svg",{y:6},{y:-8,duration:0.35,yoyo:true,repeat:7,ease:"sine.inOut"},${ctx.f2(a + 0.4)});\n`);
    ctx.sfx('pop', a, 0.24); ctx.sfx('clique', a + 0.5, 0.26);
  },
};
