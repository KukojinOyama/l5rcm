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
import rules
import models

class ChooseItemDialog(QtGui.QDialog):
    def __init__(self, pc, tag, conn, parent = None):
        super(ChooseItemDialog, self).__init__(parent)
        self.tag    = tag
        self.adv    = None
        self.pc     = pc
        self.dbconn = conn
        self.item   = None
        self.filter = None
        self.weap_by_skill = {}
        self.build_ui()
        self.load_data()

    def build_ui(self):    
        # depending on the tag ( armor or weapon )
        # we build a different interface
        
        self.bt_accept = QtGui.QPushButton(self.tr("Ok")    , self)
        self.bt_cancel = QtGui.QPushButton(self.tr("Cancel"), self)
        
        self.bt_cancel.clicked.connect( self.close     )
        self.bt_accept.clicked.connect( self.on_accept )       
        
        grid = QtGui.QGridLayout(self)
        grid.setColumnStretch(0, 2)
        
        if self.tag == 'armor':
            self.setWindowTitle(self.tr("Wear Armor"))
            grp     = QtGui.QGroupBox(self.tr("Select Armor"), self)
            vbox    = QtGui.QVBoxLayout(grp)
            self.cb = QtGui.QComboBox(self)
            self.cb.currentIndexChanged.connect( self.on_armor_select )
            vbox.addWidget(self.cb)           
            grid.addWidget(grp, 0, 0)
            
            grp     = QtGui.QGroupBox(self.tr("Stats"), self)
            vbox    = QtGui.QVBoxLayout(grp)
            self.stats = QtGui.QLabel(self)
            self.stats.setWordWrap(True)
            vbox.addWidget(self.stats)
                                
            grid.setRowStretch(1, 2)    
            grid.addWidget(grp, 1, 0, 1, 4)
            grid.addWidget(self.bt_accept, 2, 2)
            grid.addWidget(self.bt_cancel, 2, 3)
        elif self.tag == 'weapon':
            self.setWindowTitle(self.tr("Add Weapon"))
            grp     = QtGui.QGroupBox(self.tr("Weapon Skill"), self)
            vbox    = QtGui.QVBoxLayout(grp)
            self.cb1 = QtGui.QComboBox(self)
            self.cb1.currentIndexChanged.connect( self.on_weap_skill_select )
            vbox.addWidget(self.cb1)           
            grid.addWidget(grp, 0, 0, 1, 2)

            grp     = QtGui.QGroupBox(self.tr("Weapon"), self)
            vbox    = QtGui.QVBoxLayout(grp)
            self.cb2 = QtGui.QComboBox(self)
            self.cb2.currentIndexChanged.connect( self.on_weap_select )
            vbox.addWidget(self.cb2)           
            grid.addWidget(grp, 1, 0, 1, 2)
            
            grp     = QtGui.QGroupBox(self.tr("Stats"), self)
            vbox    = QtGui.QVBoxLayout(grp)
            self.stats = QtGui.QLabel(self)
            self.stats.setWordWrap(True)
            vbox.addWidget(self.stats)
            
            grid.setRowStretch(2, 2)
            grid.addWidget(grp, 2, 0, 1, 4)
            grid.addWidget(self.bt_accept, 3, 2)
            grid.addWidget(self.bt_cancel, 3, 3)            
        
    def load_data(self):
        # RESET CACHE
        self.weap_by_skill = {}        
        c = self.dbconn.cursor()
        if self.tag == 'armor':
            self.cb.clear()
            
            c.execute('''select uuid, name from armors''')
            for uuid, name in c.fetchall():
                self.cb.addItem(name, uuid)
        elif self.tag == 'weapon':
            self.cb1.clear()
            c.execute('''select skills.uuid, name, tag from skills
                         inner join tags on tags.uuid=skills.uuid
                         where tag="weapon"''')
            for uuid, name, tag in c.fetchall():
                weaps = self.get_weapons_by_skill(uuid, self.filter)
                if len(weaps) > 0:
                    self.weap_by_skill[uuid] = weaps
                    self.cb1.addItem(name, uuid)
                
    def get_weapons_by_skill(self, sk_uuid, filter):
        weapons = []
        c = self.dbconn.cursor()
        if self.filter is None:
            c.execute('''select uuid, name from weapons
                         where skill_uuid=?''', [sk_uuid])
        else:
            c.execute('''select weapons.uuid, name from weapons
                         inner join tags on tags.uuid = weapons.uuid
                         where skill_uuid=? and tag=?''', [sk_uuid, self.filter])
                         
        for uuid, name in c.fetchall():
            weapons.append( (uuid, name) )
        c.close()
        
        return weapons
                
    def on_armor_select(self, text = ''):
        # list stats
        selected = self.cb.currentIndex()
        if selected < 0:
            return
        armor_uuid = self.cb.itemData(selected)
        self.item  = models.armor_outfit_from_db(self.dbconn, armor_uuid)
        
        stats_text = '''<p><pre>%-20s %s</pre></p>
                        <p><pre>%-20s %s</pre></p>
                        <p><pre>%-20s %s</pre></p>
                        <p><i>%s</i></p>''' % \
                        ( self.tr("Armor TN" ), self.item.tn,
                          self.tr("Reduction"), self.item.rd,
                          self.tr("Cost"     ), self.item.cost,
                          self.item.rule )
        self.stats.setText(stats_text)            
        
        self.stats.setSizePolicy( QtGui.QSizePolicy.Minimum,            
                                  QtGui.QSizePolicy.Minimum )
    
    def on_weap_skill_select(self, text = ''):
        self.cb2.clear()
        selected = self.cb1.currentIndex()
        if selected < 0:
            return
        sk_uuid = self.cb1.itemData(selected)
               
        for uuid, name in self.weap_by_skill[sk_uuid]:
            self.cb2.addItem(name, uuid)            
        
    def on_weap_select(self, text = ''):
        # list stats
        self.stats.setText('')
        
        selected = self.cb2.currentIndex()
        if selected < 0:
            return
        weap_uuid = self.cb2.itemData(selected)
        sk_uuid   = self.cb1.itemData(self.cb1.currentIndex())
        
        self.item = models.weapon_outfit_from_db(self.dbconn, weap_uuid, sk_uuid)
        lines = []
                    
        if self.item.dr is not None:
            lines.append( '<pre>%-24s %s</pre>' % (self.tr("Primary DR"  ), self.item.dr      ))
        if self.item.dr_alt is not None:
            lines.append( '<pre>%-24s %s</pre>' % (self.tr("Secondary DR"), self.item.dr_alt  ))
        if self.item.range is not None:               
           lines.append( '<pre>%-24s %s</pre>' % (self.tr("Range"        ), self.item.range   ))
        if self.item.strength is not None:
           lines.append( '<pre>%-24s %s</pre>' % (self.tr("Strength"     ), self.item.strength))
        if self.item.min_str is not None:
           lines.append( '<pre>%-24s %s</pre>' % (self.tr("Min. Strength"), self.item.min_str ))
        if self.item.cost is not None:
           lines.append( '<pre>%-24s %s</pre>' % (self.tr("Cost"         ), self.item.cost    ))
        if self.item.rule is not None:
           lines.append( '<i>%s</i>' % self.item.rule )
            
        self.stats.setText( '<p>' + '\n'.join(lines) + '</p>' )
            
        self.stats.setSizePolicy( QtGui.QSizePolicy.Minimum,            
                                  QtGui.QSizePolicy.Minimum )                       

  
    def on_accept(self):
        done = True

        if self.tag == 'armor' and self.item is not None:
            self.pc.armor = self.item
        elif self.tag == 'weapon' and self.item is not None:
            self.pc.add_weapon( self.item )

        self.accept()
        
    def set_filter(self, filter):
        self.filter = filter
        self.load_data()