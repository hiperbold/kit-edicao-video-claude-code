#!/usr/bin/env python3
"""Trilha de fundo leve e original (sintetizada aqui, sem direito autoral de terceiros).

Pop leve e alegre: pad suave, piano elétrico em arpejo, baixo, bumbo macio, estalo e chimbal discretos.
Sai um WAV 48 kHz estéreo. O volume final se acerta na mixagem (fica por baixo da voz).
Uso:
  python ferramentas/trilha_leve.py --duracao 32.1 --saida trilha.wav [--bpm 104] [--tom 0] [--fade 1.2] [--semente 7]
--tom  semitons acima de Dó (0 = Dó maior; 2 = Ré maior ...)
Precisa de numpy (pip install numpy; já vem no .venv do kit, veja INSTALACAO.md).
"""
import argparse
import wave

import numpy as np

TAXA = 48000
# I - V - vi - IV (graus em semitons a partir da tônica)
PROGRESSAO = [[0, 4, 7], [7, 11, 14], [9, 12, 16], [5, 9, 12]]
BAIXO = [0, 7, 9, 5]


def hz(semitom, base=261.63):
    return base * 2 ** (semitom / 12)


def env_ad(n, ataque, queda):
    t = np.arange(n) / TAXA
    e = np.exp(-t / queda)
    a = int(ataque * TAXA)
    if a > 0:
        e[:a] *= np.linspace(0, 1, a)
    return e


def piano(f, dur):  # piano elétrico simples: fundamental + harmônicos que caem mais rápido
    n = int(dur * TAXA)
    t = np.arange(n) / TAXA
    s = np.sin(2 * np.pi * f * t) * env_ad(n, 0.004, 0.55)
    s += 0.35 * np.sin(2 * np.pi * 2 * f * t) * env_ad(n, 0.002, 0.22)
    s += 0.12 * np.sin(2 * np.pi * 3 * f * t + 0.3) * env_ad(n, 0.001, 0.09)
    return s


def pad(freqs, dur):
    n = int(dur * TAXA)
    t = np.arange(n) / TAXA
    s = np.zeros(n)
    for f in freqs:
        for k, (amp, desv) in enumerate([(1.0, 0.0), (0.5, 0.25), (0.25, -0.2)]):
            ff = f * (k + 1) * 2 ** (desv / 1200 * 4)
            s += amp * np.sin(2 * np.pi * ff * t + k)
    env = np.minimum(1, t / 0.35) * np.minimum(1, (dur - t) / 0.35)
    return s * env / len(freqs)


def baixo(f, dur):
    n = int(dur * TAXA)
    t = np.arange(n) / TAXA
    s = np.sin(2 * np.pi * f * t) + 0.2 * np.sin(2 * np.pi * 2 * f * t)
    return s * env_ad(n, 0.006, 0.35) * np.minimum(1, (dur - t) / 0.03).clip(0, 1)


def bumbo():
    n = int(0.35 * TAXA)
    t = np.arange(n) / TAXA
    fase = 2 * np.pi * (50 * t + (90 / 28) * (1 - np.exp(-t * 28)))
    return np.sin(fase) * np.exp(-t * 11)


def ruido_filtrado(rnd, dur, queda, passa_alta):
    n = int(dur * TAXA)
    r = rnd.uniform(-1, 1, n)
    if passa_alta:  # diferença simples = tira o grave
        r = np.diff(r, prepend=0) * 0.6
    return r * np.exp(-np.arange(n) / TAXA / queda)


def somar(dest, sinal, ini, ganho=1.0, pan=0.0):
    i = int(ini * TAXA)
    if i >= dest.shape[1]:
        return
    s = sinal[: dest.shape[1] - i] * ganho
    dest[0, i : i + len(s)] += s * (1 - max(0, pan))
    dest[1, i : i + len(s)] += s * (1 + min(0, pan))


def gerar(duracao, bpm, tom, fade, semente):
    rnd = np.random.default_rng(semente)
    batida = 60 / bpm
    compasso = 4 * batida
    out = np.zeros((2, int(duracao * TAXA) + TAXA))
    n_comp = int(np.ceil(duracao / compasso))
    arpejo = [0, 1, 2, 1, 0, 2, 1, 2]  # índice da nota do acorde em cada colcheia
    for c in range(n_comp):
        t0 = c * compasso
        grau = c % 4
        acorde = [x + tom for x in PROGRESSAO[grau]]
        somar(out, pad([hz(x - 12) for x in acorde], compasso + 0.3), t0, 0.16)
        intro = c == 0  # primeiro compasso sem bateria, entra macio
        for k in range(8):
            nota = acorde[arpejo[k]] + (12 if k in (3, 7) else 0)
            vel = 0.8 if k % 2 == 0 else 0.55
            somar(out, piano(hz(nota), batida * 1.6), t0 + k * batida / 2, 0.11 * vel, pan=0.25 if k % 2 else -0.25)
        b = hz(BAIXO[grau] + tom - 24)
        for pos, dur in [(0, 1.4), (1.5, 0.45), (2, 1.4), (3.5, 0.45)]:
            somar(out, baixo(b, dur * batida), t0 + pos * batida, 0.30)
        if intro:
            continue
        for k in range(4):
            if k in (0, 2):
                somar(out, bumbo(), t0 + k * batida, 0.45)
            else:
                somar(out, ruido_filtrado(rnd, 0.18, 0.045, True), t0 + k * batida, 0.16)
        for k in range(8):
            somar(out, ruido_filtrado(rnd, 0.06, 0.012 if k % 2 else 0.02, True), t0 + k * batida / 2, 0.06 if k % 2 else 0.035, pan=0.3)
    out = out[:, : int(duracao * TAXA)]
    t = np.arange(out.shape[1]) / TAXA
    out *= np.clip((duracao - t) / fade, 0, 1) * np.clip(t / 0.4, 0, 1)
    out *= 0.7 / max(np.abs(out).max(), 1e-9)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--duracao", type=float, required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--bpm", type=float, default=104)
    ap.add_argument("--tom", type=int, default=0)
    ap.add_argument("--fade", type=float, default=1.2)
    ap.add_argument("--semente", type=int, default=7)
    a = ap.parse_args()
    s = gerar(a.duracao, a.bpm, a.tom, a.fade, a.semente)
    pcm = (s.T * 32767).astype("<i2").tobytes()
    with wave.open(a.saida, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(TAXA)
        w.writeframes(pcm)
    print(f"ok: {a.saida} ({a.duracao:.1f} s, {a.bpm:.0f} bpm)")
