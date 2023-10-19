@ECHO OFF

ECHO ^>^> [Step 1/3] test local isq-open library

PUSHD playground
python basic.py
python triple_dice.py
python QBE.py
POPD

ECHO.
ECHO.

ECHO ^>^> [Step 2/3] test local isq-open service...

SET PYTHONPATH=%CD%

python modules\qlocal.py
python modules\qcircuit.py
python modules\qbloch.py

python modules\xrand.py
python modules\xcoin.py
python modules\xqkd.py
python modules\xtele.py
python modules\xvqe.py

python services\models\playerdata.py

ECHO.
ECHO.

ECHO ^>^> [Step 3/3] test docker isq service...

CALL isq-run\start.cmd
IF ERRORLEVEL 1 GOTO ERROR

python modules\qcloud.py


:ERROR
