# -*- coding: utf-8 -*-
# Copyright (C) 2011 Daniele Simonetti
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


import sys
if __name__ == "__main__":
    sys.path.append("../")

import os
import dal
import osutil
import json

from PySide  import QtCore, QtGui
from layouts import animatedvboxlayout
from models  import docs

class DataSideBar(QtGui.QScrollArea):
    def __init__(self, parent = None):
        super(DataSideBar, self).__init__(parent)
        self.build_ui()

    def build_ui(self):
        self.setSizePolicy( QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding )

        self.fr = QtGui.QTreeWidget()
        palette = self.fr.palette()
        palette.setColor( QtGui.QPalette.Base      , QtGui.QColor("#eee")  )
        palette.setColor( QtGui.QPalette.WindowText, QtGui.QColor("#000")  )
        self.fr.setPalette(palette)
        #self.fr.setAutoFillBackground(True)
        self.fr.setHeaderLabel("FILES")

        self.setWidget(self.fr)
        self.setWidgetResizable(True)

        if sys.platform == 'win32':
            # apply stylesheet
            ss = """\
QTreeWidget::branch:has-children:!has-siblings:closed,
QTreeWidget::branch:closed:has-children:has-siblings {
     border-image: none;
     image: url(branch-closed.png);
}

QTreeWidget::branch:open:has-children:!has-siblings,
QTreeWidget::branch:open:has-children:has-siblings  {
     border-image: none;
     image: url(branch-open.png);
}
QTreeWidget { font-size: 16px; }
QTreeWidget::item {
    /* Spacing between items*/
    margin: 2px 3px;
    padding: 2px;
    padding-left: 5px;

    /* Fix size */
    min-height: 20px;
}
"""

            self.setStyleSheet(ss)
            self.setCursor( QtGui.QCursor( QtCore.Qt.PointingHandCursor ) )

    def sizeHint(self):
        if self.parent() is not None:
            return QtCore.QSize( self.parent().width()*0.25, self.parent().height() )

    def tree_widget(self):
        return self.fr

class CentralWidget(QtGui.QTabBar):
    def __init__(self, parent = None):
        super(CentralWidget, self).__init__(parent)

        self.setSizePolicy( QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding )
        palette = self.palette()
        palette.setColor( QtGui.QPalette.Window, QtGui.QColor("#666")  )
        self.setPalette(palette)
        self.setAutoFillBackground( True );

    def add_document(self, item):
        self.addTab(item.path)

    def rem_document(self, item):
        pass

    def upd_document(self, item, st):
        pass

class DataEditor(QtGui.QDialog):

    current_path   = None
    documents      = None

    installed_data = None

    MANIFEST_FILE_NAME = "manifest"

    def __init__(self, parent = None):
        super(DataEditor, self).__init__(parent)
        self.build_ui()
        self.reload_installed_data()

        self.documents = docs.OpenedDocuments(self)
        self.documents.doc_added        .connect( self.central_widget.add_document )
        self.documents.doc_removed      .connect( self.central_widget.rem_document )
        self.documents.doc_status_change.connect( self.central_widget.upd_document )

    def build_ui(self):
        self.hbox = QtGui.QHBoxLayout(self)
        self.hbox.setContentsMargins(0,0,0,0)
        self.build_sidebar       ()
        self.build_central_widget()

        self.resize( 900, 500 )

    def build_sidebar(self):
        self.sidebar = DataSideBar(self)
        self.hbox.addWidget(self.sidebar)
        self.sidebar.tree_widget().itemActivated.connect( self.on_item_activate )

    def build_central_widget(self):
        self.central_widget = CentralWidget(self)
        self.hbox.addWidget(self.central_widget)

    def reload_installed_data(self):
        if not self.installed_data:
            print('Loading datapack data')
            self.dstore = dal.Data(
                [osutil.get_user_data_path('core.data'),
                 osutil.get_user_data_path('data')],
                 [])
        else:
            print('Re-loading datapack data')
            self.dstore.rebuild(
                    [osutil.get_user_data_path('core.data'),
                    osutil.get_user_data_path('data')],
                    [])

    def load_package(self, path):
        self.current_path = path

        for dir_, dirs_, files_ in os.walk(path):
            rel_path = os.path.relpath(dir_, path)
            if rel_path == ".": rel_path = "ROOT"
            top_level_item = QtGui.QTreeWidgetItem( [rel_path, dir_] )
            self.sidebar.tree_widget().addTopLevelItem(top_level_item)
            for file_ in files_:
                file_item = QtGui.QTreeWidgetItem( top_level_item, [file_, os.path.join(dir_, file_) ] )

    def open_manifest_file(self, path):
        try:
            if os.path.exists(path):
                with open(path, 'r') as manifest_fp:
                    dm = dal.DataManifest(json.load(manifest_fp))
                    dm.path = path
                    self.documents.add_document(path, dm)
        except Exception as ex:
            print(ex)

    def open_data_file(self, path): pass

    def on_item_activate(self, item, column):
        path_ = item.text(1)
        file_ = os.path.basename(path_)
        if file_ == self.MANIFEST_FILE_NAME:
            self.open_manifest_file(path_)
        elif path_.endswith(".xml"):
            self.open_data_file(path_)

def launch_data_editor(data_pack_path):
    win = DataEditor()
    win.show()
    win.load_package(data_pack_path)

def test():
    APP_NAME, APP_VERSION, APP_ORG = "l5rcm", "x.y", "openningia"

    app = QtGui.QApplication (sys.argv)
    app.setApplicationName   (APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName  (APP_ORG)

    dlg = DataEditor()
    dlg.show()
    dlg.load_package("C:\\Documents and Settings\\cns_dasi\\Application Data\\openningia\\l5rcm\\core.data\\core")
    #dlg.load_package("C:\\Documents and Settings\\cns_dasi\\Application Data\\openningia\\l5rcm\\core.data\\core")
    sys.exit(app.exec_())

if __name__ == '__main__':
    test()
