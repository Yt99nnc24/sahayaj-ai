@echo off
setlocal
cd /d "%~dp0"
echo One-time LOCAL model setup. Internet is needed only for this download.
echo Default model qwen2.5:1.5b is approximately 986 MB plus Ollama runtime.
echo No API key, login, subscription or cloud model is used.
where ollama >nul 2>nul
if errorlevel 1 (
  echo Install Ollama for Windows from https://ollama.com/download/windows
  echo Then open a new terminal and run this file again.
  pause
  exit /b 1
)
echo Quit Ollama from its tray icon before continuing, so cloud-disable settings take effect.
echo Start Ollama in a separate CMD window with these two commands:
echo set "OLLAMA_NO_CLOUD=1"
echo ollama serve
echo Leave that window running, then return here.
pause
set "OLLAMA_NO_CLOUD=1"
ollama pull qwen2.5:1.5b
if errorlevel 1 (
  echo Download failed. Check that Ollama is running and internet is available.
  pause
  exit /b 1
)
echo Model downloaded. You can now disconnect internet and run start-demo.cmd.
echo Keep Ollama running while using the local model.
pause
