#!/usr/bin/env python3
"""Diagnóstico da placa de vídeo: diz qual placa o computador tem e como o kit vai usá-la.

Uso (rode com o Python do kit, para conferir também o Whisper e o torch):
  Windows: .venv\\Scripts\\python.exe ferramentas\\placa.py
  Mac:     .venv/bin/python ferramentas/placa.py
Só usa a biblioteca padrão; o que faltar (driver, faster-whisper, torch) aparece como aviso.
Regras completas em guias/placa-de-video.md.
"""
import os
import platform
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def nvidia():
    exe = shutil.which("nvidia-smi")
    if not exe:
        return None
    # driver antigo não conhece o campo compute_cap: tenta de novo sem ele
    for campos in ("name,memory.total,driver_version,compute_cap", "name,memory.total,driver_version"):
        try:
            r = subprocess.run([exe, f"--query-gpu={campos}", "--format=csv,noheader,nounits"],
                               capture_output=True, text=True, timeout=15)
        except Exception:
            return None
        if r.returncode == 0 and r.stdout.strip():
            v = [x.strip() for x in r.stdout.strip().splitlines()[0].split(",")]
            cc = v[3] if len(v) > 3 else "?"
            return {"nome": v[0], "vram_gb": round(float(v[1]) / 1024, 1), "driver": v[2], "cc": cc}
    return None


def familia(p):
    n = p["nome"].upper()
    try:
        cc = float(p["cc"])
    except ValueError:
        cc = 0
    if "RTX 50" in n or ("RTX" in n and cc >= 12):
        return "RTX 50xx (Blackwell)"
    if "RTX" in n or cc >= 8:
        return "RTX (20xx a 40xx, ou placa de estação)"
    if "GTX 16" in n:
        return "GTX 16xx (Turing sem núcleos RTX)"
    if re.search(r"GTX 10[5-8]0", n) or ("GTX" in n and cc >= 6):
        return "GTX 10xx (Pascal)"
    return "placa NVIDIA antiga (anterior à GTX 10xx)"


def recomendacao(p):
    fam = familia(p)
    v = p["vram_gb"]
    if fam.startswith("RTX") and v >= 6:
        tipo = "float16"
    else:
        tipo = "int8"
    if fam.startswith("placa NVIDIA antiga"):
        return fam, "processador (--device cpu): placa sem suporte nas bibliotecas atuais", tipo
    if v >= 6:
        modelo = "large-v3"
    elif v >= 4:
        modelo = "large-v3 (int8) ou medium, se faltar memória"
    else:
        modelo = "small ou medium (menos de 4 GB de memória de vídeo)"
    return fam, modelo, tipo


def main():
    print(f"Sistema: {platform.system()} {platform.release()} ({platform.machine()})")
    if platform.system() == "Darwin":
        print("Mac: o kit não usa a placa do Mac para o Whisper nem para a limpeza de voz; roda no processador.")
        print("Chips Apple (M1 em diante) são rápidos o bastante; em vídeo longo, use --modelo medium.")
        return
    p = nvidia()
    if not p:
        print("Nenhuma placa NVIDIA encontrada (ou o driver não está instalado).")
        print("Tudo funciona no processador, só mais devagar. Placa AMD ou Intel: o kit usa o processador.")
        print("Tem NVIDIA? Instale o driver mais recente (nvidia.com/drivers) e rode de novo.")
        return
    fam, modelo, tipo = recomendacao(p)
    print(f"Placa: {p['nome']} | memória de vídeo: {p['vram_gb']} GB | driver: {p['driver']} | compute capability: {p['cc']}")
    if p['cc'] == '?':
        print('Driver antigo: atualize em nvidia.com/drivers antes de usar a placa no kit.')
    print(f"Família: {fam}")
    print(f"Whisper: modelo {modelo}, precisão {tipo}")
    try:
        import ctranslate2

        n = ctranslate2.get_cuda_device_count()
        print(f"faster-whisper enxerga a placa: {'sim' if n else 'NÃO'} ({n})")
        if n:
            from _whisper import escolher_tipo

            print(f"precisão que o kit vai usar: {os.environ.get('KIT_WHISPER_TIPO') or escolher_tipo('cuda')}")
    except Exception as e:
        print(f"faster-whisper: não encontrado neste Python ({type(e).__name__}). Rode com o Python do .venv.")
    try:
        import torch

        ok = torch.cuda.is_available()
        print(f"torch (limpeza de voz) enxerga a placa: {'sim' if ok else 'NÃO'} (torch {torch.__version__}, CUDA {torch.version.cuda})")
    except Exception:
        print("torch: não está neste Python (normal: ele fica em ferramentas/voz/.venv).")


if __name__ == "__main__":
    main()
