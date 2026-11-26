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


def info_placa():
    """Nome e memória (GB) da primeira placa NVIDIA, pelo nvidia-smi (vem com o driver). ("", 0) se não houver."""
    import shutil
    import subprocess

    exe = shutil.which("nvidia-smi")
    if not exe:
        return "", 0.0
    try:
        r = subprocess.run([exe, "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=10)
        linha = r.stdout.strip().splitlines()[0] if r.returncode == 0 and r.stdout.strip() else ""
        nome, _, mem = linha.rpartition(",")
        return nome.strip(), float(mem) / 1024
    except Exception:
        return "", 0.0


def escolher_tipo(device):
    """Precisão do modelo conforme a placa (detalhes em guias/placa-de-video.md).
    RTX (20xx em diante) e placas de estação (A, Quadro RTX) com 6 GB ou mais: float16.
    Placa GTX (10xx, 16xx) ou com menos de 6 GB de memória: int8 (mais leve e mais seguro nessas placas).
    Processador: int8. Para forçar outro, defina KIT_WHISPER_TIPO (ex.: int8, float16, int8_float16, float32)."""
    if device != "cuda":
        return "int8"
    nome, mem = info_placa()
    if "GTX" in nome.upper() or 0 < mem < 6:
        return "int8"
    try:
        import ctranslate2

        aceitos = ctranslate2.get_supported_compute_types("cuda")
    except Exception:
        return "int8"
    for t in ("float16", "int8_float16", "int8"):
        if t in aceitos:
            return t
    return "float32"


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
    tipo = os.environ.get("KIT_WHISPER_TIPO") or escolher_tipo(device)
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
