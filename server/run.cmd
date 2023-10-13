@ECHO OFF

REM start cloud service `run-isq` on docker
CALL isq-run\start.cmd
IF ERRORLEVEL 1 GOTO ERROR

REM start local isq & game server
python app.py

:ERROR
