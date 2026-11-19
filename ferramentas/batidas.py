#!/usr/bin/env python3
"""Gera uma trilha de batidas sincronizada com os cortes de um vídeo.

Só biblioteca padrão do Python (nada para instalar). Sai um WAV 48 kHz estéreo.
Uso:
  python3 ferramentas/batidas.py --tempos 0,0.7,1.37 --duracao 8.9 \
      --acentos 3,19 --subida 7.0:8.13 --saida trilha.wav

--tempos   segundos de cada corte (uma batida por corte)
--acentos  índices (a partir de 0) dos cortes com batida forte
--subida   início:fim de um ruído que sobe até a batida seguinte (opcional)
--fundo    volume do zumbido grave de fundo, 0 a 1 (padrão 0.12)
O volume final (-14 LUFS) se acerta depois, no ffmpeg (loudnorm).
"""
import argparse
import math
import random
import struct
import wave

TAXA = 48000


def kick(t, forte):
    if t < 0 or t > 0.45:
        return 0.0
    # frequência cai de ~200 Hz para 48 Hz; fase é a integral dela
    queda = 150 if forte else 110
    fase = 2 * math.pi * (48 * t + (queda / 32) * (1 - math.exp(-t * 32)))
    return math.sin(fase) * math.exp(-t * (6 if forte else 9)) * (1.0 if forte else 0.8)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--tempos", required=True)
    p.add_argument("--duracao", type=float, required=True)
    p.add_argument("--acentos", default="")
    p.add_argument("--subida", default="")
    p.add_argument("--fundo", type=float, default=0.12)
    p.add_argument("--saida", required=True)
    a = p.parse_args()

    tempos = [float(x) for x in a.tempos.split(",") if x.strip()]
    acentos = {int(x) for x in a.acentos.split(",") if x.strip()}
    sub_ini = sub_fim = None
    if a.subida:
        sub_ini, sub_fim = (float(x) for x in a.subida.split(":"))

    n = int(a.duracao * TAXA)
    rnd = random.Random(7)  # semente fixa: mesmo arquivo a cada execução
    ruido = [rnd.uniform(-1, 1) for _ in range(TAXA)]
    esq = [0.0] * n
    dir_ = [0.0] * n

    # batidas e cliques
    for i, t0 in enumerate(tempos):
        forte = i in acentos
        ini = int(t0 * TAXA)
        for k in range(int(0.45 * TAXA)):
            j = ini + k
            if j >= n:
                break
            t = k / TAXA
            v = kick(t, forte)
            if t < 0.012:  # clique de ataque, ruído com decaimento rápido
                v += ruido[k] * 0.35 * (1 - t / 0.012)
            if forte and t < 0.18:  # caixa de ruído na batida forte
                v += ruido[(k * 3) % TAXA] * 0.25 * math.exp(-t * 22)
            esq[j] += v
            dir_[j] += v

    # chimbal leve entre as batidas (metade do intervalo)
    for a_t, b_t in zip(tempos, tempos[1:]):
        meio = int(((a_t + b_t) / 2) * TAXA)
        for k in range(int(0.04 * TAXA)):
            j = meio + k
            if j >= n:
                break
            t = k / TAXA
            ant = ruido[(k * 7 + 11) % TAXA]
            atual = ruido[(k * 7 + 12) % TAXA]
            v = (atual - ant) * 0.09 * math.exp(-t * 90)
            esq[j] += v * 1.1
            dir_[j] += v * 0.9

    # zumbido grave de fundo com entrada e saída suaves
    for j in range(n):
        t = j / TAXA
        env = min(1.0, t / 0.4) * min(1.0, (a.duracao - t) / 0.5)
        v = (math.sin(2 * math.pi * 55 * t) + 0.5 * math.sin(2 * math.pi * 82.5 * t)) * a.fundo * env
        esq[j] += v
        dir_[j] += v

    # subida de ruído
    if sub_ini is not None:
        ini, fim = int(sub_ini * TAXA), min(n, int(sub_fim * TAXA))
        anterior = 0.0
        for j in range(ini, fim):
            prog = (j - ini) / max(1, fim - ini)
            corte = 0.02 + 0.5 * prog  # filtro passa-baixa que abre
            anterior += corte * (ruido[j % TAXA] - anterior)
            v = anterior * 0.5 * prog ** 2
            esq[j] += v
            dir_[j] += v

    pico = max(max(abs(x) for x in esq), max(abs(x) for x in dir_), 1e-9)
    ganho = 0.89 / pico
    with wave.open(a.saida, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(TAXA)
        quadros = bytearray()
        for l, r in zip(esq, dir_):
            quadros += struct.pack("<hh", int(l * ganho * 32767), int(r * ganho * 32767))
        w.writeframes(bytes(quadros))
    print(f"ok: {a.saida} ({a.duracao:.2f} s, {len(tempos)} batidas)")


if __name__ == "__main__":
    main()
