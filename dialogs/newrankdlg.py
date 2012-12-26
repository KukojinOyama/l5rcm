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

import dal
import dal.query
import models

class NextRankDlg(QtGui.QDialog):
    def __init__(self, pc, dstore, parent = None):
        super(NextRankDlg, self).__init__(parent)        
        self.pc     = pc
        self.dstore = dstore
        
        self.build_ui()
        self.connect_signals()
        
        #self.setWindowFlags(QtCore.Qt.Tool)
        self.setWindowTitle(self.tr("L5R: CM - Advance Rank"))
        
    def build_ui(self):
        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(QtGui.QLabel(self.tr("""\
You can now advance your Rank,
what would you want to do?
                                    """)))
        self.bt_go_on        = QtGui.QPushButton(
                               self.tr("Advance in my current school")
                               )
        self.bt_new_school_1 = QtGui.QPushButton(
                               self.tr("Buy 'Multiple School' advantage\n"
                                       "and join a new school"))
        self.bt_new_school_2 = QtGui.QPushButton(
                               self.tr("Just join a new school"))
                               
        for bt in [self.bt_go_on, self.bt_new_school_1, self.bt_new_school_2]:
            bt.setMinimumSize(QtCore.QSize(0, 38))
        
        vbox.addWidget(self.bt_go_on       )
        vbox.addWidget(self.bt_new_school_1)
        vbox.addWidget(self.bt_new_school_2)
        
        vbox.setSpacing(12)
        
        # check if the PC is following an alternate path
        if self.pc.get_school().is_path:
            # offer to going back
            self.bt_go_on.setText( self.tr("Go back to your old school"))            
        
    def connect_signals(self):
        self.bt_go_on.clicked.connect(self.simply_go_on)
        self.bt_new_school_1.clicked.connect(self.merit_plus_school)
        self.bt_new_school_2.clicked.connect(self.join_new_school)
    
    def join_new_school(self):
        dlg = SchoolChoiceDlg(self.pc, self.dstore, self)
        if dlg.exec_() == QtGui.QDialog.Rejected:
            #self.reject()
            return
        sc = dal.query.get_school(self.dstore, dlg.get_school_id())
        
        school_nm  = sc.name
        school_obj = models.CharacterSchool(sc.id)
        school_obj.tags = sc.tags
        school_obj.school_rank = 0

        school_obj.affinity   = sc.affinity
        school_obj.deficiency = sc.deficiency
               
        self.pc.schools.append(school_obj)
        
        # check for alternate path
        if school_obj.has_tag('alternate'):
            school_obj.is_path = True
            school_obj.path_rank = self.pc.get_insight_rank()

        self.pc.set_current_school_id(sc.id)
        
        self.accept()        
               
    def merit_plus_school(self):       
        mult_school_merit = dal.query.get_merit(self.dstore, 'multiple_schools')
        try:
            uuid = mult_school_merit.id
            name = mult_school_merit.name
            rule = mult_school_merit.id            
            cost = mult_school_merit.get_rank_value(1)
            
            if not uuid or not cost: self.reject()            
                
            itm      = models.PerkAdv(uuid, 1, cost)
            itm.rule = rule
            itm.desc = unicode.format(self.tr("{0} Rank {1}, XP Cost: {2}"),
                                      name,
                                      1, itm.cost)
                                  
            if (itm.cost + self.pc.get_px()) > self.pc.exp_limit:
                QtGui.QMessageBox.warning(self, self.tr("Not enough XP"),
                self.tr("Cannot purchase.\nYou've reached the XP Limit."))
                self.reject()
                return
                
            self.pc.add_advancement(itm)
            self.join_new_school()
        except:
            self.reject()
            
    def simply_go_on(self):
        # check if the PC is following an alternate path
        if self.pc.get_school().is_path:
            # the PC want to go back to the old school.
            # find the first school that is not a path
            for s in reversed(self.pc.schools):
                if not s.is_path:
                    self.pc.set_current_school_id(s.school_id)
        self.accept()

class SchoolChoiceDlg(QtGui.QDialog):
    def __init__(self, pc, dstore, parent = None):
        super(SchoolChoiceDlg,self).__init__(parent)
        
        self.pc     = pc
        self.dstore = dstore
        
        self.school_nm  = ''
        self.school_id  = 0
        self.school_tg  = []
        self.schools    = []
                
        self.build_ui       ()
        self.setWindowTitle(self.tr("L5R: CM - Select School"))
        
    def build_ui(self):
        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(QtGui.QLabel(self.tr("Choose the school or path to join")))
        
        grp_ = QtGui.QGroupBox(self.tr("Clan"), self)
        hb_  = QtGui.QHBoxLayout(grp_)
        self.cb_clan = QtGui.QComboBox(self)
        hb_.addWidget(self.cb_clan)        
        vbox.addWidget(grp_)
        
        self.cb_clan.currentIndexChanged.connect(self.on_clan_change)        
        
        grp_ = QtGui.QGroupBox(self.tr("School"), self)
        hb_  = QtGui.QHBoxLayout(grp_)
        self.cb_school = QtGui.QComboBox(self)
        hb_.addWidget(self.cb_school)        
        vbox.addWidget(grp_)
        
        self.cb_school.currentIndexChanged.connect(self.on_school_change)
        
        grp_ = QtGui.QGroupBox(self.tr("Filters"), self)
        vb_  = QtGui.QVBoxLayout(grp_)
        self.cx_base_schools = QtGui.QCheckBox(self.tr("Base schools"), self)
        self.cx_advc_schools = QtGui.QCheckBox(self.tr("Advanced schools"), self)
        self.cx_path_schools = QtGui.QCheckBox(self.tr("Alternate paths"), self)
        vb_.addWidget(self.cx_base_schools)
        vb_.addWidget(self.cx_advc_schools)
        vb_.addWidget(self.cx_path_schools)
        vbox.addWidget(grp_)
        
        self.cx_base_schools.toggled.connect(self.refresh_data)
        self.cx_advc_schools.toggled.connect(self.refresh_data)
        self.cx_path_schools.toggled.connect(self.refresh_data)
        
        grp_ = QtGui.QGroupBox(self.tr("Notes"), self)
        hb_  = QtGui.QHBoxLayout(grp_)
        self.te_notes = QtGui.QTextEdit(self)
        self.te_notes.setReadOnly(True)
        hb_.addWidget(self.te_notes)        
        vbox.addWidget(grp_)
        
        self.bt_ok = QtGui.QPushButton(self.tr("Confirm"), self)
        #self.bt_ok.setMaximumSize(QtCore.QSize(200, 65000))
        vbox.addWidget(self.bt_ok)
        
        self.setContentsMargins(12,0,12,0)
        
        self.bt_ok.clicked.connect(self.on_accept)
        
        self.cx_base_schools.setChecked(True)
                    
    def refresh_data(self):
        clans   = []
        schools = []
        
        if self.cx_base_schools.isChecked():
            schools += dal.query.get_base_schools(self.dstore)
        if self.cx_advc_schools.isChecked():
            schools += [x for x in self.dstore.schools if 'advanced' in x.tags]
        if self.cx_path_schools.isChecked():
            schools += [x for x in self.dstore.schools if 'alternate' in x.tags]
        
        self.schools = schools
        
        self.cb_clan.clear()
        for c in [x.clanid for x in schools]:
            if c not in clans:
                clans.append(c)
                clan = dal.query.get_clan(self.dstore, c)
                self.cb_clan.addItem(clan.name, clan.id)
                                        
    def on_clan_change(self):    
        idx_ = self.cb_clan.currentIndex()
               
        clan_id = self.cb_clan.itemData(idx_)
        schools = [ x for x in self.schools if x.clanid == clan_id ]
        
        if self.pc.has_tag('bushi'):
            schools = [ x for x in schools if 'shugenja' not in x.tags ]
        elif self.pc.has_tag('shugenja'):
            schools = [ x for x in schools if 'bushi' not in x.tags ]
        
        self.cb_school.clear()
        def has_school(uuid):
            for s in self.pc.schools:
                if s.school_id == uuid:
                    return True
            return False
                    
        for school in schools:
            if not has_school(school.id):
                self.cb_school.addItem(school.name, school.id)
        
    def on_school_change(self):
        idx_ = self.cb_school.currentIndex()       
        clan_idx_ = self.cb_clan.currentIndex()
        
        clan_id = self.cb_clan.itemData(clan_idx_)        
        school_id = self.cb_school.itemData(idx_)
                
        clan   = dal.query.get_clan  (self.dstore, clan_id)
        school = dal.query.get_school(self.dstore, school_id)
        
        if clan and school:
            self.school_tg = [clan.id] + school.tags
                                    
            more = ''
            try:
                more = [ x for x in school.require if x.type == 'more' ][0]
            except:
                pass                   

            self.te_notes.setHtml("")
            self.te_notes.setHtml(
                unicode.format(
                u"<em>{0}</em>", more))
        
    def on_accept(self):
        idx_           = self.cb_school.currentIndex()
        self.school_id = self.cb_school.itemData(idx_)
        self.school_nm = self.cb_school.itemText(idx_)
        
        if self.school_id:
            unmatched = self.check_requirements(self.school_id)

            if len(unmatched) == 0:
                self.accept()
            else:
                msgBox = QtGui.QMessageBox(self)
                msgBox.setWindowTitle('L5R: CM')
                msgBox.setText(self.tr("You don't have the requirements to join this school."))
                msgBox.setInformativeText(self.tr("You miss the following requirements\n") +
                                          '\n'.join(unmatched))
                msgBox.exec_()
                
                self.reject()
                
    def get_school_id(self):
        return self.school_id

    def get_school_name(self):
        return self.school_nm

    def get_school_tags(self):
        return self.school_tg
        
    def check_requirements(self, school_id):
        def requirement_to_string(rtype, rfield, min_, max_, trgt):
            if rtype == 'ring' or rtype == 'trait':
                return '%s: %s' % (rfield.capitalize(), min_)
            if rtype == 'skill':
                rfield = rfield.replace(';', ' or ')
                if trgt:
                    return '%s (%s): %s' % (rfield.capitalize(), trgt, min_)
                else:
                    return '%s %s' % (rfield.capitalize(), min_)
            if rtype == 'tag' or rtype == 'rule':
                return rfield.replace('_' , ' ').capitalize()
                
        def wc_requirement_to_string(rtype, rfield, min_, max_, trgt):
            if rtype == 'ring' and rfield == '*any':
                return self.tr("Any ring: %s") % min_
            if rtype == 'trait' and rfield == '*any':
                return self.tr("Any trait: %s") % min_
            if rtype == 'skill' and rfield == '*any':
                return self.tr("Any skill: %s") % min_
            elif rtype == 'skill':
                tag = rfield[1:].capitalize()
                return self.tr("Any %s skill: %s") % (tag, min_)
            return self.tr("N/A")
            
        def req_to_string(req):
            #if not hasattr(req, 'field'):
            #    return 'TODO'
            #if req.field.startswith('*'):
            #    return wc_requirement_to_string(req.type, req.field, req.min, req.max, req.trg)
            #return requirement_to_string(req.type, req.field, req.min, req.max, req.trg)
            return unicode(req)
            
        unmatched = []
        
        school = dal.query.get_school(self.dstore, school_id)
               
        pc = models.CharacterSnapshot(self.pc)
        
        for req in school.require:                                   
            if not req.match(pc, self.dstore):
                unmatched.append( req_to_string(req) )                
        return unmatched        
        
def test():
    import sys
    app = QtGui.QApplication(sys.argv)

    dlg = NextRankDlg(None, None)
    dlg.show()

    sys.exit(app.exec_())
    
if __name__ == '__main__':
    test()
    