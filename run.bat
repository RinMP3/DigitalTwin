@echo off
chcp 65001 > nul
title DigitalTwin by RinMP3

py -3.12 main.py --iterations 50000 %*

echo.
echo [!] Completed.
pause