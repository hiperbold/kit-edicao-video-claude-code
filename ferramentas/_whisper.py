"""Peças comuns ao palavras.py e ao transcrever.py: carregar o faster-whisper e ler o arquivo de nomes.

Arquivo de nomes (nomes.txt, opcional), uma linha por item:
    # linha começando com # é comentário
    Claude                      -> nome certo: entra na dica que o Whisper recebe
    cloud => Claude             -> correção: troca "cloud" por "Claude" na saída (sem diferenciar maiúscula)
    hiper bold|hyperbold => X   -> várias grafias erradas separadas por | (troca só palavra inteira)
O Whisper erra siglas, nomes de marca e de produto: liste aqui os que aparecem nos seus vídeos.
"""
import os
import re
import sys


def preparar_cuda_windows():
    """No Windows, o pip instala as DLLs da NVIDIA dentro do venv; o Python precisa ser avisado."""
    if os.name != "nt":
        return
    base = os.path.join(sys.prefix, "Lib", "site-packages", "nvidia")
    for d in ("cublas", "cuda_runtime", "cuda_nvrtc", "cudnn"):
        p = os.path.join(base, d, "bin")
        if os.path.isdir(p):
            os.add_dll_directory(p)
            os.environ["PATH"] = p + os.pathsep + os.environ.get("PATH", "")


def carregar_modelo(modelo="large-v3", device="auto"):
    """device: auto (placa NVIDIA se houver, senão processador), cuda ou cpu."""
    preparar_cuda_windows()
    from faster_whisper import WhisperModel

    if device == "auto":
        try:
            import ctranslate2

            device = "cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu"
        except Exception:
            device = "cpu"
    tipo = "float16" if device == "cuda" else "int8"
    print(f"modelo {modelo} em {device} ({tipo})", file=sys.stderr)
    return WhisperModel(modelo, device=device, compute_type=tipo, download_root=os.environ.get("HF_HOME"))


def ler_nomes(caminho=None):
    """Devolve (dica, correcoes). Sem arquivo, devolve ('', [])."""
    if caminho is None:
        for c in ("nomes.txt", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "nomes.txt")):
            if os.path.isfile(c):
                caminho = c
                break
    if not caminho or not os.path.isfile(caminho):
        return "", []
    dica, correcoes = [], []
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue
            if "=>" in linha:
                erradas, certo = (x.strip() for x in linha.split("=>", 1))
                grafias = [e.strip() for e in erradas.split("|") if e.strip()]
                if grafias and certo:
                    rx = re.compile(r"\b(?:" + "|".join(re.escape(g) for g in grafias) + r")\b", re.I)
                    correcoes.append((rx, certo))
                    dica.append(certo)
            else:
                dica.append(linha)
    return ", ".join(dict.fromkeys(dica)), correcoes


def corrigir(texto, correcoes):
    for rx, certo in correcoes:
        texto = rx.sub(certo, texto)
    return texto
