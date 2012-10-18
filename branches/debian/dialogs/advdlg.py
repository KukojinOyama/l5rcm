#!/usr/bin/python
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

import models.advances as advances
import models
import string
import dal
import dal.query

from models.chmodel import ATTRIBS, RINGS
from PySide import QtCore, QtGui

import rules

class BuyAdvDialog(QtGui.QDialog):
    def __init__(self, pc, tag, dstore, parent = None):
        super(BuyAdvDialog, self).__init__(parent)
        self.tag = tag
        self.adv = None
        self.pc  = pc
        self.dstore = dstore
        self.quit_on_accept = False
        self.build_ui()        
        self.connect_signals()
        self.load_data()        

    def build_ui(self):
        grid = QtGui.QGridLayout(self)

        titles = dict(attrib=self.tr('Buy Attribute rank'),
                      skill= self.tr('Buy Skill rank'    ),
                      void=  self.tr('Buy Void rank'     ),
                      emph=  self.tr('Buy Skill emphasys'),
                      kata=  self.tr('Buy Kata'          ),
                      kiho=  self.tr('Buy Kiho'          ),
                      spell= self.tr('Buy Spell'         ))

        labels = dict(attrib=(self.tr('Choose Attribute' ),  None),
                      skill= (self.tr('Choose Skill Type'), self.tr('Choose Skill'   )),
                      emph=  (self.tr('Choose Skill'     ), self.tr('Choose Emphasis')),
                      kata=  (self.tr('Choose Kata'      ), self.tr('Description'    )),
                      kiho=  (self.tr('Choose Kiho'      ), None),
                      spell= (self.tr('Choose Spell'     ), None))

        self.setWindowTitle( titles[self.tag] )

        self.widgets = dict(attrib=(QtGui.QComboBox(self), None),
                            skill =(QtGui.QComboBox(self), QtGui.QComboBox(self)),
                            emph  =(QtGui.QComboBox(self), QtGui.QLineEdit(self)),
                            kata  =(QtGui.QComboBox(self), QtGui.QTextEdit(self)),
                            kiho  =(None, None),
                            spell =(None, None))

        for t in self.widgets.itervalues():
            if t[0]: t[0].setVisible(False)
            if t[1]: t[1].setVisible(False)

        if self.tag in self.widgets:
            for i in xrange(0, 2):
                if labels[self.tag][i] is not None:
                    lb = QtGui.QLabel(labels[self.tag][i], self)
                    wd = self.widgets[self.tag][i]
                    wd.setVisible(True)
                    grid.addWidget(lb, i, 0)
                    grid.addWidget(wd, i, 1, 1, 3)

        self.lb_from = QtGui.QLabel(self.tr('Make your choice'), self)
        self.lb_cost = QtGui.QLabel(self.tr('Cost: 0'         ), self)

        self.bt_buy   = QtGui.QPushButton(self.tr('Buy'  ), self)
        self.bt_close = QtGui.QPushButton(self.tr('Close'), self)

        grid.addWidget(self.lb_from, 3, 0, 1, 3)
        grid.addWidget(self.lb_cost, 4, 0, 1, 3)
        grid.addWidget(self.bt_buy,  5, 2, 1, 1)
        grid.addWidget(self.bt_close,  5, 3, 1, 1)
        
    def cleanup(self):
        self.widgets = {}        

    def load_data(self):
        if self.tag == 'attrib':
            cb = self.widgets[self.tag][0]
            cb.addItem(self.tr('Stamina'     ), ATTRIBS.STAMINA     )
            cb.addItem(self.tr('Willpower'   ), ATTRIBS.WILLPOWER   )
            cb.addItem(self.tr('Reflexes'    ), ATTRIBS.REFLEXES    )
            cb.addItem(self.tr('Awareness'   ), ATTRIBS.AWARENESS   )
            cb.addItem(self.tr('Strength'    ), ATTRIBS.STRENGTH    )
            cb.addItem(self.tr('Perception'  ), ATTRIBS.PERCEPTION  )
            cb.addItem(self.tr('Agility'     ), ATTRIBS.AGILITY     )
            cb.addItem(self.tr('Intelligence'), ATTRIBS.INTELLIGENCE)            
        elif self.tag == 'void':
            self.on_void_select()
        elif self.tag == 'skill':           
            cb = self.widgets[self.tag][0]
            for t in self.dstore.skcategs:
                cb.addItem( t.name, t.id )
        elif self.tag == 'emph':
            cb = self.widgets[self.tag][0]
            for id in self.pc.get_skills():
                sk = dal.query.get_skill(self.dstore, id)
                cb.addItem(sk.name, sk.id)

            self.lb_cost.setText(self.tr('Cost: 2 exp'))
            self.lb_from.setVisible(False)
        elif self.tag == 'kata':
            cb = self.widgets[self.tag][0]
            te = self.widgets[self.tag][1]
            
            te.setLineWrapMode(QtGui.QTextEdit.WidgetWidth)
            te.setReadOnly(True)
                       
            for kata in self.dstore.katas:
                if not self.pc.has_kata(kata.id):
                    cb.addItem( kata.name, kata.id )
            
    def fix_skill_id(self, uuid):
        if self.tag == 'emph':
            cb = self.widgets[self.tag][0]
            sk = dal.query.get_skill(self.dstore, uuid)
            cb.addItem(sk.name, sk.id)
            cb.setCurrentIndex(cb.count()-1)
            cb.setEnabled(False)
            
            self.quit_on_accept = True

    def connect_signals(self):
        if self.tag == 'attrib':
            cb = self.widgets[self.tag][0]
            cb.currentIndexChanged.connect( self.on_attrib_select )
        elif self.tag == 'skill':
            cb1 = self.widgets[self.tag][0]
            cb2 = self.widgets[self.tag][1]
            cb1.currentIndexChanged.connect( self.on_skill_type_select )
            cb2.currentIndexChanged.connect( self.on_skill_select )
        elif self.tag == 'kata':
            cb = self.widgets[self.tag][0]
            cb.currentIndexChanged.connect( self.on_kata_select )

        self.bt_buy.clicked.connect  ( self.buy_advancement )
        self.bt_close.clicked.connect( self.close           )

    def on_void_select(self):
        cur_value = self.pc.get_ring_rank( RINGS.VOID )
        new_value = cur_value + 1

        cost = self.pc.void_cost * new_value
        if self.pc.has_rule('enlightened'):
            cost -= 2

        self.lb_from.setText('From %d to %d' % (cur_value, new_value))
        self.lb_cost.setText('Cost: %d exp' % cost)

        self.adv = advances.VoidAdv(cost)
        self.adv.desc = (self.tr('Void Ring, Rank {0} to {1}. Cost: {2} xp')
                         .format( cur_value, new_value, self.adv.cost ))

    def on_attrib_select(self, text = ''):
        cb = self.widgets['attrib'][0]
        idx = cb.currentIndex()
        attrib = cb.itemData(idx)
        text   = cb.itemText(idx)
        cur_value = self.pc.get_attrib_rank( attrib )
        new_value = cur_value + 1

        ring_id = models.get_ring_id_from_attrib_id(attrib)
        ring_nm = models.ring_name_from_id(ring_id)

        cost = self.pc.get_attrib_cost( attrib ) * new_value
        if self.pc.has_rule('elem_bless_%s' % ring_nm):
            cost -= 1

        self.lb_from.setText(self.tr('From {0} to {1}')
                             .format(cur_value, new_value))
        self.lb_cost.setText(self.tr('Cost: {0} exp')
                             .format(cost))

        self.adv = advances.AttribAdv(attrib, cost)
        self.adv.desc = (self.tr('{0}, Rank {1} to {2}. Cost: {3} xp')
                         .format( text, cur_value, new_value, self.adv.cost ))

    def on_skill_type_select(self, text = ''):
        cb1   = self.widgets['skill'][0]
        cb2   = self.widgets['skill'][1]
        idx   = cb1.currentIndex()
        type_ = cb1.itemData(idx)
        
        avail_skills = dal.query.get_skills(self.dstore, type_)
        cb2.clear()
        
        for sk in avail_skills:
            if sk.id not in self.pc.get_skills():
                cb2.addItem( sk.name, sk.id )

    def on_skill_select(self, text = ''):        
        cb2  = self.widgets['skill'][1]
        idx  = cb2.currentIndex()
        
        uuid = cb2.itemData(idx)
        text = cb2.itemText(idx)
        
        cb1  = self.widgets['skill'][0]
        type_= cb1.itemData(cb1.currentIndex())

        cur_value = self.pc.get_skill_rank( uuid )
        new_value = cur_value + 1

        cost = new_value
        
        print('pc is obtuse? {0}'.format(self.pc.has_rule('obtuse')))
        print('skill type: {0}'.format(type_))
        print('skill uuid: {0}'.format(uuid))
        
        if (self.pc.has_rule('obtuse') and
            type_ == 'high' and 
            uuid != 'investigation' and # investigation
            uuid != 'medicine'):        # medicine
            
            # double the cost for high skill
            # other than medicine and investigation
            cost *= 2   
                
        self.lb_from.setText(self.tr('From {0} to {1}').format(cur_value, new_value))
        self.lb_cost.setText(self.tr('Cost: {0} exp').format(cost))

        self.adv = advances.SkillAdv(uuid, cost)
        self.adv.rule = dal.query.get_mastery_ability_rule(self.dstore, uuid, new_value)
        self.adv.desc = (self.tr('{0}, Rank {1} to {2}. Cost: {3} xp')
                         .format( text, cur_value, new_value, self.adv.cost ))
        
    def on_kata_select(self, text = ''):
        cb  = self.widgets['kata'][0]
        te  = self.widgets['kata'][1]
        idx  = cb.currentIndex()
        uuid = cb.itemData(idx)
        text = cb.itemText(idx)
        
        kata = dal.query.get_kata(self.dstore, uuid)
        requirements = kata.require
               
        self.lb_from.setText(self.tr('Mastery: {0} {1}').format(kata.element, kata.mastery))
        self.lb_cost.setText(self.tr('Cost: {0} exp').format(kata.mastery))
        
        # te.setText("")
        html = unicode.format(u"<p><em>{0}</em></p>", kata.desc)        
        
        # CHECK REQUIREMENTS
        ring_id  = models.ring_from_name(kata.element)
        ring_val = self.pc.get_ring_rank(ring_id)
        
        self.adv = None
        
        ok = len(requirements) == 0
        for req in requirements:
            if self.pc.has_tag(req.field) or self.pc.has_rule(req.field):
                ok = True
                break        
        
        if not ok:
            html += self.tr(
                    "<p><strong>"
                    "To Buy this kata you need to match "
                    "at least one of there requirements:"
                    "</strong></p>")
                    
            html += unicode.format(u"<p><ul>{0}</ul></p>", 
                          ''.join(['<li>{0}</li>'.format(x.text)
                                  for x in requirements]))
                     
        ok = ok and ring_val >= kata.mastery                     
        if not ok:
            html += unicode.format(self.tr("\n<p>You need a value of {0} in your {1} Ring</p>"),
                               kata.mastery, kata.element)
        else:
            self.adv = models.KataAdv(uuid, kata.id, kata.mastery)
            self.adv.desc = self.tr('{0}, Cost: {1} xp').format( kata.name, self.adv.cost )
            
        self.bt_buy.setEnabled(ok)           
        te.setHtml(html)

    def buy_advancement(self):

        if self.adv and ((self.adv.cost + self.pc.get_px()) > 
                         self.pc.exp_limit):
            QtGui.QMessageBox.warning(self, self.tr("Not enough XP"),
            self.tr("Cannot purchase.\nYou've reached the XP Limit."))
            self.close()
            return

        if self.tag == 'attrib':
            self.pc.add_advancement( self.adv )
            self.on_attrib_select()
        elif self.tag == 'void':
            self.pc.add_advancement( self.adv )
            self.on_void_select()
        elif self.tag == 'skill':
            self.pc.add_advancement( self.adv )
            self.on_skill_select()
        elif self.tag == 'emph':
            cb = self.widgets[self.tag][0]
            tx = self.widgets[self.tag][1]
            sk_name = cb.itemText( cb.currentIndex() )
            sk_uuid = cb.itemData( cb.currentIndex() )
            self.adv = advances.SkillEmph(sk_uuid, tx.text(), 2)
            self.adv.desc = (self.tr('{0}, Skill {1}. Cost: {2} xp')
                            .format( tx.text(), sk_name, self.adv.cost ))
            self.pc.add_advancement( self.adv )
            tx.setText('')
        elif self.tag == 'kata':
            self.pc.add_advancement( self.adv )
            cb = self.widgets[self.tag][0]
            cb.removeItem(cb.currentIndex())
            
        if self.quit_on_accept:
            self.close()
            
    def closeEvent(self, event):
        self.cleanup()

def check_all_done(cb_list):
    # check that all the choice have been made
    for cb in cb_list:
        if cb.currentIndex() < 0:
            return False
    return True

def check_all_done_2(le_list):
    for le in le_list:
        if len(le.text()) == 0:
            return False
    return True

def check_all_different(cb_list):
    # check that all the choices are different
    for i in xrange(0, len(cb_list)-1):
        cb = cb_list[i]
        id = cb.itemData(cb.currentIndex())
        for j in xrange(i+1, len(cb_list)):
            cb2 = cb_list[j]
            id2 = cb2.itemData(cb2.currentIndex())

            if id2 == id:
                return False
    return True

def check_already_got(list1, list2):
    # check if you already got this item
    for id in list1:
        if id in list2:
            return True
    return False

class SelWcSkills(QtGui.QDialog):
    def __init__(self, pc, dstore, parent = None):
        super(SelWcSkills, self).__init__(parent)
        self.pc  = pc
        self.dstore = dstore
        self.cbs    = []
        self.les    = []
        self.error_bar = None
        self.build_ui()
        self.connect_signals()
        self.load_data()

    def build_ui(self):
        self.setWindowTitle(self.tr('Choose School Skills'))

        grid = QtGui.QGridLayout(self)
        grid.addWidget( QtGui.QLabel(self.tr("<i>Your school has granted you \
                                             the right to choose some skills.</i> \
                                             <br/><b>Choose with care.</b>"), self),
                                      0, 0, 1, 3)
        grid.setRowStretch(0,2)

        self.bt_ok     = QtGui.QPushButton(self.tr('Ok'    ), self)
        self.bt_cancel = QtGui.QPushButton(self.tr('Cancel'), self)
        
        # TODO: translate skill category

        row_ = 2
        for ws in self.pc.get_pending_wc_skills():                    
            lb = ''
            wl = ws.wildcards
            if len(ws.wildcards):
                or_wc  = [x.value for x in wl if not x.modifier or x.modifier == 'or']
                not_wc = [x.value for x in wl if x.modifier and x.modifier == 'not'  ]
                
                sw1 = self.tr(' or ' ).join (or_wc)
                sw2 = ', '.join(not_wc)
                
                if ( wl[0].value == 'any' ):
                    sw1 = 'one'
                
                if len(not_wc):
                    lb = self.tr('Any {0}, not {1} skill (rank {2}):').format(sw1, sw2, ws.rank)
                else:
                    lb = self.tr('Any {0} skill (rank {1}):').format(sw1, ws.rank)

            grid.addWidget( QtGui.QLabel(lb, self), row_, 0 )

            cb = QtGui.QComboBox(self)
            self.cbs.append(cb)
            grid.addWidget(cb, row_, 1, 1, 2)

            row_ += 1

        for s in self.pc.get_pending_wc_emphs():
            lb = self.tr("{0}'s Emphases: ").format(dal.query.get_skill(self.dstore, s).name)

            grid.addWidget( QtGui.QLabel(lb, self), row_, 0 )

            le = QtGui.QLineEdit(self)
            self.les.append(le)
            grid.addWidget( le, row_, 1, 1, 2)

            row_ += 1

        self.error_bar = QtGui.QLabel(self)
        self.error_bar.setVisible(False)
        grid.addWidget(self.error_bar, row_, 0, 1, 3)

        grid.addWidget( self.bt_ok,     row_+1, 1)
        grid.addWidget( self.bt_cancel, row_+1, 2)
      
    def cleanup(self):
        self.cbs    = []
        self.les    = []
        self.error_bar = None    

    def load_data(self):
        i = 0        
        for ws in self.pc.get_pending_wc_skills():
            outcome = []
            wl = ws.wildcards
            
            for w_ in wl:                    
                if w_.value == 'any':
                    outcome += self.dstore.skills
                else:
                    print('search skills with tag {0}'.format(w_.value))                    
                    skills_by_tag = [x for x in self.dstore.skills if w_.value in x.tags]
                    if not w_.modifier or w_.modifier == 'or':
                        outcome += skills_by_tag
                    elif w_.modifier == 'not':
                        outcome = [x for x in outcome if x not in skills_by_tag]

            for sk in outcome:
                if sk.id not in self.pc.get_skills():
                    self.cbs[i].addItem( sk.name, (sk.id, ws.rank) )

            i += 1
        
    def connect_signals(self):
        self.bt_cancel.clicked.connect( self.close     )
        self.bt_ok    .clicked.connect( self.on_accept )

    def on_accept(self):

        # check if all selected
        done = check_all_done(self.cbs) and check_all_done_2(self.les)

        if not done:
            self.error_bar.setText('''<p style='color:#FF0000'>
                                      <b>
                                      You need to choose all the skills
                                      e/o emphases
                                      </b>
                                      </p>
                                      ''')
            self.error_bar.setVisible(True)
            return

        # check if all different
        all_different = check_all_different(self.cbs)

        if not all_different:
            self.error_bar.setText('''<p style='color:#FF0000'>
                                      <b>
                                      You can't select the same skill more than once
                                      </b>
                                      </p>
                                      ''')
            self.error_bar.setVisible(True)
            return

        # check if already got
        already_got = check_already_got([x.itemData(x.currentIndex())[0] for x in self.cbs], self.pc.get_skills())

        if already_got:
            self.error_bar.setText('''<p style='color:#FF0000'>
                                      <b>
                                      You already possess some of these skills
                                      </b>
                                      </p>
                                      ''')
            self.error_bar.setVisible(True)
            return

        self.error_bar.setVisible(False)

        for cb in self.cbs:
            idx = cb.currentIndex()
            uuid, rank = cb.itemData(idx)
            self.pc.add_school_skill(uuid, rank)

        for i in xrange(0, len(self.les)):
            emph = self.les[i].text()
            s_id = self.pc.get_pending_wc_emphs()[i]

            self.pc.add_school_skill(s_id, 0, emph)

        self.accept()
        
    def closeEvent(self, event):
        self.cleanup()
        

class SelWcSpells(QtGui.QDialog):
    def __init__(self, pc, store, parent = None):
        super(SelWcSpells, self).__init__(parent)
        self.pc  = pc
        self.dstore = store
        self.cbs_ring    = []
        self.cbs_mast    = []
        self.cbs_spell   = []
        self.error_bar = None
        self.build_ui()        
        self.connect_signals()
        self.load_data()        

    def build_ui(self):
        self.setWindowTitle(self.tr('Choose School Spells'))

        grid = QtGui.QGridLayout(self)
        grid.addWidget( QtGui.QLabel(self.tr("<i>Your school has granted you \
                                             the right to choose some spells.</i> \
                                             <br/><b>Choose with care.</b>"), self),
                                              0, 0, 1, 5)
        grid.setRowStretch(0,2)

        self.bt_ok     = QtGui.QPushButton(self.tr('Ok'    ), self)
        self.bt_cancel = QtGui.QPushButton(self.tr('Cancel'), self)

        row_ = 2
        col_ = 0
        max_row = row_
        max_col = col_

        for i in xrange(0, self.pc.get_how_many_spell_i_miss()):
            grp  = QtGui.QGroupBox(self.tr('Choose Spell'))
            fbox = QtGui.QFormLayout(grp)

            cb_ring  = QtGui.QComboBox(self)
            cb_mast  = QtGui.QComboBox(self)
            cb_spell = QtGui.QComboBox(self)

            fbox.addRow(self.tr('Ring'   ), cb_ring)
            fbox.addRow(self.tr('Mastery'), cb_mast)
            fbox.addRow(self.tr('Spell'  ), cb_spell)

            self.cbs_ring .append(cb_ring)
            self.cbs_mast .append(cb_mast)
            self.cbs_spell.append(cb_spell)

            if i and (i % 4) == 0:
                col_ += 1
                row_ = 2

            grid.addWidget(grp, row_, col_)

            row_ += 1
            max_row = max(row_, max_row)
            max_col = max(col_, max_col)

        self.error_bar = QtGui.QLabel(self)
        self.error_bar.setVisible(False)
        grid.addWidget(self.error_bar, max_row, 0, 1, max_col)

        buttonBox = QtGui.QDialogButtonBox(QtCore.Qt.Horizontal, self)
        buttonBox.addButton(self.bt_ok, QtGui.QDialogButtonBox.AcceptRole)
        buttonBox.addButton(self.bt_cancel, QtGui.QDialogButtonBox.RejectRole)

        grid.addWidget( buttonBox, max_row+1, max_col)
        #grid.addWidget( self.bt_cancel, max_row+1, max_col+1)

    def load_data(self):           
        for cb in self.cbs_ring:            
            cb.blockSignals(True)
            cb.addItem(self.tr('Earth'), 'earth')
            cb.addItem(self.tr('Air'  ), 'air')
            cb.addItem(self.tr('Water'), 'water')
            cb.addItem(self.tr('Fire' ), 'fire')
            cb.addItem(self.tr('Void' ), 'void')

        max_mastery = self.pc.get_insight_rank()
        
        idx = 0
        for wc in self.pc.get_pending_wc_spells():
            ring, qty = wc
            print('wildcard, ring: {0}, qty: {1}'.format(ring, qty))
            for i in xrange(idx, qty+idx):
                if 'maho' in ring:
                    print('set maho flag for index {0}'.format(i))
                    self.cbs_mast[i].setProperty('only_maho', True)
                    self.cbs_ring[i].setProperty('only_maho', True)
                elif models.chmodel.ring_from_name(ring) >= 0:
                    ring_n = models.chmodel.ring_from_name(ring)
                    self.cbs_ring[i].setCurrentIndex(ring_n)
                    self.cbs_ring[i].setEnabled(False)
                if 'nodefic' in ring:
                    print('set nodefic flag for index {0}'.format(i))
                    self.cbs_mast[i].setProperty('no_defic', True)
                    self.cbs_ring[i].setProperty('no_defic', True)
            idx += qty
        
        # HACK: might be needed for a good layout
        for cb in self.cbs_spell:
            cb.addItem('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        
        # resume signals
        for cb in self.cbs_ring:            
            self.do_ring_change(cb)
            cb.blockSignals(False)       

    def connect_signals(self):
        for cb in self.cbs_ring:
            cb.currentIndexChanged.connect( self.on_ring_change    )

        for cb in self.cbs_mast:
            cb.currentIndexChanged.connect( self.on_mastery_change )

        self.bt_cancel.clicked.connect( self.close     )
        self.bt_ok    .clicked.connect( self.on_accept )
        
    def cleanup(self):
        self.cbs_ring    = []
        self.cbs_mast    = []
        self.cbs_spell   = []
        self.error_bar = None
        
    def do_ring_change(self, cb_ring):        
        ring  = cb_ring.itemData( cb_ring.currentIndex() )
        which = self.cbs_ring.index( cb_ring )
        cb_mast = self.cbs_mast[which]
        cb_spell = self.cbs_spell[which]
        
        # SPECIAL FLAGS
        only_maho = cb_ring.property('only_maho') or False
        no_defic  = cb_ring.property('no_defic' ) or False       
        
        # UPDATE MASTERY COMBOBOX BASED ON AFFINITY/DEFICIENCY
        affin = self.pc.get_affinity  ()
        defic = self.pc.get_deficiency()
        
        print("affinity: {0}, deficiency: {1}, element: {2}".format(affin, defic, ring))
               
        cb_mast.blockSignals(True)
        cb_mast.clear()
        mod_ = 0
        if affin == ring or ring in affin:  mod_ = 1
        if defic == ring and not only_maho: mod_ = -1        
        
        for x in xrange(0,self.pc.get_insight_rank()+mod_):
            cb_mast.addItem(self.tr('Mastery Level {0}').format(x+1), x+1)   
        cb_mast.blockSignals(False)
        
        if cb_mast.currentIndex() < 0:
            cb_mast.setCurrentIndex(0)
            
        mastery = cb_mast.itemData( cb_mast.currentIndex() ) or 0            
        
        if defic == ring and no_defic:
            cb_spell.clear()
        else:
            self.do_update_spells(cb_spell, ring, mastery, only_maho)
            
    def on_ring_change(self, text = ''):
        self.do_ring_change(self.sender())

    def do_mastery_change(self, cb_mast):
        mastery  = cb_mast.itemData( cb_mast.currentIndex() ) or 0
        which = self.cbs_mast.index( cb_mast )
        cb_ring = self.cbs_ring[which]
        ring = cb_ring.itemData( cb_ring.currentIndex() )
        cb_spell = self.cbs_spell[which]       

        affin = self.pc.get_affinity  ()
        defic = self.pc.get_deficiency()
               
        only_maho = cb_mast.property('only_maho') or False
        no_defic  = cb_mast.property('no_defic' ) or False
                
        if defic == ring and no_defic:
            cb_spell.clear()
        else:
            self.do_update_spells(cb_spell, ring, mastery, only_maho)               
        
    def on_mastery_change(self, text = ''):
        self.do_mastery_change(self.sender())
        
    def do_update_spells(self, cb_spell, ring, mastery, only_maho):  
        print('update spells for ring {0}, mastery {1}, only_maho {2}'.format(ring, mastery, only_maho))        
        cb_spell.clear()        
        if mastery <= 0:
            return        
        avail_spells = []
        if only_maho:
            avail_spells = dal.query.get_maho_spells(self.dstore, ring, mastery)
        else:
            avail_spells = dal.query.get_spells(self.dstore, ring, mastery)                
        
        for spell in avail_spells:
            cb_spell.addItem(spell.name, spell.id)
        
    def on_accept(self):
        # check if all selected
        done = check_all_done(self.cbs_spell)

        if not done:
            self.error_bar.setText(self.tr(
            '''<p style='color:#FF0000'>
               <b>
               You need to choose all the spells
               </b>
               </p>
            '''))
            
            self.error_bar.setVisible(True)
            return
        
        # check if all different
        all_different = check_all_different(self.cbs_spell)

        if not all_different:
            self.error_bar.setText(self.tr(
            '''<p style='color:#FF0000'>
               <b>
               You can't select the same spell more than once
               </b>
               </p>
            '''))
            self.error_bar.setVisible(True)
            return

        # check if already got
        already_got = check_already_got([x.itemData(x.currentIndex()) for x in self.cbs_spell], self.pc.get_skills())

        if already_got:
            self.error_bar.setText(self.tr(
            '''<p style='color:#FF0000'>
               <b>
               You already possess some of these spells
               </b>
               </p>
            '''))
            
            self.error_bar.setVisible(True)
            return

        self.error_bar.setVisible(False)

        for cb in self.cbs_spell:
            idx = cb.currentIndex()
            uuid = cb.itemData(idx)
            self.pc.add_spell(uuid)

        self.accept()

    def closeEvent(self, event):
        self.cleanup()
