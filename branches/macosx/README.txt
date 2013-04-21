GETTING THE SOURCES

clone the repository
svn checkout http://l5rcm.googlecode.com/svn/trunk/ l5rcm-read-only

or you can clone a release tag instead
svn checkout http://l5rcm.googlecode.com/svn/tags/v3.7 l5rcm-3-7

GETTING THE DEPENDENCIES

* python2       >= 2.6   ( 2.7.3 recommended )
* python-pyside >= 1.1.0 ( 1.1.1 if l5rcm version < 3.7, 1.1.2 recommended with 3.7 )
* pdftk                  ( needed for pdf export )

RUN

python l5rcm.py
