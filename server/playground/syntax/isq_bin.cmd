@ECHO OFF

SET IN=.\isq_bin.isq
SET OUT=.\isq_bin.so

isqc compile %IN% -O %OUT%
isqc simulate %OUT% --shots 100 --debug

isqc run %IN% --shots 1000 --debug
