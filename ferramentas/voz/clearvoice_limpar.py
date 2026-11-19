#!/usr/bin/env python3
"""Limpa voz com o ClearerVoice-Studio (MossFormer2, 48 kHz), 100% local.
Uso: <python do ferramentas/voz/.venv> ferramentas/voz/clearvoice_limpar.py entrada.wav saida.wav [modelo]
(Windows: ferramentas\\voz\\.venv\\Scripts\\python.exe; Mac/Linux: ferramentas/voz/.venv/bin/python)
Modelos: MossFormer2_SE_48K (padrão), FRCRN_SE_16K, MossFormerGAN_SE_16K.
Na primeira execução baixa o modelo (211 MB) para ~/.cache/clearvoice/checkpoints, fora do repositório.
Cadeia usada depois da limpeza: EQ suave sem reforço de agudo (corte em 3 kHz e 6,5 kHz, passa-baixa 11 kHz, de-esser) e loudnorm em duas passadas.
"""
import os
import sys

from clearvoice import ClearVoice

entrada, saida = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
modelo = sys.argv[3] if len(sys.argv) > 3 else "MossFormer2_SE_48K"
cache = os.path.expanduser("~/.cache/clearvoice")
os.makedirs(cache, exist_ok=True)
os.chdir(cache)  # o ClearVoice grava os checkpoints na pasta atual
cv = ClearVoice(task="speech_enhancement", model_names=[modelo])
resultado = cv(input_path=entrada, online_write=False)
cv.write(resultado, output_path=saida)
print(f"ok: {saida} ({modelo})")
