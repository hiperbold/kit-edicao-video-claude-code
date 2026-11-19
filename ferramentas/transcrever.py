#!/usr/bin/env python3
"""Transcreve um áudio ou vídeo e grava, ao lado do arquivo, "<nome>.srt" e "<nome> - transcricao.txt".

Uso (normalmente pelo transcrever.ps1 ou transcrever.sh):
  python ferramentas/transcrever.py <arquivo> [--idioma pt] [--nomes nomes.txt] [--modelo large-v3] [--device auto|cuda|cpu]
Usa o faster-whisper, local. Nomes e siglas que o Whisper erra: veja ferramentas/_whisper.py (nomes.txt).
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _whisper import carregar_modelo, corrigir, ler_nomes  # noqa: E402


def tempo_srt(s):
    ms = int(round(s * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("arquivo")
ap.add_argument("--idioma", default="pt")
ap.add_argument("--nomes", default=None)
ap.add_argument("--modelo", default="large-v3")
ap.add_argument("--device", default="auto", choices=["auto", "cuda", "cpu"])
a = ap.parse_args()

arquivo = os.path.abspath(a.arquivo)
base = os.path.splitext(arquivo)[0]
dica, correcoes = ler_nomes(a.nomes)
m = carregar_modelo(a.modelo, a.device)
segs, _ = m.transcribe(arquivo, language=a.idioma, vad_filter=False, initial_prompt=dica or None)
segs = list(segs)
with open(base + ".srt", "w", encoding="utf-8") as f:
    for i, s in enumerate(segs, 1):
        f.write(f"{i}\n{tempo_srt(s.start)} --> {tempo_srt(s.end)}\n{corrigir(s.text.strip(), correcoes)}\n\n")
with open(base + " - transcricao.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(corrigir(s.text.strip(), correcoes) for s in segs) + "\n")
print(f"ok: {os.path.basename(base)}.srt e {os.path.basename(base)} - transcricao.txt em {os.path.dirname(arquivo)}")
