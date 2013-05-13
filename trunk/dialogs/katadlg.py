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

import dal
import dal.query
import models
import widgets
import rules
from PyQt4 import QtCore, QtGui

class KataDialog(QtGui.QDialog):

    # data storage
    dstore         = None
    # title bar
    header         = None
    # frame layout
    vbox_lo        = None 
    # buttons
    bt_ok          = None
    # controls
    cb_kata        = None
    tx_element     = None
    tx_mastery     = None
    tx_cost        = None
    req_list       = None
    tx_detail      = None    
    
    def __init__(self, pc, dstore, parent = None):
        super(KataDialog, self).__init__(parent)
        self.pc     = pc
        self.dstore = dstore
        self.item   = None        
        
        self.build_ui       ()
        self.connect_signals()
        self.setup          ()
        
    def build_ui(self):
        self.vbox_lo  = QtGui.QVBoxLayout(self)        
        self.bt_ok    = QtGui.QPushButton(self.tr('Buy'), self)        
        self.header   = QtGui.QLabel(self)                                
        center_fr     = QtGui.QFrame(self)
        center_fr.setFrameStyle(QtGui.QFrame.Sunken)
        cfr_fbox      = QtGui.QFormLayout(center_fr)       

        # bottom bar
        bottom_bar     = QtGui.QFrame(self)                                
        hbox = QtGui.QHBoxLayout(bottom_bar)
        hbox.addStretch()
        hbox.addWidget(self.bt_ok)
        
        self.cb_kata     = QtGui.QComboBox(self)
        self.req_list    = widgets.RequirementsWidget(self)
        self.tx_element  = QtGui.QLabel(self)
        self.tx_mastery  = QtGui.QLabel(self)
        self.tx_cost     = QtGui.QLabel(self)
        self.tx_detail   = QtGui.QLabel(self)
        self.tx_detail.setWordWrap(True)
        
        cfr_fbox.addRow(self.tr("Kata"          ), self.cb_kata   )
        cfr_fbox.addRow(self.tr("Element"       ), self.tx_element)
        cfr_fbox.addRow(self.tr("Mastery"       ), self.tx_mastery)
        cfr_fbox.addRow(self.tr("XP Cost"       ), self.tx_cost   )
        cfr_fbox.addRow(self.tr("Requirements"  ), self.req_list  )
        cfr_fbox.addRow(self.tr("Details"       ), self.tx_detail )
        
        cfr_fbox.setContentsMargins(160, 20, 160, 20)
        
        self.vbox_lo.addWidget(self.header)
        self.vbox_lo.addWidget(center_fr  )
        self.vbox_lo.addWidget(bottom_bar )
        
        self.resize( 600, 300 )
        
    def connect_signals(self):
        self.bt_ok.clicked.connect( self.accept )
        self.cb_kata.currentIndexChanged.connect( self.on_kata_change )
        
    def setup(self):
        self.set_header_text(self.tr('''
        <center>
        <h1>Buy a Kata</h1>
        <p style="color: #666">You can only buy Kata if you match at least one requirement</p>
        </center>
        '''))
        
        self.setWindowTitle(self.tr("L5RCM: Kata")) 
        self.load_kata()
        
    def load_kata(self):
        for kata in self.dstore.katas:
            if not self.pc.has_kata(kata.id):
                self.cb_kata.addItem( kata.name, kata.id )                        
        
    def set_header_text(self, text):
        self.header.setText(text)
        
    def on_kata_change(self, idx):
        idx = self.cb_kata.currentIndex()
        itm = self.cb_kata.itemData(idx)
        
        kata = dal.query.get_kata(self.dstore, itm)
        if not kata:
            return           

        ring_name = dal.query.get_ring(self.dstore, kata.element)
            
        self.tx_element.setText(ring_name.text)
        self.tx_mastery.setText(str(kata.mastery))
        self.tx_cost.setText(str(kata.mastery))
        self.tx_detail.setText("<p><em>{0}</em></p>".format(kata.desc))
        self.req_list.set_requirements( self.pc, self.dstore, kata.require )
        
        self.bt_ok.setEnabled( self.req_list.match_at_least_one() )

    def accept(self):
        # save item

        super(KataDialog, self).accept()
            