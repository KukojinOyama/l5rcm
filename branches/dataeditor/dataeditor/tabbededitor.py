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

from PySide import QtCore, QtGui
import os

class L5RCMTabbedEditor(QtGui.QTabWidget):
    def __init__(self, model, parent = None):
        super(L5RCMTabbedEditor, self).__init__(parent)

        self.setSizePolicy( QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding )
        palette = self.palette()
        palette.setColor( QtGui.QPalette.Window, QtGui.QColor("#666")  )
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.setDocumentMode(True)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setUsesScrollButtons(True)
        #self.setTabShape(QtGui.QTabBar.RoundedEast)

        model.doc_added        .connect( self.on_doc_added          )
        #model.doc_removed      .connect( self.on_doc_removed        )
        #model.doc_status_change.connect( self.on_doc_status_changed )

        self.model = model

    def on_doc_added(self, doc):
    	short_name = os.path.basename(doc.path)
    	self.addTab(QtGui.QLabel(doc.path), short_name)

   	def on_doc_removed(self, doc):
   		pass

   	def on_doc_status_changed(self, doc):
   		pass

