#!/usr/bin/env python3
"""Transcrição palavra por palavra (faster-whisper, local) para cortar em fronteira exata de palavra.

Uso:
  python ferramentas/palavras.py <audio-ou-video> <saida.json> [--idioma pt] [--nomes nomes.txt]
                                 [--modelo large-v3] [--device auto|cuda|cpu] [--dica "texto"]

Saída: lista de {"w": palavra, "s": início em s, "e": fim em s}.
Para o reels.mjs, use o JSON de um vídeo já cortado: {"dur": <segundos>, "palavras": [...]} (veja exemplo/composicao/corte.json);
este script escreve só a lista, e você a coloca dentro de "palavras".

Nomes e siglas que o Whisper erra: crie um nomes.txt (formato em ferramentas/_whisper.py). O script procura
primeiro ./nomes.txt, depois o nomes.txt da raiz do kit. Sem arquivo, funciona igual, só sem as correções.
Precisa do faster-whisper (veja INSTALACAO.md). Placa NVIDIA usa float16; sem placa, usa o processador (mais lento).
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _whisper import carregar_modelo, corrigir, ler_nomes  # noqa: E402

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("entrada")
ap.add_argument("saida")
ap.add_argument("--idioma", default="pt")
ap.add_argument("--nomes", default=None, help="arquivo de nomes (padrão: nomes.txt, se existir)")
ap.add_argument("--modelo", default="large-v3")
ap.add_argument("--device", default="auto", choices=["auto", "cuda", "cpu"])
ap.add_argument("--dica", default="", help="texto extra para o Whisper (nomes e termos do vídeo)")
a = ap.parse_args()

dica_arquivo, correcoes = ler_nomes(a.nomes)
dica = ", ".join(x for x in (a.dica, dica_arquivo) if x)

m = carregar_modelo(a.modelo, a.device)
segs, _ = m.transcribe(a.entrada, language=a.idioma, word_timestamps=True, vad_filter=False, initial_prompt=dica or None)
palavras = [{"w": corrigir(w.word.strip(), correcoes), "s": round(w.start, 2), "e": round(w.end, 2)} for s in segs for w in s.words]
with open(a.saida, "w", encoding="utf-8") as f:
    json.dump(palavras, f, ensure_ascii=False)
print(len(palavras), "palavras")
