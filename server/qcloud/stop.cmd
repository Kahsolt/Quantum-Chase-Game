@ECHO OFF

SET NAME=isq-run
SET IMAGE=kahsolt/isq-run

docker ps --filter name=%NAME% | FINDSTR /I "%NAME%" > NUL

REM ignore if container not exists and running
IF %ERRORLEVEL% EQU 1 GOTO END

docker stop %NAME%

:END
