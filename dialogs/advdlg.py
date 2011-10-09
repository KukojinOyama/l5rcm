#!/usr/bin/python

import models.advances as advances

from models.chmodel import ATTRIBS, RINGS
from PySide import QtCore, QtGui


class BuyAdvDialog(QtGui.QDialog):
    def __init__(self, pc, tag, conn, parent = None):
        super(BuyAdvDialog, self).__init__(parent)
        self.tag = tag
        self.adv = None
        self.pc  = pc
        self.dbconn = conn
        self.build_ui()
        self.connect_signals()
        self.load_data()

    def build_ui(self):
        grid = QtGui.QGridLayout(self)

        titles = dict(attrib='Buy Attribute rank',
                      skill= 'Buy Skill rank',
                      void=  'Buy Void rank',
                      emph=  'Buy Skill emphasys',
                      merit= 'Buy Advantages',
                      flaw=  'Buy Disadvantages',
                      kata=  'Buy Kata',
                      kiho=  'Buy Kiho',
                      spell= 'Buy Spell')

        labels = dict(attrib=('Choose Attribute'   ,  None),
                      skill= ('Choose Skill Type'  , 'Choose Skill'),
                      emph=  ('Choose Skill'       , 'Choose Emphasis'),
                      merit= ('Choose Advantage'   , None),
                      flaw=  ('Choose Disadvantage', None),
                      kata=  ('Choose Kata'        , None),
                      kiho=  ('Choose Kiho'        , None),
                      spell= ('Choose Spell'       , None))

        self.setWindowTitle( titles[self.tag] )

        self.widgets = dict(attrib=(QtGui.QComboBox(self), None),
                            skill =(QtGui.QComboBox(self), QtGui.QComboBox(self)),
                            emph  =(QtGui.QComboBox(self), QtGui.QLineEdit(self)),
                            merit =(QtGui.QComboBox(self), None),
                            flaw  =(QtGui.QComboBox(self), None),
                            kata  =(None, None),
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

        self.lb_from = QtGui.QLabel('Make your choice', self)
        self.lb_cost = QtGui.QLabel('Cost: 0', self)

        self.bt_buy   = QtGui.QPushButton('Buy', self)
        self.bt_close = QtGui.QPushButton('Close', self)

        grid.addWidget(self.lb_from, 3, 0, 1, 3)
        grid.addWidget(self.lb_cost, 4, 0, 1, 3)
        grid.addWidget(self.bt_buy,  5, 2, 1, 1)
        grid.addWidget(self.bt_close,  5, 3, 1, 1)

    def load_data(self):
        if self.tag == 'attrib':
            cb = self.widgets[self.tag][0]
            cb.addItem('Stamina',      ATTRIBS.STAMINA     )
            cb.addItem('Willpower',    ATTRIBS.WILLPOWER   )
            cb.addItem('Reflexes',     ATTRIBS.REFLEXES    )
            cb.addItem('Awareness',    ATTRIBS.AWARENESS   )
            cb.addItem('Strength',     ATTRIBS.STRENGTH    )
            cb.addItem('Perception',   ATTRIBS.PERCEPTION  )
            cb.addItem('Agility',      ATTRIBS.AGILITY     )
            cb.addItem('Intelligence', ATTRIBS.INTELLIGENCE)
        elif self.tag == 'void':
            self.on_void_select()
        elif self.tag == 'skill':
            cb = self.widgets[self.tag][0]
            c = self.dbconn.cursor()
            c.execute('''select distinct type from skills order by type''')
            for t in c.fetchall():
                cb.addItem( t[0].capitalize(), t[0] )
            c.close()
        elif self.tag == 'emph':
            cb = self.widgets[self.tag][0]
            c = self.dbconn.cursor()
            for id in self.pc.get_skills():
                c.execute('''select uuid, name from skills
                             where uuid=? order by name''', [id])
                for u, s in c.fetchall():
                    cb.addItem(s, u)
            self.lb_cost.setText('Cost: 2 exp')
            self.lb_from.setVisible(False)
            c.close()
        elif self.tag == 'merit':
            cb = self.widgets[self.tag][0]
            c = self.dbconn.cursor()
            c.execute('''select uuid, name from perks order by name''')
            for uuid, name in c.fetchall():
                cb.addItem( name, uuid )
            c.close()            

    def connect_signals(self):
        if self.tag == 'attrib':
            cb = self.widgets[self.tag][0]
            cb.currentIndexChanged.connect( self.on_attrib_select )
        elif self.tag == 'skill':
            cb1 = self.widgets[self.tag][0]
            cb2 = self.widgets[self.tag][1]
            cb1.currentIndexChanged.connect( self.on_skill_type_select )
            cb2.currentIndexChanged.connect( self.on_skill_select )
        elif self.tag == 'merit':
            cb = self.widgets[self.tag][0]
            cb.currentIndexChanged.connect( self.on_merit_select )

        self.bt_buy.clicked.connect  ( self.buy_advancement )
        self.bt_close.clicked.connect( self.close           )

    def on_void_select(self):
        cur_value = self.pc.get_ring_rank( RINGS.VOID )
        new_value = cur_value + 1

        cost = self.pc.void_cost * new_value

        self.lb_from.setText('From %d to %d' % (cur_value, new_value))
        self.lb_cost.setText('Cost: %d exp' % cost)

        self.adv = advances.VoidAdv(cost)
        self.adv.desc = 'Void Ring, Rank %d to %d. Cost: %d xp' % ( cur_value, new_value, cost )

    def on_attrib_select(self, text = ''):
        cb = self.widgets['attrib'][0]
        idx = cb.currentIndex()
        attrib = cb.itemData(idx)
        text   = cb.itemText(idx)
        cur_value = self.pc.get_attrib_rank( attrib )
        new_value = cur_value + 1

        cost = self.pc.get_attrib_cost( attrib ) * new_value

        self.lb_from.setText('From %d to %d' % (cur_value, new_value))
        self.lb_cost.setText('Cost: %d exp' % cost)

        self.adv = advances.AttribAdv(attrib, cost)
        self.adv.desc = '%s, Rank %d to %d. Cost: %d xp' % ( text, cur_value, new_value, cost )

    def on_skill_type_select(self, text = ''):
        cb1   = self.widgets['skill'][0]
        cb2   = self.widgets['skill'][1]
        idx   = cb1.currentIndex()
        type_ = cb1.itemData(idx)
        c     = self.dbconn.cursor()
        c.execute('''select uuid, name from skills
                     where type=? order by name''', [type_])
        cb2.clear()
        for u, s in c.fetchall():
            cb2.addItem( s, u )
        c.close()

    def on_skill_select(self, text = ''):
        cb1  = self.widgets['skill'][0]
        cb2  = self.widgets['skill'][1]
        idx  = cb2.currentIndex()
        uuid = cb2.itemData(idx)
        text = cb2.itemText(idx)

        cur_value = self.pc.get_skill_rank( uuid )
        new_value = cur_value + 1

        cost = new_value

        self.lb_from.setText('From %d to %d' % (cur_value, new_value))
        self.lb_cost.setText('Cost: %d exp' % cost)

        self.adv = advances.SkillAdv(uuid, cost)
        self.adv.desc = '%s, Rank %d to %d. Cost: %d xp' % ( text, cur_value, new_value, cost )
        
    def on_merit_select(self, text = ''):
        cb   = self.widgets['merit'][0]
        idx  = cb.currentIndex()
        perk = cb.itemData(idx)
        text = cb.itemText(idx)

        c     = self.dbconn.cursor()
        c.execute('''select uuid, cost from perks
                     where uuid=? order by name''', [perk])
        cost = 0
        tag  = None
        for u, c_ in c.fetchall():
            cost = c_
            break

        c.execute('''select tag, cost from perk_except
                     where perk_uuid=? order by cost asc''', [perk])
                     
        for t, c_ in c.fetchall():
            if self.pc.has_tag(t):
                cost = c_
                tag  = t
                break
                
        c.close()

        if tag is None:
            self.lb_cost.setText('Cost: %d exp' % cost)
        else:
            self.lb_cost.setText('Cost: %d exp (%s)' % (cost, tag))

        self.adv = advances.MeritAdv(perk, cost, tag)
        if tag is None:
            self.adv.desc = '%s, Cost: %d xp' % ( text, cost )
        else:
            self.adv.desc = '%s, Cost: %d xp (%s)' % ( text, cost, tag )
        
    def buy_advancement(self):
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
            self.adv.desc = '%s, Skill %s. Cost: 2 xp' % ( tx.text(), sk_name )
            self.pc.add_advancement( self.adv )
            tx.setText('')
        elif self.tag == 'merit':
            self.pc.add_advancement( self.adv )
            self.accept()

class SelWcSkills(QtGui.QDialog):
    def __init__(self, pc, conn, parent = None):
        super(SelWcSkills, self).__init__(parent)
        self.pc  = pc
        self.dbconn = conn
        self.cbs    = []
        self.error_bar = None
        self.build_ui()
        self.connect_signals()
        self.load_data()

    def build_ui(self):
        self.setWindowTitle('Choose School Skills')

        grid = QtGui.QGridLayout(self)
        grid.addWidget( QtGui.QLabel('<i>Your school has granted you ' +
                                     'the right to choose some skills.</i> ' +
                                     '<br/><b>Choose with care.</b>', self),
                                      0, 0, 1, 3)
        grid.setRowStretch(0,2)

        self.bt_ok     = QtGui.QPushButton('Ok', self)
        self.bt_cancel = QtGui.QPushButton('Cancel', self)

        row_ = 2
        for w, r in self.pc.get_pending_wc_skills():
            lb = ''
            if w == 'any':
                lb = 'Any one skill (rank %d):' % r
            else:
                wildcards = w.split(';')
                w = ' or '.join(wildcards)
                lb = 'Any %s skill (rank %d):' % (w, r)

            grid.addWidget( QtGui.QLabel(lb, self), row_, 0 )

            cb = QtGui.QComboBox(self)
            self.cbs.append(cb)
            grid.addWidget( cb, row_, 1, 1, 2)

            row_ += 1

        self.error_bar = QtGui.QLabel(self)
        self.error_bar.setVisible(False)
        grid.addWidget(self.error_bar, row_, 0, 1, 3)

        grid.addWidget( self.bt_ok,     row_+1, 1)
        grid.addWidget( self.bt_cancel, row_+1, 2)

    def load_data(self):
        c = self.dbconn.cursor()

        c.execute('''DROP TABLE IF EXISTS tmp_sc_sk_skills''')
        c.execute('''CREATE TEMP TABLE tmp_sc_sk_skills
           AS SELECT skills.uuid,
           skills.name, skills.type, tags.tag FROM skills inner join tags
           ON skills.uuid=tags.uuid
           UNION SELECT uuid, name, type, type FROM skills''')
        i = 0
        for w, r in self.pc.get_pending_wc_skills():

            if w == 'any':
                c.execute('''SELECT uuid, name FROM skills order by type, name''')
                for uuid, name in c.fetchall():
                    self.cbs[i].addItem( name, (uuid, r) )
            else:
                wildcards = w.split(';')
                for w_ in wildcards:
                    c.execute('''SELECT uuid, name FROM tmp_sc_sk_skills
                                 WHERE tag=? group by uuid order by name''', [w_])

                    for uuid, name in c.fetchall():
                        self.cbs[i].addItem( name, (uuid, r) )
            i += 1
        c.close()


    def connect_signals(self):
        self.bt_cancel.clicked.connect( self.close     )
        self.bt_ok    .clicked.connect( self.on_accept )

    def on_accept(self):
        done = True

        # check that all the choice have been made
        for cb in self.cbs:
            if cb.currentIndex() < 0:
                done = False;
                break

        if not done:
            self.error_bar.setText('''<span color:#FF0000>
                                      <b>
                                      You need to choose all the skills
                                      </b>
                                      </span>
                                      ''')
            self.error_bar.setVisible(True)
            return
        self.error_bar.setVisible(False)

        for cb in self.cbs:
            idx = cb.currentIndex()
            uuid, rank = cb.itemData(idx)
            self.pc.add_school_skill(uuid, rank)
        self.accept()

