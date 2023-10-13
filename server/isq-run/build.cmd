@ECHO OFF

SET NAME=kahsolt/isq-run

ECHO ^>^> [Step 1/2] build the image
docker build -t %NAME% .
IF ERRORLEVEL 1 GOTO ERROR

ECHO.
ECHO.

ECHO ^>^> [Step 2/2] push the image to hub
docker push %NAME%
IF ERRORLEVEL 1 GOTO ERROR

:ERROR
