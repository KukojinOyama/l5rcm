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

class BuyPerkDialog(QtGui.QDialog):
    def __init__(self, pc, tag, conn, parent = None):
        super(BuyPerkDialog, self).__init__(parent)
        self.tag = tag
        self.adv = None
        self.pc  = pc
        self.dbconn = conn
        self.perk_id   = 0
        self.perk_nm   = ''
        self.item = None
        self.build_ui()
        self.load_data()
        
    def build_ui(self):
        if self.tag == 'merit':
            self.setWindowTitle("Add Advantage")
        else:
            self.setWindowTitle("Add Disadvantage")
            
        self.setMinimumSize(400, 0)
                        
        self.bt_accept = QtGui.QPushButton('Ok'    , self)
        self.bt_cancel = QtGui.QPushButton('Cancel', self)            
        
        lvbox = QtGui.QVBoxLayout(self)        
            
        grp     = QtGui.QGroupBox("SubType", self)
        vbox    = QtGui.QVBoxLayout(grp)
        self.cb_subtype = QtGui.QComboBox(self)
        self.cb_subtype.currentIndexChanged.connect( self.on_subtype_select )
        vbox.addWidget(self.cb_subtype)
        lvbox.addWidget(grp)
        
        grp     = None
        if self.tag == 'merit':
            grp     = QtGui.QGroupBox("Advantage", self)        
        else:
            grp     = QtGui.QGroupBox("Disadvantage", self)
        vbox    = QtGui.QVBoxLayout(grp)
        self.cb_perk = QtGui.QComboBox(self)
        self.cb_perk.currentIndexChanged.connect( self.on_perk_select )
        vbox.addWidget(self.cb_perk)           
        lvbox.addWidget(grp)
        
        grp     = QtGui.QGroupBox("Rank", self)
        vbox    = QtGui.QVBoxLayout(grp)
        self.cb_rank = QtGui.QComboBox(self)
        self.cb_rank.currentIndexChanged.connect( self.on_rank_select )
        vbox.addWidget(self.cb_rank)
        lvbox.addWidget(grp)
        
        grp     = QtGui.QGroupBox("Notes", self)
        vbox    = QtGui.QVBoxLayout(grp)
        self.tx_notes = QtGui.QTextEdit(self)
        vbox.addWidget(self.tx_notes)
        lvbox.addWidget(grp)     
        
        if self.tag == 'merit':
            grp     = QtGui.QGroupBox("XP Cost", self)
        else:
            grp     = QtGui.QGroupBox("XP Gain", self)
        vbox    = QtGui.QVBoxLayout(grp)
        self.le_cost = QtGui.QLineEdit(self)
        vbox.addWidget(self.le_cost)
        lvbox.addWidget(grp)       
        
        
        self.btbox = QtGui.QDialogButtonBox(QtCore.Qt.Horizontal)
        self.btbox.addButton(self.bt_accept, QtGui.QDialogButtonBox.AcceptRole)
        self.btbox.addButton(self.bt_cancel, QtGui.QDialogButtonBox.RejectRole)
        
        self.btbox.accepted.connect(self.on_accept)
        self.btbox.rejected.connect(self.close    )
        
        lvbox.addWidget(self.btbox)

    def load_data(self):
        # load subtypes
        c = self.dbconn.cursor()        
        c.execute('''select distinct subtype from perks''')
        for typ in c.fetchall():
            self.cb_subtype.addItem(typ[0].capitalize(), typ[0])
        c.close()
        
    def on_subtype_select(self, text = ''):
        self.item = None
        self.cb_perk.clear()
        
        selected = self.cb_subtype.currentIndex()
        if selected < 0:
            return
        type_ = self.cb_subtype.itemData(selected)
        
        # populate perks
        c = self.dbconn.cursor()        
        c.execute('''select name, uuid from perks
                     where type=? and subtype=?''', [self.tag, type_])
        for name, uuid in c.fetchall():
            self.cb_perk.addItem(name, uuid)
        c.close()        
        
    def on_perk_select(self, text = ''):
        self.item = None
        self.cb_rank.clear()
    
        selected = self.cb_perk.currentIndex()
        if selected < 0:
            return
        perk = self.cb_perk.itemData(selected)
        self.perk_id = perk
        self.perk_nm = text
        
        # populate ranks
        # populate perks
        c = self.dbconn.cursor()        
        c.execute('''select perk_rank, cost from perk_ranks
                     where perk_uuid=?''', [perk])
        for rank, cost in c.fetchall():
            self.cb_rank.addItem('Rank %d' % rank, 
                                (rank, cost))
        c.close() 
        
    def on_rank_select(self, text = ''):       
        selected = self.cb_rank.currentIndex()
        if selected < 0:
            return
        rank, cost = self.cb_rank.itemData(selected)        
        tag  = None
        self.le_cost.setReadOnly( cost != 0 )
        if cost == 0:
            self.le_cost.setPlaceholderText('Insert XP')
            self.le_cost.setText('')
        else:
            # look for exceptions
            c = self.dbconn.cursor() 
            c.execute('''select tag, cost from perk_excepts
                         where perk_uuid=? and perk_rank=?
                         order by cost asc''', [self.perk_id, rank])            
            cost = abs(cost)
            
            for t, discounted in c.fetchall():
                if self.pc.has_tag(t):
                    if discounted.startswith('-') or discounted.startswith('+'):
                        cost += int(discounted)
                    else:
                        cost = int(discounted)
                    tag  = t
                    break
            if cost <= 0:
                cost = 1
            
            text = '%d' % cost
            
            if tag:
                text += ' (%s)' % tag.capitalize()
            self.le_cost.setText(text)
            c.close()
        
        if self.tag == 'flaw':
            cost = -cost
        self.item = models.PerkAdv(self.perk_id, rank, cost, tag)
            
    def on_accept(self):
        if not self.item:
            QtGui.QMessageBox.warning(self, "Perk not found",
                                      "Please select a perk.")
            return
        
        self.item.extra = self.tx_notes.toPlainText()
        if self.item.cost == 0:
            if self.le_cost.text() != '':
                try:
                    self.item.cost = int(self.le_cost.text())
                except:
                    self.item.cost = 0
            if self.item.cost == 0:
                QtGui.QMessageBox.warning(self, "Invalid XP Cost",
                                          "Please specify the XP Cost.")
                return

        if self.tag == 'merit':
            self.item.desc = "%s Rank %d, XP Cost: %d" % \
            ( self.perk_nm, self.item.rank, self.item.cost )
            
            if (self.item.cost + self.pc.get_px()) > self.pc.exp_limit:
                QtGui.QMessageBox.warning(self, "Not enough XP",
                "Cannot purchase.\nYou've reached the XP Limit.")                
                return
        else:
            self.item.desc = "%s Rank %d, XP Gain: %d" % \
            ( self.perk_nm, self.item.rank, abs(self.item.cost) )
            
            
        self.pc.add_advancement(self.item)
        self.accept()
