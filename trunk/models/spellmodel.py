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

from PySide import QtGui, QtCore

class SpellItemModel(object):
    def __init__(self):
        self.name      = ''
        self.ring      = ''
        self.mastery   = ''
        self.range     = ''
        self.area      = ''
        self.duration  = ''
        self.raises    = ''
        self.is_school = False
        self.tags      = []

    def __str__(self):
        return self.name

class SpellTableViewModel(QtCore.QAbstractTableModel):
    def __init__(self, dbconn, parent = None):
        super(SpellTableViewModel, self).__init__(parent)
        self.items = []
        self.headers = ['Name', 'Ring', 'Mastery', 'Range', 'Area of Effect', 
                        'Duration', 'Raises']
        self.text_color = QtGui.QBrush(QtGui.QColor(0x15, 0x15, 0x15))
        self.bg_color   = [ QtGui.QBrush(QtGui.QColor(0xFF, 0xEB, 0x82)),
                            QtGui.QBrush(QtGui.QColor(0xEB, 0xFF, 0x82)) ]        
        self.item_size = QtCore.QSize(28, 28)
        if parent:
            self.bold_font = parent.font()
            self.bold_font.setBold(True)

        self.dbconn = dbconn

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

    def data(self, index, role):
        if not index.isValid() or index.row() >= len(self.items):
            return None
        item = self.items[index.row()]
        if role == QtCore.Qt.DisplayRole:
			if index.column() == 0:
				return item.name
			if index.column() == 1:
				return item.ring
			if index.column() == 2:
				return item.mastery
			if index.column() == 3:
				return item.range
			if index.column() == 4:
				return item.area
			if index.column() == 5:
				return item.duration
			if index.column() == 6:
				return item.raises
        #    elif role == QtCore.Qt.DecorationRole:
        #        if index.column() == 0 and (item['epstatus'] & SHOW_STATUS_NEW == SHOW_STATUS_NEW):
        #            return QtGui.QIcon(':/icons/label_new_red.png')
        #    elif role == QtCore.Qt.UserRole:
        #        return item['showid']
        elif role == QtCore.Qt.FontRole:
            if item.is_school and self.bold_font:
                return self.bold_font
        elif role == QtCore.Qt.ForegroundRole:
            return self.text_color
        elif role == QtCore.Qt.BackgroundRole:
            return self.bg_color[ index.row() % 2 ]            
        elif role == QtCore.Qt.SizeHintRole:
            return self.item_size
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


    def build_item_model(self, sp_id):
        c = self.dbconn.cursor()
        itm = SpellItemModel()
        c.execute('''SELECT * FROM spells
                     WHERE uuid=?''', [sp_id])
           
        for f in c.fetchall():
            itm.name     = f[1]
            itm.ring     = f[2]
            itm.mastery  = f[3]
            itm.range    = f[4]
            itm.area     = f[5]
            itm.duration = f[6]
            itm.raises   = f[7]
            
        c.close()
        return itm

    def update_from_model(self, model):
        spells = model.get_spells()
        self.clean()
        
        print 'update spells from model'
       
        for s in spells:
            itm = self.build_item_model(s)
            self.add_item(itm)
        