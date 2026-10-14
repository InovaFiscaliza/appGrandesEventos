@echo off
setlocal
title Testes completos - AppGrandesEventos

echo Iniciando a suite completa de testes.
echo Podman deve estar em execucao.
echo.

"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\testar_todas_camadas.ps1"
set "RESULTADO=%ERRORLEVEL%"

echo.
if "%RESULTADO%"=="0" (
    echo Todos os testes passaram.
) else (
    echo A suite terminou com falhas. Consulte as mensagens acima.
)
echo.
pause
exit /b %RESULTADO%