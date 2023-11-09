@REM update the symbol link to server project
@ECHO OFF

PUSHD modules
IF EXIST shared RMDIR shared
MKLINK /J shared ..\..\server\services\shared
POPD
