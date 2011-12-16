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

class ArmorOutfit(object):
    def __init__(self):
        self.tn   = 0
        self.rd   = 0
        self.name = ''
        self.desc = ''
        self.rule = ''
        self.cost = ''

class WeaponOutfit(object):        
    def __init__(self):
        self.dr       = ''
        self.dr_alt   = ''
        self.name     = ''
        self.desc     = ''
        self.rule     = ''
        self.cost     = '' 
        self.range    = ''
        self.strength = 0
        self.min_str  = 0
        self.qty      = 1
        self.tags     = []        
        
def weapon_outfit_from_db(dbconn, weap_uuid):
    itm = WeaponOutfit()
    
    c = dbconn.cursor()
    c.execute('''select name, dr, dr_alt, range, strength,
                 min_strength, effect_id, cost
                 from weapons
                 where uuid=?''', [weap_uuid])
    
    for name, dr, dr_alt, rng, str_, mstr_, eff, cost in c.fetchall():
        c.execute('''select desc from effects
                     where uuid=?''', [eff])
        rule_text = ''
        for desc in c.fetchall():
            rule_text = desc[0]
            break
       
        itm.name     = name
        itm.dr       = dr        or 'N/A'
        itm.dr_alt   = dr_alt    or 'N/A'
        itm.rule     = rule_text
        itm.cost     = cost      or 'N/A'
        itm.range    = rng       or 'N/A' 
        itm.strength = str_      or 'N/A'
        itm.min_str  = mstr_     or 'N/A'
        break
        
    c.execute('''select uuid, tag from tags where uuid=?''', [weap_uuid])
    for uuid, tag in c.fetchall():
        print 'weapon has tag %s' % tag
        itm.tags.append(tag)
        
    c.close()
    return itm
            
def armor_outfit_from_db(dbconn, armor_uuid):
    itm = ArmorOutfit()
    
    c = dbconn.cursor()
    c.execute('''select name, tn, rd, special, cost from armors
                 where uuid=?''', [armor_uuid])
    
    for name, tn, rd, special, cost in c.fetchall():
        c.execute('''select desc from effects
                     where tag=?''', [special])
        rule_text = ''
        for desc in c.fetchall():
            rule_text = desc[0]
            break
            
        itm.name = name
        itm.tn   = tn
        itm.rd   = rd
        itm.rule = rule_text
        itm.cost = cost
        break
        
    c.close()
    return itm

class WeaponTableViewModel(QtCore.QAbstractTableModel):
    def __init__(self, type_, parent = None):
        super(WeaponTableViewModel, self).__init__(parent)
        self.type  = type_
        self.items = []
        if type_ == 'melee':
            self.headers = ['Name', 'DR', 'Sec. DR']
        elif type_ == 'ranged':
            self.headers = ['Name', 'Range', 'Strength', 'Min. Str.']
        elif type_ == 'arrow':
            self.headers = ['Name', 'DR', 'Quantity']
            
        self.text_color = QtGui.QBrush(QtGui.QColor(0x15, 0x15, 0x15))
        self.bg_color   = [ QtGui.QBrush(QtGui.QColor(0xFF, 0xEB, 0x82)),
                            QtGui.QBrush(QtGui.QColor(0xEB, 0xFF, 0x82)) ]        
        self.item_size = QtCore.QSize(28, 28)

    def rowCount(self, parent = QtCore.QModelIndex()):
        return len(self.items)

    def columnCount(self, parent = QtCore.QModelIndex()):
        return len(self.headers)

    def headerData(self, section, orientation, role = QtCore.Qt.ItemDataRole.DisplayRole):
        if orientation != QtCore.Qt.Orientation.Horizontal:
            return None
        if role == QtCore.Qt.DisplayRole:
            return self.headers[section]
        return None

    def data(self, index, role = QtCore.Qt.UserRole):
        if not index.isValid() or index.row() >= len(self.items):
            return None
        item = self.items[index.row()]
        if role == QtCore.Qt.DisplayRole:
            if self.type == 'melee':
                return self.melee_display_role(item, index.column())
            elif self.type == 'ranged':
                return self.ranged_display_role(item, index.column())
            elif self.type == 'arrow':
                return self.arrow_display_role(item, index.column())
        elif role == QtCore.Qt.ForegroundRole:
            return self.text_color
        elif role == QtCore.Qt.BackgroundRole:
            return self.bg_color[ index.row() % 2 ]            
        elif role == QtCore.Qt.SizeHintRole:
            return self.item_size
        elif role == QtCore.Qt.UserRole:
            return item    
        return None
        
    def melee_display_role(self, item, column):
        if column == 0:
            return item.name
        if column == 1:
            return item.dr
        if column == 2:
            return item.dr_alt
        return None
        
    def ranged_display_role(self, item, column):
        if column == 0:
            return item.name
        if column == 1:
            return item.range
        if column == 2:
            return item.strength
        if column == 3:
            return item.min_str            
        return None        

    def arrow_display_role(self, item, column):
        if column == 0:
            return item.name
        if column == 1:
            return item.dr
        if column == 2:
            return item.qty
        return None
        
    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsDropEnabled
        flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        return flags

    def add_item(self, item):
        row = self.rowCount()
        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        self.items.append(item)
        self.endInsertRows()

    def clean(self):
        self.beginResetModel()
        self.items = []
        self.endResetModel()

    def update_from_model(self, model):
        self.clean()
        for w in model.get_weapons():
            if self.type in w.tags:
                self.add_item(w)