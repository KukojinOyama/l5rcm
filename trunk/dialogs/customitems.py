# -*- coding: iso-8859-1 -*-
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

import models
from PySide import QtCore, QtGui

def grouped_widget(title, widget, parent = None):
    grp     = QtGui.QGroupBox(title, parent)
    vbox    = QtGui.QVBoxLayout(grp)
    vbox.addWidget(widget)
    
    return grp

class CustomArmorDialog(QtGui.QDialog):
    def __init__(self, pc, parent = None):
        super(CustomArmorDialog, self).__init__(parent)
        self.pc  = pc
        self.item = None
        self.build_ui()
        self.load_data()
        
    def build_ui(self):
        self.setWindowTitle("Add Custom Armor")
            
        self.setMinimumSize(400, 0)
                        
        self.bt_accept = QtGui.QPushButton('Ok'    , self)
        self.bt_cancel = QtGui.QPushButton('Cancel', self)            
        
        lvbox = QtGui.QVBoxLayout(self)
        self.tx_name = QtGui.QLineEdit(self)           
        lvbox.addWidget(grouped_widget("Name", self.tx_name, self))

        self.tx_tn = QtGui.QLineEdit(self)                
        self.tx_rd = QtGui.QLineEdit(self) 
        fr      = QtGui.QFrame(self)
        hbox    = QtGui.QHBoxLayout(fr)
        hbox.addWidget(grouped_widget("Armor TN", self.tx_tn, self))
        hbox.addWidget(grouped_widget("Reduction", self.tx_rd, self))      
        lvbox.addWidget(fr)
        
        self.tx_notes = QtGui.QTextEdit(self)         
        lvbox.addWidget(grouped_widget("Notes", self.tx_notes, self))
        
        self.btbox = QtGui.QDialogButtonBox(QtCore.Qt.Horizontal)
        self.btbox.addButton(self.bt_accept, QtGui.QDialogButtonBox.AcceptRole)
        self.btbox.addButton(self.bt_cancel, QtGui.QDialogButtonBox.RejectRole)
        
        self.btbox.accepted.connect(self.on_accept)
        self.btbox.rejected.connect(self.close    )
        
        lvbox.addWidget(self.btbox)
        
    def load_data(self):
        if self.pc.armor is None:
            return
        self.tx_name .setText(self.pc.armor.name    )
        self.tx_tn   .setText(str(self.pc.armor.tn) )
        self.tx_rd   .setText(str(self.pc.armor.rd) )
        self.tx_notes.setText(self.pc.armor.desc)
            
    def on_accept(self):
        self.item = models.ArmorOutfit()
        try:
            self.item.tn   = int(self.tx_tn.text())
            self.item.rd   = int(self.tx_rd.text())
        except:
            self.item.tn   = 0
            self.item.rd   = 0
        
        self.item.name = self.tx_name.text()
        self.item.desc = self.tx_notes.toPlainText()
        
        if self.item.name == '':
            QtGui.QMessageBox.warning(self, "Custom Armor",
                                      "Please enter a name.")
            return
        
        self.pc.armor = self.item
        self.accept()
