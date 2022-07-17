@echo off
:main
cls
q server.py objects\*.py routes\*.py common\*.py
rem python -m cProfile -s ncalls server.py | list /s
rem hypercorn server.py
pause
eliot-tree server_0.log | list /s
#if errorlevel 1 goto end
goto main
:end
