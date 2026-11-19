#!/usr/bin/env bash
# Efeitos sonoros sintetizados (originais, sem direito autoral de terceiros). Mesma coisa do sfx.ps1, para Mac/Linux.
# Uso: ferramentas/sfx.sh <pasta-de-saida>      (nos vídeos: <pasta do vídeo>/composicao/assets/sfx)
# Gera WAV 48 kHz mono: whoosh, whoosh-curto, impacto, tique, clique, pop, risco.
# Volume final se acerta na mixagem (12 a 20 dB abaixo da voz). Para publicação, preferir biblioteca com licença.
set -euo pipefail
[ $# -ge 1 ] || { echo "uso: $0 <pasta-de-saida>" >&2; exit 1; }
saida="$1"
mkdir -p "$saida"
gera() { ffmpeg -hide_banner -loglevel error -y -filter_complex "$2" -ar 48000 -ac 1 "$saida/$1.wav" || { echo "falhou: $1" >&2; exit 1; }; }
# whoosh: ruído rosa filtrado, sobe devagar e cai rápido (pico em ~0,32 s)
gera whoosh "anoisesrc=d=0.5:c=pink:a=0.9:seed=11,bandpass=f=900:width_type=o:w=2.5,highpass=f=180,afade=t=in:d=0.32:curve=exp,afade=t=out:st=0.32:d=0.18:curve=qsin,volume=2"
gera whoosh-curto "anoisesrc=d=0.25:c=pink:a=0.9:seed=5,bandpass=f=1600:width_type=o:w=2,afade=t=in:d=0.14:curve=exp,afade=t=out:st=0.14:d=0.11,volume=2"
# impacto: grave de 55 Hz decaindo + estalo filtrado
gera impacto "aevalsrc='0.9*sin(2*PI*(55+40*exp(-30*t))*t)*exp(-3.5*t)':d=1.0[a];anoisesrc=d=1.0:c=brown:a=0.8:seed=3,lowpass=f=500,aeval='val(0)*exp(-14*t)'[b];[a][b]amix=inputs=2:normalize=0,alimiter=limit=0.9"
# tique: clique agudo curto (contador)
gera tique "aevalsrc='0.6*sin(2*PI*2600*t)*exp(-90*t)':d=0.06"
# clique: interface (seleção)
gera clique "aevalsrc='0.5*sin(2*PI*1800*t)*exp(-120*t)':d=0.07[a];anoisesrc=d=0.07:c=white:a=0.4:seed=9,highpass=f=2500,aeval='val(0)*exp(-150*t)'[b];[a][b]amix=inputs=2:normalize=0"
# pop: bolha com queda de altura (gráfico entra)
gera pop "aevalsrc='0.7*sin(2*PI*(700-1800*t)*t)*exp(-28*t)':d=0.14"
# risco: caneta riscando
gera risco "anoisesrc=d=0.35:c=white:a=0.6:seed=21,bandpass=f=3200:width_type=o:w=1.5,aeval='val(0)*(0.6+0.4*sin(2*PI*28*t))',afade=t=in:d=0.04,afade=t=out:st=0.22:d=0.13"
for f in "$saida"/*.wav; do
  printf '%s  %.2f s\n' "$(basename "$f")" "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")"
done
