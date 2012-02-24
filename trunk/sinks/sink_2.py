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

import dialogs

class Sink2(QtCore.QObject):
    def __init__(self, parent = None):
        self.form = parent

    def act_buy_merit(self):
        form = self.form
        
        dlg = dialogs.BuyPerkDialog(form.pc, 'merit',
                                    form.db_conn, form)
        dlg.exec_()
        form.update_from_model()
        
    def act_buy_flaw(self):
        form = self.form
        
        dlg = dialogs.BuyPerkDialog(form.pc, 'flaw',
                                    form.db_conn, form)
        dlg.exec_()
        form.update_from_model() 

    def act_edit_merit(self):
        form = self.form
        
        sel_idx = form.merit_view.selectionModel().currentIndex()
        if not sel_idx.isValid():
            return
        sel_itm = form.merit_view.model().data(sel_idx, QtCore.Qt.UserRole)
        
        dlg = dialogs.BuyPerkDialog(form.pc, 'merit',
                                    form.db_conn, form)

        dlg.set_edit_mode(True)        
        dlg.load_item(sel_itm)
        dlg.exec_()
        form.update_from_model()
    
    def act_edit_flaw(self):   
        form = self.form    
        
        sel_idx = self.flaw_view.selectionModel().currentIndex()
        if not sel_idx.isValid():
            return
        sel_itm = self.flaw_view.model().data(sel_idx, QtCore.Qt.UserRole)
        
        dlg = dialogs.BuyPerkDialog(self.pc, 'flaw',
                                    self.db_conn, form)

        dlg.load_item(sel_itm)
        dlg.set_edit_mode(True)        
        dlg.exec_()
        form.update_from_model()

    def act_del_merit(self):
        form = self.form
        
        sel_idx = form.merit_view.selectionModel().currentIndex()
        if not sel_idx.isValid():
            return
        sel_itm = self.merit_view.model().data(sel_idx, QtCore.Qt.UserRole)        
        self.remove_advancement_item(sel_itm.adv)        
        
    def act_del_flaw(self):
        form = self.form
        
        sel_idx = form.flaw_view.selectionModel().currentIndex()
        if not sel_idx.isValid():
            return
        sel_itm = form.flaw_view.model().data(sel_idx, QtCore.Qt.UserRole)
        form.remove_advancement_item(sel_itm.adv)        