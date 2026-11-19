# Receitas de ffmpeg do kit

Comandos prontos para as tarefas que se repetem na edição de vídeo vertical.

- Parte vem do repositório [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) (licença MIT, Copyright (c) 2026 kajisho5), adaptada. A skill não foi instalada: ela proíbe ffmpeg direto e não cobre punch-in, NVIDIA nem efeito sonoro em tempo exato. A parte que faltava foi escrita aqui.
- Testado no Windows com ffmpeg 8.1 (gyan full) em 06/11/2026: cada receita marcada "testado" rodou e foi conferida com ffprobe ou ebur128.
- Texto na tela não sai daqui: vai sempre pela composição do HyperFrames.
- Caminhos de exemplo são relativos à pasta do vídeo (`videos/<pasta>/`).

## 1. Conferir a entrada antes de tudo

```
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,avg_frame_rate,pix_fmt,color_transfer,color_primaries:stream_side_data=rotation -of default=nw=1 bruto/<arquivo>
```

- `color_transfer` = `arib-std-b67` (HLG) ou `smpte2084` (PQ): é HDR, ver seção 3.
- `r_frame_rate` diferente de `avg_frame_rate`: taxa variável (celular). Todo recorte reencoda com `fps=30` no filtro, nunca `-c copy`.
- `rotation` -90 ou 90: o ffmpeg já gira sozinho ao reencodar.

## 2. Cortar em fronteira de palavra

- Nunca `-c copy` para cortar: o corte cai no quadro-chave anterior e começa num quadro congelado ou errado (pegadinha do ffmpeg-skill, `references/gotchas.md`). Sempre `trim`/`atrim` com reencode.
- Tempos de palavra: `ferramentas/palavras.py`. Margem: começar 0,05 s antes da palavra, terminar 0,08 s depois, sem invadir a palavra vizinha.
- Microfade de 20 a 30 ms em cada emenda de áudio para não estalar.

```
[0:v]trim=18.45:30.99,setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos,fps=30[v0];
[0:a]atrim=18.45:30.99,asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st=12.51:d=0.03[a0];
... um par por trecho ...
[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]
```

Grafo longo vai num arquivo e entra com `-filter_complex_script grafo.txt`.

## 3. HDR do iPhone para SDR (testado)

Na placa (libplacebo, Vulkan):

```
ffmpeg -init_hw_device vulkan -i bruto/<arquivo> -vf "libplacebo=tonemapping=bt.2390:colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv:format=yuv420p" -c:v libx264 -crf 17 trabalho/sdr.mp4
```

No processador (cadeia do ffmpeg-skill, `scripts/color.py:187`; a ordem importa):

```
-vf "zscale=tin=arib-std-b67:pin=bt2020:min=bt2020nc:rin=tv:t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=mobius:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p"
```

- `tin` é o `color_transfer` do ffprobe (`arib-std-b67` para HLG, `smpte2084` para PQ).
- Se o ffprobe mostrar `unknown` no transfer ou nas primárias, o zscale falha com "no path between colorspaces" mesmo com `tin`/`pin` escritos (testado em 06/11/2026). Etiquetar antes, no começo do mesmo filtro: `setparams=color_primaries=bt2020:color_trc=arib-std-b67:colorspace=bt2020nc:range=tv,` e então a cadeia acima.
- Nunca só trocar a etiqueta para bt709 em pixels bt2020: a imagem fica lavada.
- Vídeo bt2020 sem HDR (raro): só conversão de gama, sem `tonemap`, senão o branco escurece.
- Conferir um quadro antes do vídeo inteiro.

## 4. Punch-in e zoom (testado)

Corte com mudança de enquadramento (esconde o pulo do jump cut). Zoom fixo `z` por trecho:

```
scale=round(1080*z/2)*2:round(1920*z/2)*2:flags=lanczos,crop=1080:1920
```

Com `z` de 1.07 a 1.12. Se o rosto não estiver no centro, deslocar o crop: `crop=1080:1920:x:y`.

Zoom lento contínuo (de 1,00 a 1,06 ao longo do trecho) é melhor feito no HyperFrames (escala do `<video>` animada no GSAP), porque fica editável e sem serrilhado. No ffmpeg, só se for preciso:

```
scale=2160:3840,zoompan=z='1+0.06*on/(30*DUR)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30
```

(`DUR` = duração do trecho em segundos; escalar antes evita tremor, como o ffmpeg-skill faz em `scripts/insert.py:92`.)

## 5. Transições entre trechos (testado)

`xfade` para imagem e `acrossfade` para som, encadeados. `offset` = soma das durações anteriores menos a duração da transição acumulada (receita do ffmpeg-skill, `scripts/join.py:773`):

```
[v0][v1]xfade=transition=slideleft:duration=0.3:offset=<dur0-0.3>[vx1];
[a0][a1]acrossfade=d=0.3:c1=tri:c2=tri[ax1]
```

Tipos úteis: `fade`, `fadeblack`, `fadewhite`, `slideleft`/`slideright`/`slideup`, `smoothleft`, `wipeleft`, `circleopen`, `radial`, `zoomin`, `hblur`, `pixelize`, `squeezev`.

- Os trechos precisam do mesmo tamanho, qps e formato de pixel.
- Em depoimento a transição come fala: usar só entre blocos (troca de assunto), com 0,2 a 0,35 s. Transição elaborada (whip com desfoque, máscara, flash) vai no HyperFrames.

## 6. Trilha por baixo da voz, abaixando sozinha (testado)

Receita do ffmpeg-skill (`scripts/audio.py:349`), com os valores que usamos (trilha cerca de 20 dB abaixo da voz):

```
ffmpeg -i voz.wav -i trilha.wav -filter_complex "
[1:a]volume=-20dB,atrim=0:<dur>,afade=t=out:st=<dur-1.5>:d=1.5[music];
[0:a]asplit=2[voz][sc];
[music][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400:makeup=1[ducked];
[voz][ducked]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[mix]" -map "[mix]" mix.wav
```

- `normalize=0` no `amix` sempre: sem ele o amix corta o volume pela metade.
- `release` de 300 a 500 ms: a trilha volta suave entre as frases.

## 7. Efeitos sonoros em tempo exato (testado)

Cada efeito entra com `adelay` em milissegundos (o tempo vem da palavra em `corte.json` ou do corte), e é somado sem compressão (o efeito não abaixa com a voz, para não sair do quadro):

```
ffmpeg -i mix.wav -i whoosh.wav -i pop.wav -filter_complex "
[1:a]volume=-8dB,adelay=12550:all=1[s1];
[2:a]volume=-10dB,adelay=19310:all=1[s2];
[0:a][s1][s2]amix=inputs=3:duration=first:normalize=0[out]" -map "[out]" final.wav
```

- Whoosh de transição começa 0,1 a 0,15 s antes do corte (o pico cai no corte).
- Pop ou clique de gráfico: no quadro em que o gráfico entra.
- Impacto em palavra-chave: no início da palavra.
- No HyperFrames o mesmo se faz com um `<audio>` por efeito com `data-start`: preferir lá quando o efeito acompanha um gráfico da composição.

## 8. Volume final em -14 LUFS, duas passadas (testado)

Receita do ffmpeg-skill (`scripts/loudness.py`). Passada 1 mede:

```
ffmpeg -i entrada.wav -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null -
```

Passada 2 aplica com os números medidos, em modo linear (não muda a dinâmica):

```
-af loudnorm=I=-14:TP=-1:LRA=11:measured_I=<input_i>:measured_TP=<input_tp>:measured_LRA=<input_lra>:measured_thresh=<input_thresh>:offset=<target_offset>:linear=true
```

- Se o pico medido estiver alto demais, o loudnorm desiste do modo linear e comprime: baixar o volume antes (`volume=-3dB,`) e medir de novo.
- O AAC acrescenta pico ao codificar: medir de novo o arquivo final (`ebur128=peak=true`); se o pico passar de -1 dBTP, refazer com `TP=-1.5` ou menos. No teste de 06/11/2026, `TP=-1` saiu -0,8 dBTP depois do AAC: usar `TP=-1.5` direto na entrega.
- Ler o JSON da passada 1 no PowerShell: pegar o trecho entre o último `{` e o `}` seguinte da saída (depois dele o ffmpeg ainda escreve linhas).
- Não normalizar trecho que é só ambiente ou silêncio (-40 LUFS ou menos): sobe o ruído, não o conteúdo.

## 9. Codificar na placa NVIDIA (testado)

Para intermediário rápido (cortes, testes):

```
-c:v h264_nvenc -preset p5 -cq 19 -b:v 0 -pix_fmt yuv420p
```

Entrega final continua em `libx264 -crf 17` (melhor qualidade por tamanho). O HyperFrames já usa a placa no render.

## 10. Quadros e folhas para conferir

```
ffmpeg -i entrada.mp4 -vf "fps=1/5,scale=270:-1,tile=6x4" -frames:v 1 folha.jpg
```

Cortes de cena: `-vf "select='gt(scene,0.25)',showinfo" -f null -` (o ffmpeg-skill usa `scdet=threshold=8`, que dá o mesmo).

## Pegadinhas (do ffmpeg-skill, `references/gotchas.md`)

- `-c copy` para cortar começa em quadro errado ou congelado.
- Vídeo de celular com taxa variável: sempre reencodar com `fps` fixo.
- HDR passado por caminho SDR sem conversão fica lavado.
- Volume "normalizado" ainda pode estourar: conferir o pico, não só o LUFS.
- Legenda queimada antes de recortar ou redimensionar sai do lugar ou fica borrada (no nosso fluxo a legenda é do HyperFrames, depois do corte).
- Instagram e TikTok cobrem o quinto de baixo e a coluna da direita: área segura no `AGENTS.md`.
