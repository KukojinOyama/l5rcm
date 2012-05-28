@echo off
cd ..

REM DELETE PREVIOUS BUILD
del /S /F /Q .\build\*.*
del /S /F /Q .\dist\*.*

python setup.py py2exe

xcopy /Y /E /C /I /R share\* dist\share\
copy LICENSE.GPL3 dist\
python l5rdb.py -c -i dist/share/l5rcm/l5rdb.sqlite

cd windows