@REM update the symbol link to server project
@ECHO OFF

PUSHD modules
DEL playerdata.py
MKLINK playerdata.py ..\..\server\services\playerdata.py
POPD
