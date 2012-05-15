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
import dbutil
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
        self.perk_rule = None
        self.item = None
        self.edit_mode = False
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
        
    def set_edit_mode(self, flag):
        self.edit_mode = flag

        self.cb_subtype.setEnabled(not flag)
        self.cb_perk.setEnabled   (not flag)
        self.cb_rank.setEnabled   (not flag)
        
        self.cb_subtype.parent().setVisible(not flag)
        
        self.cb_rank   .blockSignals(flag)
        self.cb_perk   .blockSignals(flag)
        self.cb_subtype.blockSignals(flag)
        
    def load_item(self, perk):
        self.item = perk.adv
        self.cb_perk.clear()
        self.cb_perk.addItem(perk.name, perk.adv.perk)        
        self.cb_perk.setCurrentIndex(0)
        
        self.tx_notes.setPlainText(perk.adv.extra)
        
    def on_subtype_select(self, text = ''):
        print 'on_subtype_select'
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
        print 'on_perk_select'
        self.item = None
        self.cb_rank.clear()
    
        selected = self.cb_perk.currentIndex()
        if selected < 0:
            return
        perk = self.cb_perk.itemData(selected)
        self.perk_id = perk
        self.perk_nm = self.cb_perk.itemText(selected)
        
        # get perk rule
        c = self.dbconn.cursor()        
        c.execute('''select uuid, rule from perks
                     where uuid=?''', [perk])
        for uuid, rule in c.fetchall():
            self.perk_rule = rule
            break;
        c.close()   
        
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
        print 'on_rank_select'
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
            
            c.close()
        
        self.item = models.PerkAdv(self.perk_id, rank, cost, tag)
        
        text_ = '%d' % self.item.cost        
        if tag:
            text_ += ' (%s)' % tag.capitalize()
        self.le_cost.setText(text_)
                
    def update_perk(self):
        self.item.extra = self.tx_notes.toPlainText()
        
    def on_accept(self):
        if self.edit_mode:
            self.update_perk()
            self.accept()
            return
        
        if not self.item:
            QtGui.QMessageBox.warning(self, "Perk not found",
                                      "Please select a perk.")
            return
        
        self.item.rule  = self.perk_rule
        self.item.extra = self.tx_notes.toPlainText()
        if self.item.cost == 0:
            if self.le_cost.text() != '':
                try:
                    self.item.cost = int(self.le_cost.text())
                except:
                    self.item.cost = 0
            if self.item.cost < 0:
                QtGui.QMessageBox.warning(self, "Invalid XP Cost",
                                          "Please specify a number greater than 0.")
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
            
        if self.tag == 'flaw':
            self.item.cost *= -1
            
        self.pc.add_advancement      (self.item)        
        self.process_special_effects (self.item)        
        self.accept()
        
    def process_special_effects(self, item):
        def _add_free_skill_rank(skill_nm):
            skill_id  = dbutil.get_skill_id_from_name(self.dbconn, skill_nm)
            print '%s => %d' % ( skill_nm, skill_id )
            cur_value = self.pc.get_skill_rank(skill_id)
            new_value = cur_value + 1
            cost = 0
            adv = models.SkillAdv(skill_id, 0)
            adv.rule = dbutil.get_mastery_ability_rule(self.dbconn, skill_id, new_value)
            adv.desc = str.format('{0}, Rank {1} to {2}. Gained by {3}',
                                  skill_nm, cur_value, new_value, self.perk_nm )
            self.pc.add_advancement(adv)
            
        if item.rule == 'fk_gaijin_pepper':
            # add a rank in Craft (Explosives), zero cost :)
            _add_free_skill_rank('Craft (Explosives)')
        elif item.rule == 'fk_gozoku':
            # add a rank in Lore (Gozoku), zero cost :)
            _add_free_skill_rank('Lore (Gozoku)')
        elif item.rule == 'fk_kolat':
            # add a rank in Lore (Kolat), zero cost :)
            _add_free_skill_rank('Lore (Kolat)')
        elif item.rule == 'fk_lying_darkness':
            # add a rank in Lore (Lying Darkness), zero cost :)
            _add_free_skill_rank('Lore (Lying Darkness)')
        elif item.rule == 'fk_maho':
            # add a rank in Lore (Maho), zero cost :)
            _add_free_skill_rank('Lore (Maho)')
