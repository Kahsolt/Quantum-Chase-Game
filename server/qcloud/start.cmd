@ECHO OFF

SET NAME=isq-run
SET IMAGE=kahsolt/isq-run

docker ps -a --filter name=%NAME% | FINDSTR /I "%NAME%" > NUL

REM container already exists
IF %ERRORLEVEL% EQU 0 (
  docker start %NAME%
) else (
  docker run --name %NAME% -p 5001:5001 -d %IMAGE%
)
