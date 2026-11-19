// Peças comuns ao reels.mjs e ao capa.mjs: lê a marca (marca.json, ou marca.exemplo.json se não existir),
// calcula cores derivadas e copia logo e fontes para dentro da pasta composicao/ do vídeo.
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// raiz do kit = pasta acima de ferramentas/
export const RAIZ = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

export function lerMarca() {
  for (const nome of ['marca.json', 'marca.exemplo.json']) {
    const p = path.join(RAIZ, nome);
    if (fs.existsSync(p)) return { marca: JSON.parse(fs.readFileSync(p, 'utf8')), origem: nome };
  }
  throw new Error('Não achei marca.json nem marca.exemplo.json na raiz do projeto: ' + RAIZ);
}

// "#3B82F6" (ou "#38F") -> [59, 130, 246]
const rgb = hex => {
  let h = hex.replace('#', '');
  if (h.length === 3) h = [...h].map(c => c + c).join('');
  return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16));
};
export const rgba = (hex, a) => `rgba(${rgb(hex).join(',')},${a})`;
// mistura duas cores: t = 0 devolve a, t = 1 devolve b
export const misturar = (a, b, t) => '#' + rgb(a).map((v, i) => Math.round(v + (rgb(b)[i] - v) * t).toString(16).padStart(2, '0')).join('');

// Copia o logo e as fontes que existirem para <composicao>/assets/marca/ e devolve:
//   logo: caminho do logo relativo à composição (ou null se o arquivo não existe)
//   fontFace: CSS @font-face das fontes que foram achadas
// Fonte que não existe só gera aviso: o vídeo sai com a fonte padrão do sistema.
export function prepararAssets(marca, compDir) {
  const dest = path.join(compDir, 'assets', 'marca');
  fs.mkdirSync(dest, { recursive: true });
  const copiar = rel => {
    const origem = path.join(RAIZ, rel);
    if (!fs.existsSync(origem)) { console.warn('aviso: arquivo da marca não encontrado:', rel); return null; }
    fs.copyFileSync(origem, path.join(dest, path.basename(rel)));
    return 'assets/marca/' + path.basename(rel);
  };
  const logo = marca.logo ? copiar(marca.logo) : null;
  let fontFace = '';
  for (const papel of ['titulo', 'texto']) {
    const f = marca.fontes?.[papel];
    if (!f) continue;
    for (const [peso, arq] of Object.entries(f.arquivos || {})) {
      const url = copiar(arq);
      if (!url) continue;
      const formato = /\.woff2$/i.test(arq) ? 'woff2' : /\.woff$/i.test(arq) ? 'woff' : /\.otf$/i.test(arq) ? 'opentype' : 'truetype';
      fontFace += `@font-face{font-family:"${f.familia}";font-weight:${peso};src:url(${url}) format("${formato}");}\n`;
    }
  }
  return { logo, fontFace };
}

// família da fonte para usar no CSS, com Arial como reserva
export const pilha = (marca, papel) => `"${marca.fontes?.[papel]?.familia || 'Arial'}",Arial,sans-serif`;
