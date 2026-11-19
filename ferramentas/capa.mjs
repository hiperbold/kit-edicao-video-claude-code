// Capa de Reels (1080x1920) com todo o conteúdo dentro da faixa de 1350 px que a grade do Instagram mostra.
// Cores, fontes e logo vêm do marca.json da raiz do projeto (ou do marca.exemplo.json).
// Uso: node ferramentas/capa.mjs <pasta-do-video> [--guia]   (lê <pasta-do-video>/composicao/capa.json)
// capa.json: { "rosto": "assets/img/capa-rosto.jpg", "rostoPos": "50% 30%", "logoTopo": "assets/img/logo-x.svg",
//              "titulo": "Texto com <b>destaque</b>", "tituloPx": 130, "apoio": "linha curta",
//              "apoioTop": 520, "fotoTop": 640, "saida": "final/capa-x.jpg" }
//   rosto     um quadro do próprio vídeo (caminho dentro de composicao/)
//   logoTopo  opcional: logo de uma empresa ou ferramenta citada, mostrado numa plaquinha branca no topo
//   O logo da sua marca (marca.json) aparece no canto de baixo da foto.
// A faixa visível na grade vai de y 285 a 1635. Acima e abaixo dela só fundo, sem texto nem elemento.
// --guia desenha as duas linhas da faixa (só para conferir; grava um arquivo "-guia.jpg" ao lado).
// O Chrome usado é o que o HyperFrames instala (npx hyperframes browser ensure). Outro Chrome: variável CHROME_PATH.
import fs from 'fs';
import path from 'path';
import os from 'os';
import { execFileSync } from 'child_process';
import { pathToFileURL } from 'url';
import { lerMarca, rgba, misturar, prepararAssets, pilha } from './_marca.mjs';

const pasta = path.resolve(process.argv.slice(2).find(a => !a.startsWith('--')) || '.');
const comp = path.join(pasta, 'composicao');
const cfg = JSON.parse(fs.readFileSync(path.join(comp, 'capa.json'), 'utf8'));
const guia = process.argv.includes('--guia');

const { marca } = lerMarca();
const C = marca.cores;
const assets = prepararAssets(marca, comp);
const FT = pilha(marca, 'titulo'), FX = pilha(marca, 'texto');

const TOPO = 285, BASE = 1635; // (1920 - 1350) / 2
const html = `<!doctype html><html><head><meta charset="utf-8"><style>
${assets.fontFace}*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:${C.fundo};color:#fff;font-family:${FX}}
.fundo{position:absolute;inset:0;background:radial-gradient(900px 700px at 50% 42%,${misturar(C.fundo, C.acento, 0.18)} 0%,${C.fundo} 70%)}
.faixa{position:absolute;left:0;right:0;top:${TOPO}px;height:${BASE - TOPO}px}
.topo{position:absolute;left:90px;right:90px;top:50px;height:84px;display:flex;align-items:center;justify-content:space-between}
.tile{height:84px;padding:0 30px;border-radius:22px;background:#fff;display:flex;align-items:center;box-shadow:0 12px 34px rgba(0,0,0,.4)}
.tile img{height:38px;max-width:200px}
.titulo{position:absolute;left:90px;right:90px;top:175px;font-family:${FT};font-weight:800;font-size:${cfg.tituloPx || 130}px;line-height:.95;letter-spacing:-1px;text-shadow:0 4px 28px rgba(0,0,0,.5)}
.titulo b{color:${C.acento};font-weight:800}
.apoio{position:absolute;left:90px;right:90px;top:${cfg.apoioTop || 520}px;font-weight:700;font-size:44px;line-height:1.2;color:${C.creme}}
.foto{position:absolute;left:90px;right:90px;top:${cfg.fotoTop || 640}px;bottom:40px;border-radius:36px;overflow:hidden;box-shadow:0 24px 60px rgba(0,0,0,.5);border:3px solid ${rgba(C.creme, 0.12)}}
.foto img{width:100%;height:100%;object-fit:cover;object-position:${cfg.rostoPos || '50% 30%'}}
.foto:after{content:"";position:absolute;inset:auto 0 0 0;height:180px;background:linear-gradient(transparent,${rgba(C.fundo, 0.85)})}
.foto img.logo{position:absolute;right:40px;bottom:34px;width:auto;height:46px;z-index:2;object-fit:contain}
.guia{position:absolute;left:0;right:0;height:0;border-top:3px dashed #ff3b3b;z-index:9}
</style></head><body>
<div class="fundo"></div>
<div class="faixa">
  <div class="topo">${cfg.logoTopo ? `<div class="tile"><img src="${cfg.logoTopo}" alt=""></div>` : ''}</div>
  <div class="titulo">${cfg.titulo}</div>
  ${cfg.apoio ? `<div class="apoio">${cfg.apoio}</div>` : ''}
  <div class="foto"><img src="${cfg.rosto}" alt="">${assets.logo ? `<img class="logo" src="${assets.logo}" alt="">` : ''}</div>
</div>
${guia ? `<div class="guia" style="top:${TOPO}px"></div><div class="guia" style="top:${BASE}px"></div>` : ''}
</body></html>`;

// arquivos temporários ficam dentro de composicao/ e são apagados no fim (nunca na pasta temporária do sistema)
const htmlPath = path.join(comp, `capa-tmp-${Date.now()}.html`);
const png = path.join(comp, `capa-tmp-${Date.now()}.png`);

const achar = d => {
  if (!fs.existsSync(d)) return null;
  for (const n of fs.readdirSync(d, { withFileTypes: true })) {
    const p = path.join(d, n.name);
    if (n.isDirectory()) { const r = achar(p); if (r) return r; }
    else if (/^chrome-headless-shell(\.exe)?$/.test(n.name)) return p;
  }
  return null;
};
const chrome = process.env.CHROME_PATH || achar(path.join(os.homedir(), '.cache', 'hyperframes', 'chrome'));
if (!chrome) { console.error('Chrome não encontrado. Rode: npx hyperframes browser ensure'); process.exit(1); }

try {
  fs.writeFileSync(htmlPath, html);
  execFileSync(chrome, ['--headless', '--hide-scrollbars', '--allow-file-access-from-files', '--virtual-time-budget=4000',
    '--window-size=1080,1920', `--screenshot=${png}`, pathToFileURL(htmlPath).href], { stdio: 'ignore' });
  const saida = path.join(pasta, guia ? cfg.saida.replace(/\.jpg$/, '-guia.jpg') : cfg.saida);
  fs.mkdirSync(path.dirname(saida), { recursive: true });
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', png, '-q:v', '1', saida]);
  console.log(saida);
} finally {
  for (const f of [htmlPath, png]) if (fs.existsSync(f)) fs.unlinkSync(f);
}
