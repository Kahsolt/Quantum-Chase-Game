@ECHO OFF

IF EXIST bullet-samples.zip GOTO skip_bullet_samples
wget -nc https://www.panda3d.org/download/noversion/bullet-samples.zip
:skip_bullet_samples

IF EXIST panda3d-1.10.13-samples.zip GOTO skip_samples
wget -nc https://www.panda3d.org/download/panda3d-1.10.13/panda3d-1.10.13-samples.zip
:skip_samples
