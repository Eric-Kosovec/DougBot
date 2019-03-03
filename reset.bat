@echo off

if [%1] == [] EXIT /B

set dougbot-pid=%1

taskkill /f /PID %dougbot-pid%

start cmd /C py.exe run.py
