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

import os
import models
import dialogs
import osutil

class Sink4(QtCore.QObject):
    def __init__(self, parent = None):
        super(Sink4, self).__init__(parent)
        self.form = parent
        
    def add_new_modifier(self):    
        item = models.ModifierModel()
        self.form.pc.add_modifier(item)
        dlg = dialogs.ModifierDialog(self.form.pc, self.form.dstore, self.form)
        dlg.load_modifier(item)
        if dlg.exec_() == QtGui.QDialog.DialogCode.Accepted:
            self.form.update_from_model()
        
    def edit_selected_modifier(self):        
        index = self.form.mod_view.selectionModel().currentIndex()
        if not index.isValid():
            return               
        item = index.model().data(index, QtCore.Qt.UserRole)
        dlg  = dialogs.ModifierDialog(self.form.pc, self.form.dstore, self.form)
        dlg.load_modifier(item)
        if dlg.exec_() == QtGui.QDialog.DialogCode.Accepted:
            self.form.update_from_model()        
            
    def remove_selected_modifier(self):
        index = self.form.mod_view.selectionModel().currentIndex()
        if not index.isValid():
            return            
        item = index.model().data(index, QtCore.Qt.UserRole)
        self.form.pc.modifiers.remove(item)
        self.form.update_from_model()
        
    # DATA MENU
    def import_data_act(self):
        data_pack_file = self.form.select_import_data_pack()
        if data_pack_file:
            self.form.import_data_pack(data_pack_file)
        
    def manage_data_act(self):
        dlg = dialogs.ManageDataPackDlg(self.form.dstore, self.form)
        if dlg.exec_() == QtGui.QDialog.DialogCode.Accepted:
            self.form.update_data_blacklist()
            self.reload_data_act           ()
    
    def open_data_dir_act(self):
        path = os.path.normpath(osutil.get_user_data_path())
        if not os.path.exists(path):
            os.makedirs(path)            
        osutil.portable_open(path)
        
    def reload_data_act(self):
        self.form.reload_data  ()
        self.form.create_new_character()
        
    def add_equipment(self):        
        equip_list = self.form.pc.get_property('equip', [])
        equip_list.append( self.tr('Doubleclick to edit') )
        self.form.update_from_model()
        
    def remove_selected_equipment(self):    
        index = self.form.equip_view.selectionModel().currentIndex()
        if not index.isValid():
            return            
        item = index.model().data(index, QtCore.Qt.UserRole)
        
        equip_list = self.form.pc.get_property('equip')
        if equip_list:
            equip_list.remove(item)
        
        self.form.update_from_model()           
        
    def on_money_value_changed(self, value):
        self.form.pc.set_property('money', value)        