#!/usr/bin/env bash
# Transcrição no Mac/Linux (faster-whisper, local). Grava ao lado do arquivo: "<nome>.srt" e "<nome> - transcricao.txt".
# Uso: ferramentas/transcrever.sh <audio-ou-video> [idioma, padrão pt] [arquivo-de-nomes]
# Qual Python usar (nesta ordem): variável de ambiente KIT_PYTHON, .venv/bin/python na raiz do kit.
# Modelo e processador opcionais pelas variáveis KIT_WHISPER_MODELO (ex.: medium) e KIT_WHISPER_DEVICE (auto, cuda, cpu).
# Usa a placa NVIDIA se houver; senão o processador (mais lento). Veja guias/placa-de-video.md.
set -euo pipefail
raiz="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
py="${KIT_PYTHON:-$raiz/.venv/bin/python}"
if [ ! -x "$py" ]; then
  echo "Python do Whisper não encontrado ($py). Crie o .venv conforme o INSTALACAO.md ou defina KIT_PYTHON." >&2
  exit 1
fi
[ $# -ge 1 ] || { echo "uso: $0 <audio-ou-video> [idioma] [arquivo-de-nomes]" >&2; exit 1; }
args=("$1" --idioma "${2:-pt}")
[ -n "${3:-}" ] && args+=(--nomes "$3")
[ -n "${KIT_WHISPER_MODELO:-}" ] && args+=(--modelo "$KIT_WHISPER_MODELO")
[ -n "${KIT_WHISPER_DEVICE:-}" ] && args+=(--device "$KIT_WHISPER_DEVICE")
exec "$py" "$(dirname "${BASH_SOURCE[0]}")/transcrever.py" "${args[@]}"
