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

from PySide import QtCore, QtGui
from widgets.spell_item_selection import SpellItemSelection

class SpellAdvDialog(QtGui.QDialog):
        
    adv            = None
    pc             = None
    dstore         = None
    quit_on_accept = False
    error_bar      = None
    header         = None
    spell_wdg      = None
    lb_pgcnt       = None       
    bt_next        = None
    bt_back        = None
    page_count     = 0
    current_page   = 0
    
    rb_omaho       = None
    rb_amaho       = None
    rb_nmaho       = None
    
    vbox_lo        = None
    
    selected       = None
    
    def __init__(self, pc, dstore, parent = None):
        super(SpellAdvDialog, self).__init__(parent)
        self.pc  = pc
        self.dstore = dstore
        self.page_count = self.pc.get_how_many_spell_i_miss()
        self.selected = [None]*self.page_count
        self.build_ui()
        self.connect_signals()
        self.load_data(0)
        
    def build_ui(self):
        self.vbox_lo = QtGui.QVBoxLayout(self)        
        self.bt_next  = QtGui.QPushButton(self.tr('Next'), self)
        self.bt_back  = QtGui.QPushButton(self.tr('Back'), self)        
        self.lb_pgcnt = QtGui.QLabel(self)                
        self.spell_wdg = SpellItemSelection(self.pc, self.dstore, self)        
        self.header    = QtGui.QLabel(self)                
        self.error_bar = QtGui.QLabel(self)
        
        center_fr      = QtGui.QFrame(self)
        cfr_vbox       = QtGui.QVBoxLayout(center_fr)
        
        grp_maho       = QtGui.QGroupBox(self.tr('Maho'), self)
        bottom_bar     = QtGui.QFrame(self)
        
        self.rb_amaho       = QtGui.QRadioButton(self.tr('Allow Maho'), self)
        self.rb_nmaho       = QtGui.QRadioButton(self.tr('No Maho'),    self)
        self.rb_omaho       = QtGui.QRadioButton(self.tr('Only Maho'),  self)
        
        self.rb_amaho.setProperty('tag', 'allow_maho')
        self.rb_nmaho.setProperty('tag', 'no_maho')
        self.rb_omaho.setProperty('tag', 'only_maho')
        
        # maho groupbox
        maho_hbox = QtGui.QHBoxLayout(grp_maho)
        maho_hbox.addWidget(self.rb_amaho)
        maho_hbox.addWidget(self.rb_nmaho)
        maho_hbox.addWidget(self.rb_omaho)
        
        self.rb_amaho.setChecked(True)
        
        # bottom bar
        hbox = QtGui.QHBoxLayout(bottom_bar)
        hbox.addWidget(self.lb_pgcnt)
        hbox.addStretch()
        hbox.addWidget(self.bt_back)
        hbox.addWidget(self.bt_next)
        
        cfr_vbox.addWidget(self.spell_wdg)
        cfr_vbox.addWidget(grp_maho)
        cfr_vbox.setContentsMargins(100, 20, 100, 20)
        
        self.vbox_lo.addWidget(self.header)
        self.vbox_lo.addWidget(center_fr)
        self.vbox_lo.addWidget(self.error_bar)
        self.vbox_lo.addWidget(bottom_bar)
        
        self.resize( 600, 300 )               
        self.update_label_count()
        
    def connect_signals(self):
        self.bt_next.clicked.connect( self.next_page )
        self.bt_back.clicked.connect( self.prev_page )
        
        self.rb_amaho.toggled.connect( self.on_maho_toggled )
        self.rb_nmaho.toggled.connect( self.on_maho_toggled )
        self.rb_omaho.toggled.connect( self.on_maho_toggled )
        
    def load_data(self, pagen):
        self.spell_wdg.set_spell(self.selected[pagen])
        
        self.bt_back.setVisible(self.current_page != 0)
        if self.current_page == self.page_count-1:
            self.bt_next.setText(self.tr('Finish'))
        else:
            self.bt_next.setText(self.tr('Next'))
        
    def set_header_text(self, text):
        self.header.setText(text)
        
    def update_label_count(self):
        self.lb_pgcnt.setText( self.tr('Page {0} of {1}').format(self.current_page+1, self.page_count) )
        
    def next_page(self):
        self.selected[self.current_page] = self.spell_wdg.get_spell()
        if self.current_page == self.page_count - 1:
            self.accept()
        else:
            self.current_page += 1
            self.load_data(self.current_page)
        
    def prev_page(self):
        self.selected[self.current_page] = self.spell_wdg.get_spell()
        self.current_page -= 1
        self.load_data(self.current_page)
        
    def on_maho_toggled(self):
        self.spell_wdg.set_maho_filter( self.sender().property('tag') )
            