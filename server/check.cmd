@ECHO OFF

ECHO ^>^> [Step 1/2] test local isq-open

PUSHD playground

python basic.py
python triple_dice.py
python QBE.py

POPD

ECHO.
ECHO.

ECHO ^>^> [Step 2/2] test docker isq service...

CALL qcloud\start.cmd
IF ERRORLEVEL 1 GOTO ERROR

python qvm\qcloud.py
