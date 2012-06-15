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
        
    def connect_signals(self):
        self.bt_go_on.clicked.connect(self.accept)
        self.bt_new_school_1.clicked.connect(self.merit_plus_school )
        self.bt_new_school_2.clicked.connect(self.join_new_school   )
    
    def join_new_school(self):
        dlg = SchoolChoiceDlg(self.pc, self.dbconn, self)
        if dlg.exec_() == QtGui.QDialog.Rejected:
            #self.reject()
            return
                   
        school_nm  = dlg.get_school_name()
        school_obj = models.CharacterSchool(dlg.get_school_id())        
        school_obj.tags = dlg.get_school_tags()
        school_obj.school_rank = 0
        aff_def = self.parent().get_school_aff_def(school_obj.school_id)
        school_obj.affinity   = aff_def[0]
        school_obj.deficiency = aff_def[1]        
        
        self.pc.schools.append(school_obj)
        self.accept()
        
    def merit_plus_school(self):
        c = self.dbconn.cursor()
        
        query = '''SELECT perks.uuid, perks.name, perks.rule, perk_ranks.cost
                   FROM perks
                   INNER JOIN perk_ranks ON perks.uuid=perk_ranks.perk_uuid
                   WHERE perk_ranks.perk_rank=1 AND perks.name=?'''
        
        c.execute(query, [self.tr("Multiple Schools")])
        try:
            uuid, name, rule, cost = c.fetchone()       
            c.close()
            
            if not uuid or not cost: self.reject()            
                
            itm      = models.PerkAdv(uuid, 1, cost)
            itm.rule = rule
            itm.desc = unicode.format(self.tr("{0} Rank {1}, XP Cost: {2}"),
                                      self.tr("Multiple Schools"),
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

class SchoolChoiceDlg(QtGui.QDialog):
    def __init__(self, pc, dbconn, parent = None):
        super(SchoolChoiceDlg,self).__init__(parent)
        
        self.pc     = pc
        self.dbconn = dbconn
        
        self.school_nm = ''
        self.school_id = 0
        self.school_tg = []
                
        self.build_ui       ()
        self.setWindowTitle(self.tr("L5R: CM - Select School"))
        
    def build_ui(self):
        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(QtGui.QLabel(self.tr("Choose the school to join")))
        
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

        grp_ = QtGui.QGroupBox(self.tr("Notes"), self)
        hb_  = QtGui.QHBoxLayout(grp_)
        self.te_notes = QtGui.QTextEdit(self)
        self.te_notes.setReadOnly(True)
        hb_.addWidget(self.te_notes)        
        vbox.addWidget(grp_)
        
        self.bt_ok = QtGui.QPushButton(self.tr("Confirm"), self)
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
        
        query += """ order by name asc"""
        
        c.execute(query, [self.cb_clan.itemData(idx_)])
        
        self.cb_school.clear()
        def has_school(uuid):
            for s in self.pc.schools:
                if s.school_id == uuid:
                    return True
            return False
            
        for uuid, name in c.fetchall():
            if not has_school(uuid):
                self.cb_school.addItem(name, uuid)
            
        c.close()
        
    def on_school_change(self):
        idx_ = self.cb_school.currentIndex()       
        clan_idx_ = self.cb_clan.currentIndex()       
        c = self.dbconn.cursor()
        
        school_id = self.cb_school.itemData(idx_)
        self.school_tg = [self.cb_clan.itemText(clan_idx_).lower()]
        
        c.execute('''select tag from schools
                     where uuid=?''', [school_id])
        tag = c.fetchone()
        if tag:
            self.school_tg.append(tag[0])            
        
        query = """SELECT req_field, target_val
                   FROM requirements WHERE
                   ref_uuid=? AND req_type=? 
                   order by req_type asc"""
                   
        c.execute(query, [school_id, 'more'])
        self.te_notes.setHtml("")
        for req_field, target_val in c.fetchall():
            self.te_notes.setHtml(
            unicode.format(
            u"<em>{0}</em>", target_val))
        
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
                
        unmatched = []
        
        c = self.dbconn.cursor()
        
        query = """SELECT req_type, req_field,
                   min_val, max_val, target_val
                   FROM requirements WHERE
                   ref_uuid=? order by req_type asc"""
                   
        c.execute(query, [school_id])
        
        self.pc_skills = {}
        self.pc_rings  = []
        self.pc_traits = []
        
        for sk_id in self.pc.get_skills():
            self.pc_skills[sk_id] = self.pc.get_skill_rank(sk_id)
            
        for i in xrange(0, 5):
            self.pc_rings.append((i, self.pc.get_ring_rank(i)))
            
        for i in xrange(0, 8):
            self.pc_traits.append((i, self.pc.get_attrib_rank(i)))
        
        for rtype, rfield, min_, max_, trgt in c.fetchall():
            print (rtype, rfield, min_, max_, trgt)
            if rfield.startswith('*'):            
                if not self.match_wc_requirement(rtype, rfield, min_, max_, trgt):                     
                    unmatched.append( wc_requirement_to_string(rtype, rfield, min_, max_, trgt) )
            else:
                if not self.match_requirement(rtype, rfield, min_, max_, trgt):
                    unmatched.append( requirement_to_string(rtype, rfield, min_, max_, trgt) )
        
        c.close()
        
        return unmatched
        
    def match_requirement(self, rtype, rfield, min_, max_, trgt):
        if rfield == 'honor':
            return self.pc.get_honor() > min_
        if rfield == 'status':
            return self.pc.get_status() > min_
        if rfield == 'glory':
            return self.pc.get_glory() > min_        
        if rtype == 'ring':
            ring_id = models.ring_from_name(rfield)
            return self.pc.get_ring_rank(ring_id) >= min_
        if rtype == 'trait':
            trait_id = models.attrib_from_name(rfield)
            return self.pc.get_attrib_rank(trait_id) >= min_
        if rtype == 'skill':
            or_skills = rfield.split(';')
            if len(or_skills) > 1:
                ret = False
                for sk in or_skills:
                    ret = self.match_requirement(rtype, sk, min_, max_, trgt)
                    if ret: return True
                return False
                
            skill_id = dbutil.get_skill_id_from_name(self.dbconn, rfield)
            if not skill_id: return True
            if trgt and trgt not in self.pc.get_skill_emphases(skill_id):
                return False # missing emphases
            if (skill_id not in self.pc_skills or
                self.pc_skills[skill_id] < min_):
                return False
            
            self.pc_skills.pop(skill_id)
            return True
        if rtype == 'tag':
            return self.pc.has_tag(rfield)
        if rtype == 'rule':
            return self.pc.has_rule(rfield)
        return True
            
    def match_wc_requirement(self, rtype, rfield, min_, max_, trgt):
        got_req = -1
        if rtype == 'ring':
            if rfield == '*any': # any ring                
                for i in xrange(0, len(self.pc_rings)):
                    if self.pc_rings[i][1] >= min_:
                        got_req = i
            if got_req >= 0:
                del self.pc_rings[got_req]
                return True            
            return False
        if rtype == 'trait':
            if rfield == '*any': # any trait
                for i in xrange(0, len(self.pc_traits)):
                    if self.pc_traits[i][1] >= min_:
                        got_req = i
            if got_req >= 0:
                del self.pc_traits[got_req]
                return True                 
            return False
        if rtype == 'skill':
            if rfield == '*any': # any skills
                for k in self.pc_skills.iterkeys():
                    if self.pc_skills[k] >= min_:
                        got_req = k
            else:
                tag = rfield[1:]
                for k in self.pc_skills.iterkeys():
                    if not dbutil.has_tag(self.dbconn, k, tag):
                        continue
                    if self.pc_skills[k] >= min_:
                        got_req = k
                        
            if got_req >= 0:
                self.pc_skills.pop(got_req)
                return True  
            return False
        return True
        
def test():
    import sys
    app = QtGui.QApplication(sys.argv)

    dlg = NextRankDlg(None, None)
    dlg.show()

    sys.exit(app.exec_())
    
if __name__ == '__main__':
    test()
    