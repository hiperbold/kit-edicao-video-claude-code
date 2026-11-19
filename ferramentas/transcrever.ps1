# Transcrição no Windows (faster-whisper, local). Grava ao lado do arquivo: "<nome>.srt" e "<nome> - transcricao.txt".
# Uso: pwsh -File ferramentas\transcrever.ps1 <audio-ou-video> [idioma, padrão pt] [-Python <python.exe>] [-Nomes nomes.txt]
# Qual Python usar (nesta ordem): parâmetro -Python, variável de ambiente KIT_PYTHON, .venv\Scripts\python.exe na raiz do kit.
# Usa a placa NVIDIA se houver; senão o processador (mais lento). Veja INSTALACAO.md.
param(
  [Parameter(Mandatory=$true)][string]$Arquivo,
  [string]$Idioma = 'pt',
  [string]$Python = '',
  [string]$Nomes = ''
)
$ErrorActionPreference = 'Stop'
$raiz = Split-Path $PSScriptRoot -Parent
if (-not $Python) { $Python = $env:KIT_PYTHON }
if (-not $Python) { $Python = Join-Path $raiz '.venv\Scripts\python.exe' }
if (-not (Test-Path -LiteralPath $Python)) {
  throw "Python do Whisper não encontrado ($Python). Crie o .venv conforme o INSTALACAO.md, ou use -Python / a variável KIT_PYTHON."
}
$Arquivo = (Resolve-Path -LiteralPath $Arquivo).Path
$args2 = @((Join-Path $PSScriptRoot 'transcrever.py'), $Arquivo, '--idioma', $Idioma)
if ($Nomes) { $args2 += @('--nomes', $Nomes) }
& $Python @args2
if ($LASTEXITCODE -ne 0) { throw "a transcrição falhou (código $LASTEXITCODE)" }
