@ECHO OFF

REM start clound isq-server on docker
CALL qcloud\start.cmd
IF ERRORLEVEL 1 GOTO ERROR

REM start local isq-server
python app.py

:ERROR
