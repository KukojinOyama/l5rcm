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

import dbutil
import models

class NextRankDlg(QtGui.QDialog):
    def __init__(self, pc, conn, parent = None):
        super(NextRankDlg, self).__init__(parent)        
        self.pc     = pc
        self.dbconn = conn
        
        self.build_ui()
        self.connect_signals()
        
        #self.setWindowFlags(QtCore.Qt.Tool)
        self.setWindowTitle('L5R: CM - Advance Rank')
        
    def build_ui(self):
        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(QtGui.QLabel("""\
You can now advance your Rank,
what would you want to do?
                                    """))
        self.bt_go_on        = QtGui.QPushButton(
                               "Advance in my current school"
                               )
        self.bt_new_school_1 = QtGui.QPushButton(
                               "Buy 'Multiple School' advantage\n"
                               "and join a new school")
        self.bt_new_school_2 = QtGui.QPushButton(
                               "Just join a new school")
                               
        for bt in [self.bt_go_on, self.bt_new_school_1, self.bt_new_school_2]:
            bt.setMinimumSize(QtCore.QSize(0, 38))
        
        vbox.addWidget(self.bt_go_on       )
        vbox.addWidget(self.bt_new_school_1)
        vbox.addWidget(self.bt_new_school_2)
        
        vbox.setSpacing(12)
        
    def connect_signals(self):
        self.bt_go_on.clicked.connect(self.accept)
        self.bt_new_school_1.clicked.connect(self.merit_plus_school )
        self.bt_new_school_2.clicked.connect(self.join_new_school   )
    
    def join_new_school(self):
        dlg = SchoolChoiceDlg(self.pc, self.dbconn, self)
        if dlg.exec_() == QtGui.QDialog.Rejected:
            self.reject()
                   
        school_nm  = dlg.get_school_name()
        school_obj = models.CharacterSchool(dlg.get_school_id())        
        school_obj.tags = dlg.get_school_tags()
        school_obj.school_rank = 0
        
        self.pc.schools.append(school_obj)
        self.accept()
        
    def merit_plus_school(self):
        c = self.dbconn.cursor()
        
        query = '''SELECT perks.uuid, perks.name, perks.rule, perk_ranks.cost
                   FROM perks
                   INNER JOIN perk_ranks ON perks.uuid=perk_ranks.perk_uuid
                   WHERE perk_ranks.perk_rank=1 AND perks.name=?'''
                   
        
        c.execute(query, ["Multiple Schools"])
        try:
            uuid, name, rule, cost = c.fetchone()       
            c.close()
            
            if not uuid or not cost: self.reject()
            
            if (cost + self.pc.get_px()) > self.pc.exp_limit:
                QtGui.QMessageBox.warning(self, "Not enough XP",
                "Cannot purchase.\nYou've reached the XP Limit.")                
                self.reject()
                return
                
            itm      = models.PerkAdv(uuid, 1, cost)
            itm.rule = rule
            itm.desc = str.format("{0} Rank {1}, XP Cost: {2}",
                                  "Multiple Schools",
                                  1, itm.cost)
            self.pc.add_advancement(itm)

            self.join_new_school()
        except:
            self.reject()

class SchoolChoiceDlg(QtGui.QDialog):
    def __init__(self, pc, dbconn, parent = None):
        super(SchoolChoiceDlg,self).__init__(parent)
        
        self.pc     = pc
        self.dbconn = dbconn
        
        self.school_nm = ''
        self.school_id = 0
        self.school_tg = []
                
        self.build_ui       ()
        self.setWindowTitle('L5R: CM - Select School')
        
    def build_ui(self):
        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(QtGui.QLabel("Choose the school to join"))
        
        grp_ = QtGui.QGroupBox("Clan", self)
        hb_  = QtGui.QHBoxLayout(grp_)
        self.cb_clan = QtGui.QComboBox(self)
        hb_.addWidget(self.cb_clan)        
        vbox.addWidget(grp_)
        
        self.cb_clan.currentIndexChanged.connect(self.on_clan_change)
        
        grp_ = QtGui.QGroupBox("School", self)
        hb_  = QtGui.QHBoxLayout(grp_)
        self.cb_school = QtGui.QComboBox(self)
        hb_.addWidget(self.cb_school)        
        vbox.addWidget(grp_)
        
        self.bt_ok = QtGui.QPushButton("Confirm", self)
        self.bt_ok.setMaximumSize(QtCore.QSize(200, 65000))        
        vbox.addWidget(self.bt_ok)
        
        self.bt_ok.clicked.connect(self.on_accept)
        
        c = self.dbconn.cursor()
        c.execute('''SELECT uuid, name from clans''')
        for uuid, name in c.fetchall():
            self.cb_clan.addItem(name, uuid)
        c.close()
                        
    def on_clan_change(self):    
        idx_ = self.cb_clan.currentIndex()
        
        c = self.dbconn.cursor()
        
        query = """SELECT uuid, name FROM schools
                   WHERE clan_id=?"""
        
        if self.pc.has_tag('bushi'):
            query += """ AND tag NOT LIKE '%shugenja%'"""
        elif self.pc.has_tag('shugenja'):
            query += """ AND tag NOT LIKE '%bushi%'"""
        
        c.execute(query, [self.cb_clan.itemData(idx_)])
        
        self.cb_school.clear()
        for uuid, name in c.fetchall():
            self.cb_school.addItem(name, uuid)
            
        c.close()
        
    def on_accept(self):
        idx_           = self.cb_school.currentIndex()
        self.school_id = self.cb_school.itemData(idx_)
        self.school_nm = self.cb_school.itemText(idx_)
        
        if self.school_id:
            self.accept()
        
    def get_school_id(self):
        return self.school_id

    def get_school_name(self):
        return self.school_nm

    def get_school_tags(self):
        return self.school_tg
        
def test():
    import sys
    app = QtGui.QApplication(sys.argv)

    dlg = NextRankDlg(None, None)
    dlg.show()

    sys.exit(app.exec_())
    
if __name__ == '__main__':
    test()
    