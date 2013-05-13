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
import dal
import dal.query

MOD_TYPES = {
    "none" : "Select a modifier",
    "wdmg" : "Damage Roll",
    #"spcr" : "Spell Casting Roll",
    "anyr" : "Any Roll",
    "skir" : "Skill Roll",
    "hrnk" : "Health Rank",
    #"init" : "Initiative"
}

MOD_DTLS = {
    "none": ("none", "N/A"),
    "anyr": ("none", "N/A"),
    "hrnk": ("none", "N/A"),
    "skir": ("skill", "Select Skill"),
    "wdmg": ("aweap", "Select Weapon"),
}

class ModifierModel(object):
    def __init__(self):
        self.type   = 'none'
        self.dtl    = None
        self.value  = (0, 0)
        self.reason = "I'm just this good"
        self.active = False
       
class ModifiersTableViewModel(QtCore.QAbstractTableModel):
    user_change = QtCore.Signal()
    
    def __init__(self, parent = None):
        super(ModifiersTableViewModel, self).__init__(parent)
        self.items = []
        self.headers = ['Modifies', 'Detail', 'Value', 'Reason']
        self.dirty   = False
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
            return self.__display_role(item, index.column())
        elif role == QtCore.Qt.ForegroundRole:
            return self.text_color
        elif role == QtCore.Qt.BackgroundRole:
            return self.bg_color[ index.row() % 2 ]            
        elif role == QtCore.Qt.SizeHintRole:
            return self.item_size
        elif role == QtCore.Qt.CheckStateRole:
            return self.__checkstate_role(item, index.column())
        elif role == QtCore.Qt.UserRole:
            return item    
        return None
    
    def setData(self, index, value, role):
        if not index.isValid():
            return False
        
        ret  = False
        item = self.items[index.row()]
        self.dirty = True

        if index.column() == 0 and role == QtCore.Qt.CheckStateRole:
            item.active = (value == QtCore.Qt.Checked)
            ret = True
        elif role == QtCore.Qt.EditRole:
            if index.column() == 0:
                item.type = value
            elif index.column() == 1:
                item.dtl = value
            elif index.column() == 2:
                item.value = rules.parse_rtk_with_bonus(value)
            elif index.column() == 3:
                item.reason = value
            else:
                ret = False
            ret = True
        else:
            ret = super(ModifiersTableViewModel, self).setData(index, value, role)
        
        if ret:
            print('user change' + str(item.active))
            self.user_change.emit()
        return ret
        
    def __display_role(self, item, column):
        if column == 0:
            return MOD_TYPES[item.type] if item.type else None
        if column == 1:
            return item.dtl or MOD_DTLS[item.type][1]
        if column == 2:
            return rules.format_rtk_t(item.value)
        if column == 3:
            return item.reason
        return None
        
    def __checkstate_role(self, item, column):
        if column == 0:
            return QtCore.Qt.Checked if item.active else QtCore.Qt.Unchecked
        return None
        
    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsDropEnabled
        flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
        if index.column() == 0:
	        flags |= QtCore.Qt.ItemIsUserCheckable        
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
        for m in model.get_modifiers():
            self.add_item(m)
        
        if self.dirty:
            print('set model unsaved')
            model.unsaved = True
            self.dirty    = False
                        
## MODIFIER ITEM DELEGATE ##     
class ModifierDelegate(QtGui.QStyledItemDelegate):    
    def __init__(self, dstore, parent=None):
        super(ModifierDelegate, self).__init__(parent)        
        self.dstore = dstore
                    
    def createEditor(self, parent, option, index):
        if not index.isValid():            
            return None
        
        def __editor(column):
            edit = None
            if column == 0:
                edit = QtGui.QComboBox(parent)
                edit.activated.connect(self.commitAndCloseEditor)
            else:
                edit = QtGui.QLineEdit(parent)
                edit.editingFinished.connect(self.commitAndCloseEditor)
            return edit
         
        return __editor(index.column())       
        
    def setEditorData(self, editor, index):
        if not index.isValid():
            return
        
        item = index.model().data(index, QtCore.Qt.UserRole)
        
        def __skill_completer():
            all_skills = []
            for t in self.dstore.skills:
                all_skills.append(t.name)
            return QtGui.QCompleter(all_skills)
            
        def __weap_completer():
            pc = None
            if self.parent():
                pc = self.parent().pc
            aweaps = []
            for w in pc.get_weapons():
                aweaps.append(w.name)
            return QtGui.QCompleter(aweaps)
            
        def __set_edit_data(column):
            if column == 0:                
                cur_idx = -1
                for mk in MOD_TYPES.iterkeys():
                    if mk == 'none': continue
                    editor.addItem(MOD_TYPES[mk], mk)
                    if mk == item.type:
                        cur_idx = editor.count() - 1
                editor.setCurrentIndex(cur_idx)
                item.dtl = None
            elif column == 1:
                dtl = MOD_DTLS[item.type] if item.type else 'none'
                if dtl[0] == 'skill':
                    editor.setCompleter(__skill_completer())
                elif dtl[0] == 'aweap':
                    editor.setCompleter(__weap_completer())
                editor.setText(item.dtl)
            elif column == 2:
                editor.setText(rules.format_rtk_t(item.value))
            elif column == 3:
                editor.setText(item.reason)
            else:
                editor.setText("")
                
        __set_edit_data(index.column())
        
    def setModelData(self, editor, model, index):
        if not index.isValid():
            return False
                
        #item = model.data(index, QtCore.Qt.UserRole)
        def __set_itm_value(editor, column):
            if column == 0:
                idx = editor.currentIndex()
                return editor.itemData(idx)
            elif column == 1:
                return editor.text()                
            elif column == 2:
                return editor.text()
            elif column == 3:
                return editor.text()
            return None
                
        value = __set_itm_value(editor, index.column())
        
        return model.setData(index, value, QtCore.Qt.EditRole)
        
    def commitAndCloseEditor(self):
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor, QtGui.QAbstractItemDelegate.EndEditHint.NoHint)