for /r %%i in (*.xml) do xml fo --indent-spaces 2 --encode utf-8 "%%i" > tmp.xml && copy tmp.xml "%%i"

