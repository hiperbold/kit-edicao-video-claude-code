---
name: video-cut
description: >
  Junta e LIMPA partes ou takes brutos de um vídeo falando para a câmera (talking-head) em um corte
  único e limpo, 100% local (Whisper + FFmpeg). Use quando o usuário tem um vídeo em PARTES
  (parte 1/2/3, takes brutos) e quer cortar, juntar e remover gaguejos, takes duplicados e
  pausas longas. Faz transcrição palavra por palavra, corte em FRONTEIRA EXATA DE PALAVRA, remoção de
  takes repetidos, junção com transição (zoom-punch ou crossfade), correção de cor opcional e
  VERIFICAÇÃO por nova transcrição. Gatilhos: "juntar as partes", "cortar e juntar", "remover
  silêncios", "tirar take duplicado", "corte exato", "limpar o vídeo bruto", "montar o corte".
---

# video-cut: corte e junção local (Whisper + FFmpeg)

Decide os cortes a partir da transcrição e executa com FFmpeg, tudo na sua máquina. O corte é por
**palavra**, não por silêncio, o que evita os defeitos que o corte automático por silêncio não pega.

## Princípios

1. **Corte SEMPRE em fronteira de palavra, nunca no meio.** Cortar só por `silencedetect` corta no
   meio de palavras arrastadas e deixa fragmentos ("...oblema", "fo-foi"). Use o tempo de cada
   palavra (`ferramentas/palavras.py`) para achar o início e o fim exatos.
2. **Takes brutos têm repetições.** Quem grava costuma repetir a frase (take A, take B), e uma parte
   costuma repetir o começo da próxima. Identifique e **mantenha um take só** (em geral o mais
   completo), descartando o outro e a pausa entre eles.
3. **Verifique por nova transcrição.** Depois de cortar, transcreva o resultado e leia: nenhuma
   palavra cortada, nenhum trecho duplicado. Repetição de propósito do roteiro ("o problema... o
   problema...") não é erro de corte.
4. **Uma faixa só.** Um clipe por vez, com o áudio do próprio clipe. B-roll e gráficos são outra etapa
   (composição no HyperFrames).

## Pré-requisitos

- **FFmpeg e FFprobe** no PATH.
- **Python do kit** com o `faster-whisper` (veja `INSTALACAO.md`): `.venv\Scripts\python.exe` no Windows,
  `.venv/bin/python` no Mac. Daqui para frente, `python` quer dizer esse.
- `ferramentas/palavras.py` (tempo de cada palavra) e `ferramentas/transcrever.ps1` ou `.sh` (SRT e texto).
- Opcional: um `nomes.txt` com nomes de marca, produtos e siglas que o Whisper costuma errar.

## Fluxo

### 1. Sondar
```bash
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,codec_name \
  -show_entries format=duration -of default=noprint_wrappers=1 PARTE.mov
```
Confirme que as partes têm as mesmas especificações (facilita juntar). Anote largura, altura, qps e duração.

### 2. Transcrever e entender o contexto
Transcreva CADA parte (`ferramentas/transcrever.ps1 PARTE.mov`, ou `ferramentas/transcrever.sh PARTE.mov`).
Leia os SRTs e monte o **roteiro real**. Marque onde uma parte repete a outra, as frases ditas duas
vezes (take A e B) e a chamada final (costuma vir gravada em dobro).

### 3. Mapear pausas
```bash
ffmpeg -i PARTE.mov -af silencedetect=n=-30dB:d=0.6 -f null - 2>&1 | grep silence
```
Os silêncios mostram as pausas longas e os limites entre takes.

### 4. Decidir os cortes (editorial)
Defina a lista de **trechos a MANTER** (arquivo de origem, início, fim e o que contém). Descarte caudas
repetidas, takes duplicados e pausas acima de cerca de 1 s. Para um corte bem apertado, corte também
pausas curtas, mas nunca à custa de cortar uma palavra.

### 5. Precisão por palavra (CRÍTICO)
Gere o tempo de cada palavra de cada parte:
```bash
python ferramentas/palavras.py PARTE.mov trabalho/parte1-palavras.json
```
Para cada fronteira de corte, ache no JSON o **fim exato da última palavra** do trecho e o **início exato
da primeira palavra** do próximo. Corte de 0,02 a 0,05 s depois do fim de uma palavra e no começo da
seguinte. Isso evita palavra cortada e gaguejo.

### 6. Montar com transição
Gere cada trecho recodificado (mesmas especificações) e junte. O **zoom-punch** (entra a cerca de
1,10x e assenta em 1,0 em 0,22 s) disfarça o corte e a troca de cena:
```bash
PUNCH="crop=w='iw*(0.90+0.10*min(t/0.22,1))':h='ih*(0.90+0.10*min(t/0.22,1))':x='(iw-ow)/2':y='(ih-oh)/2'"
TAIL="scale=W:H,setsar=1,fps=FPS,format=yuv420p"
# por trecho (o primeiro normalmente sem punch):
ffmpeg -y -ss INI -t DUR -i PARTE.mov -vf "$PUNCH,$TAIL" -c:v libx264 -crf 18 -g FPS -keyint_min FPS \
  -c:a aac -ar 48000 -ac 2 -movflags +faststart trecho1.mp4
# juntar (todos com as mesmas especificações):
printf "file 'trecho1.mp4'\nfile 'trecho2.mp4'\n" > lista.txt
ffmpeg -y -f concat -safe 0 -i lista.txt -c copy saida.mp4   # recodifique se -c copy falhar
```
Troque `W`, `H` e `FPS` pelos valores do vídeo (para Reels: 1080, 1920, 30). Alternativa de transição:
`xfade` (precisa de sobreposição; cuidado para não sobrepor fala). Mantenha `-g FPS -keyint_min FPS`
(quadros-chave densos): assim o vídeo já serve de entrada para o HyperFrames. Receitas prontas em
`ferramentas/ffmpeg-receitas.md`.

### 7. (Opcional) Correção de cor
Se as partes foram gravadas em locais ou luz diferentes, acerte o balanço de branco de cada parte
(`colorbalance`, `eq`) usando uma como referência, e aplique um visual único (LUT) por cima, no mesmo
`-vf` de cada trecho. Para escolher o visual, gere tiras comparativas (original e variações) com um
quadro de cada parte.

### 8. VERIFICAR (obrigatório)
```bash
ferramentas/transcrever.sh saida.mp4        # ou transcrever.ps1 no Windows
```
Leia o SRT: alguma palavra cortada? Algum trecho duplicado? Se sim, volte ao passo 5 e ajuste a
fronteira. Só entregue depois que a leitura passar limpa.

### 9. Entregar
Nomeie claro (`<assunto>-corte-v1.mp4`). Se o vídeo segue para gráficos e legendas, o arquivo (com
quadros-chave densos) é a entrada do HyperFrames; refaça o áudio no fim, se a composição sair muda.

## Notas

- Fale com o usuário como editor (cortes, takes, ritmo), não como programador.
- Este fluxo cobre juntar partes, escolher takes e limpar pausas. Não exporta projeto para Premiere ou
  DaVinci: entrega um MP4 pronto para a composição.
