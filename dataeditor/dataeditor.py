# -*- coding: utf-8 -*-

import sys
import os
from PySide import QtCore, QtGui
from layouts import animatedvboxlayout

class DataSideBar(QtGui.QScrollArea):
    def __init__(self, parent = None):
        super(DataSideBar, self).__init__(parent)
        self.build_ui()

    def build_ui(self):
        self.setSizePolicy( QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding )
        palette = self.palette()
        palette.setColor( QtGui.QPalette.Window    , QtGui.QColor("#666")  )
        palette.setColor( QtGui.QPalette.WindowText, QtGui.QColor("#ffe")  )
        self.setPalette(palette)
        self.fr   = QtGui.QFrame()
        #self.vbox = animatedvboxlayout.AnimatedVBoxLayout(self.fr)
        self.vbox = QtGui.QVBoxLayout(self.fr)
        self.setWidget(self.fr)
        self.setWidgetResizable(True)

    def sizeHint(self):
        if self.parent() is not None:
            return QtCore.QSize( self.parent().width()*0.25, self.parent().height() )

    def frame_layout(self):
        return self.vbox

class LightCentralWidget(QtGui.QFrame):
    def __init__(self, parent = None):
        super(LightCentralWidget, self).__init__(parent)
        self.setSizePolicy( QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding )
        palette = self.palette()
        palette.setColor( QtGui.QPalette.Window, QtGui.QColor("#EEE")  )
        self.setPalette(palette)
        self.setAutoFillBackground( True );

class DataEditor(QtGui.QDialog):

    current_path = None

    def __init__(self, parent = None):
        super(DataEditor, self).__init__(parent)
        self.build_ui()

    def build_ui(self):
        self.hbox = QtGui.QHBoxLayout(self)
        self.hbox.setContentsMargins(0,0,0,0)
        self.build_sidebar       ()
        self.build_central_widget()

        self.resize( 900, 500 )

    def build_sidebar(self):
        self.sidebar = DataSideBar(self)
        self.hbox.addWidget(self.sidebar)

    def build_central_widget(self):
        self.central_widget = LightCentralWidget(self)
        self.hbox.addWidget(self.central_widget)

    def load_package(self, path):
        self.current_path = path

        for dir_, dirs_, files_ in os.walk(path):
            for file_ in files_:
                file_path_ = os.path.join(dir_, file_)
                rel_path   = os.path.relpath(file_path_, path)
                self.add_sidebar_label( rel_path )

    def add_sidebar_label(self, text):
        lb = QtGui.QLabel(text, self)
        lb.setCursor( QtCore.Qt.PointingHandCursor )
        self.sidebar.frame_layout().addWidget(lb)

def launch_data_editor(data_pack_path):
    win = DataEditor()
    win.show()
    win.load_package(data_pack_path)

import sys
def test():
    app = QtGui.QApplication(sys.argv)

    dlg = DataEditor()
    dlg.show()
    dlg.load_package("C:\\Documents and Settings\\cns_dasi\\Application Data\\openningia\\l5rcm\\core.data\\core")
    sys.exit(app.exec_())

if __name__ == '__main__':
    test()
