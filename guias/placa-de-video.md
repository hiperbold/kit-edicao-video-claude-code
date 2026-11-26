# Placa de vídeo (Windows)

No Windows, a placa NVIDIA deixa a transcrição e a limpeza de voz muito mais rápidas. Sem ela, tudo funciona no processador, só mais devagar. No Mac o kit não usa a placa de vídeo: Whisper e limpeza de voz rodam no processador.

**Regra para o Claude:** no Windows, antes da primeira transcrição ou limpeza de voz, rode `.venv\Scripts\python.exe ferramentas\placa.py`. Siga a recomendação dele e a tabela abaixo. Diga ao usuário em uma linha qual placa ele tem e o que isso muda.

## 1. Descobrir qual é a placa

- Pelo kit: `.venv\Scripts\python.exe ferramentas\placa.py`. Mostra o nome, a memória de vídeo, o driver e a família, e diz se o Whisper e o torch enxergam a placa.
- Sem o kit: `nvidia-smi` no PowerShell, ou Gerenciador de Tarefas > Desempenho > GPU.
- Se o `nvidia-smi` não existir, ou o driver não está instalado, ou a placa não é NVIDIA. Placa AMD ou Intel (Arc, Iris) não acelera o Whisper nem o torch deste kit: o kit usa o processador.

## 2. O que cada família usa

| Família | Exemplos | Whisper (faster-whisper) | Limpeza de voz (torch) | Codificar no ffmpeg (NVENC) |
|---|---|---|---|---|
| **RTX 50xx** (Blackwell) | 5060, 5070, 5080, 5090 | `large-v3`, `float16` | torch com **CUDA 12.8 ou mais novo** (com aviso "sm_120 is not compatible", o CUDA escolhido é antigo demais) | `h264_nvenc`, `hevc_nvenc`, `av1_nvenc` |
| **RTX 20xx a 40xx** | 2060, 3060, 3070, 4060, 4060 Ti, 4070, 4090 | `large-v3`, `float16` | torch com o CUDA mais novo da lista do pytorch.org | `h264_nvenc`, `hevc_nvenc` (40xx também `av1_nvenc`) |
| **GTX 16xx** (Turing sem núcleos RTX) | 1630, 1650, 1660, 1660 Super, 1660 Ti | `large-v3` em `int8` (o kit escolhe sozinho, por segurança: há relatos de problema com `float16` nessas placas) | funciona; se der erro ou som estranho, use o processador | `h264_nvenc` (1650 de primeira geração tem NVENC mais antigo, qualidade menor) |
| **GTX 10xx** (Pascal) | 1050, 1050 Ti, 1060, 1070, 1080 | `int8` (o kit escolhe sozinho); com 2 a 3 GB de memória, `--modelo medium` ou `small` | torch com o CUDA mais novo da lista; se aparecer aviso "sm_61 is not compatible", escolha uma opção de CUDA mais antiga (12.6 ou anterior) ou use o processador | `h264_nvenc` |
| **Anteriores** (GTX 9xx, 7xx) | 960, 970, 980 | processador (`--device cpu`) | processador | `h264_nvenc` funciona, mas não compensa |

Memória de vídeo (o `placa.py` mostra):
- **6 GB ou mais:** `large-v3` sem preocupação.
- **4 a 5 GB:** `large-v3` em `int8`. Se der "out of memory", `--modelo medium`.
- **Menos de 4 GB:** `--modelo small` ou `medium`, ou o processador.
- **Uma tarefa pesada por vez** na placa: transcrição, limpeza de voz e render do HyperFrames juntos estouram a memória de placas de 8 GB ou menos.

## 3. Instalar para a placa

1. **Driver:** o mais recente em nvidia.com/drivers (Game Ready ou Studio, tanto faz). Reinicie o computador.
2. **Whisper:** no passo 4 do `INSTALACAO.md`, instale `nvidia-cublas-cu12` e `nvidia-cudnn-cu12` e rode o `placa.py`. Tem de aparecer "faster-whisper enxerga a placa: sim". Se não, atualize o driver; se continuar, use `-Device cpu`.
3. **Limpeza de voz (torch):** no passo 6 do `INSTALACAO.md`, escolha no pytorch.org o CUDA certo para a família (tabela acima). Confira com `ferramentas\voz\.venv\Scripts\python.exe -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"`. Tem de sair `True` e o nome da placa. Se sair aviso de "sm_XX is not compatible", a versão do CUDA não serve para a placa: troque conforme a tabela.

## 4. Forçar uma escolha

- Precisão do Whisper: variável de ambiente `KIT_WHISPER_TIPO` (`int8`, `int8_float16`, `float16`, `float32`). Ex.: `$env:KIT_WHISPER_TIPO="int8"` antes do comando.
- Sem placa: `--device cpu` no `transcrever.py` ou no `palavras.py`.
- Modelo menor: `--modelo medium` ou `--modelo small`.

## 5. Problemas comuns

- **"em cpu" mesmo com NVIDIA:** driver desatualizado, ou faltou o `pip install nvidia-cublas-cu12 nvidia-cudnn-cu12` do passo 4.
- **"out of memory" ou "CUDA failed":** feche o que usa a placa (jogos, outro render) e tente `--modelo medium`.
- **Transcrição com texto repetido, vazio ou sem sentido numa GTX:** `$env:KIT_WHISPER_TIPO="int8"` (ou `float32`) e transcreva de novo.
- **Notebook com duas placas (Intel + NVIDIA):** em Configurações > Sistema > Tela > Gráficos, ponha o `python.exe` do `.venv` em "Alto desempenho".
