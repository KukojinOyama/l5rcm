@echo off
cd ..

REM DELETE PREVIOUS BUILD
del /S /F /Q .\build\*.*
del /S /F /Q .\dist\*.*

REM UPDATE QRC
REM echo UPDATE RESOURCES
REM pyside-rcc widgets/toolbar.qrc -o widgets/toolbar_rc.py

python setup.py py2exe

xcopy /Y /E /C /I /R share\* dist\share\
xcopy /Y /E /C /I /R tools\* dist\tools\

copy LICENSE.GPL3 dist\
REM database is placed under version control
REM python l5rdb.py -c -i dist/share/l5rcm/l5rdb.sqlite

cd windows