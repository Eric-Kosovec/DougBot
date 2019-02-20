@echo off

if [%1] == [] EXIT /B

set dougbot-pid=%1
echo %dougbot-pid%

taskkill /f /PID %dougbot-pid%

start cmd /k python run.py
