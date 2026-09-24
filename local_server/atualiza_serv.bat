@echo off
setlocal EnableExtensions DisableDelayedExpansion
title Atualizar servidor - AppGrandesEventos

REM ===== EDITE OS PARAMETROS ABAIXO =====
REM IP ou nome do computador de destino.
set "SERVIDOR_IP=192.168.1.11"
REM Usuario Windows que executa o Podman Desktop no servidor.
set "USUARIO_SERVIDOR=andre"
REM Porta da aplicacao web no servidor.
set "PORTA_WEB=8501"
REM Chave privada SSH deste computador. A chave publica deve estar no servidor.
set "CHAVE_SSH=%USERPROFILE%\.ssh\id_ed25519_appgrandeseventos"
REM Pasta onde cada execucao salva seu log completo.
set "PASTA_LOG=%~dp0logs"
REM ===== FIM DOS PARAMETROS =====

REM O auxiliar registra a saida e os erros sem esconder as mensagens da janela.
REM O instalador remoto para e recria os dois containers, preservando o volume.
REM Os parametros sao lidos do ambiente para preservar espacos nos caminhos.
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "%~dp0atualizar-com-log.ps1"
set "RESULTADO=%ERRORLEVEL%"

echo.
if "%RESULTADO%"=="0" (
    echo Atualizacao concluida com sucesso.
) else (
    echo A atualizacao falhou. Consulte o log indicado acima.
)
echo.
pause
exit /b %RESULTADO%
