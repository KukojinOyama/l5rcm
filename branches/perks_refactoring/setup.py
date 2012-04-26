from distutils.core import setup
import py2exe

setup(
    windows = [
        {
            "script": "l5rcm.py",
            "icon_resources": [(0, "windows/l5rcm.ico")]
        }
    ],
    options={"py2exe": {"includes": ["PySide.QtGui"]}}
    )
