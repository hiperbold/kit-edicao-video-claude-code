#!/usr/bin/env python3
"""Encaixa uma locução gravada de uma vez só no tempo das cenas do vídeo.

A locução (gerada no Magnific ou gravada) vem inteira. O script corta no silêncio mais próximo
do início de cada frase e põe cada frase no começo da sua cena. Se uma frase for mais longa que a
cena, a seguinte entra logo depois dela (com 0,12 s de respiro) em vez de sobrepor.

Uso:
  python ferramentas/encaixar_locucao.py <locucao.mp3|wav> --cortes 4.03,7.68,9.47 \
      --cenas 0.15,4.55,8.45,11.45 --dur 27.42 --saida videos/<pasta>/trabalho/locucao.wav
--cortes  segundos, NA LOCUÇÃO, em que começa a frase de cada cena a partir da 2ª
          (sai do audio_timing_get do Magnific, ou do palavras.py sobre a locução)
--cenas   segundos, NO VÍDEO, em que cada cena começa (uma a mais que os cortes)
--dur     duração do vídeo; a saída tem exatamente esse tamanho
Precisa de numpy e do ffmpeg (já vêm com o .venv e o INSTALACAO.md).
Depois, misture com a trilha (receita 11 do ferramentas/ffmpeg-receitas.md).
"""
import argparse
import subprocess
import wave

import numpy as np

SR = 48000


def ler(arquivo):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", arquivo, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32).copy()


def numeros(txt):
    return [float(x) for x in txt.split(",") if x.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("locucao")
    ap.add_argument("--cortes", required=True)
    ap.add_argument("--cenas", required=True)
    ap.add_argument("--dur", type=float, required=True)
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    cortes, cenas = numeros(a.cortes), numeros(a.cenas)
    if len(cenas) != len(cortes) + 1:
        raise SystemExit(f"--cenas precisa ter um valor a mais que --cortes ({len(cenas)} cenas, {len(cortes)} cortes)")

    voz = ler(a.locucao)
    env = np.convolve(np.abs(voz), np.ones(480) / 480, "same")
    pontos = [0]
    for c in cortes:  # silêncio mais próximo, de 0,12 s antes a 0,02 s depois do início da frase
        i0, i1 = max(int((c - 0.12) * SR), pontos[-1] + 1), min(int((c + 0.02) * SR), len(voz) - 1)
        pontos.append(i0 + int(np.argmin(env[i0:i1])) if i1 > i0 else i0)
    pontos.append(len(voz))

    out = np.zeros(int(a.dur * SR), np.float32)
    fim = 0.0
    for k, cena in enumerate(cenas):
        seg = voz[pontos[k]:pontos[k + 1]].copy()
        f = min(int(0.008 * SR), len(seg) // 2)
        if f:
            seg[:f] *= np.linspace(0, 1, f)
            seg[-f:] *= np.linspace(1, 0, f)
        t = max(cena, fim + 0.12)
        i = int(t * SR)
        if i >= len(out):
            print(f"aviso: a frase {k + 1} passou do fim do vídeo e ficou de fora")
            break
        n = min(len(seg), len(out) - i)
        out[i:i + n] += seg[:n]
        fim = t + len(seg) / SR
        atraso = f" (atrasou {t - cena:.2f} s)" if t - cena > 0.01 else ""
        print(f"cena {k + 1}: {t:.2f} a {fim:.2f} s{atraso}")

    with wave.open(a.saida, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(out, -1, 1) * 32767).astype("<i2").tobytes())
    print("ok:", a.saida)


if __name__ == "__main__":
    main()
