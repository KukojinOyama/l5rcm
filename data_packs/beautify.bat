for /r %%i in (*.xml) do xml fo --indent-spaces 2 --encode utf-8 "%%i" > "%%i"
