#!/usr/bin/python

import advances
from PySide import QtCore, QtGui
from chmodel import ATTRIBS, RINGS

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
                      kata=  'Buy Kata',
                      kiho=  'Buy Kiho',
                      spell= 'Buy Spell')

        labels = dict(attrib=('Choose Attribute', None, None),
                      skill= ('Choose Skill Type', 'Choose Skill', None),
                      emph=  ('Choose Skill Type', 'Choose Skill', 'Choose Emphasys'),
                      kata=  ('Choose Kata', None, None),
                      kiho=  ('Choose Kiho', None, None),
                      spell= ('Choose Spell', None, None))

        self.setWindowTitle( titles[self.tag] )

        lb1 = None
        lb2 = None
        lb3 = None

        self.cb1 = None
        self.cb2 = None
        self.cb3 = None

        if self.tag in labels:
            if labels[self.tag][0] is not None:
                lb1 = QtGui.QLabel(labels[self.tag][0], self)
                self.cb1 = QtGui.QComboBox(self)
                grid.addWidget(lb1, 0, 0)
                grid.addWidget(self.cb1, 0, 1, 1, 3)
            if labels[self.tag][1] is not None:
                lb2 = QtGui.QLabel(labels[self.tag][1], self)
                self.cb2 = QtGui.QComboBox(self)
                grid.addWidget(lb2, 1, 0)
                grid.addWidget(self.cb2, 1, 1, 1, 3)
            if labels[self.tag][2] is not None:
                lb3 = QtGui.QLabel(labels[self.tag][2], self)
                self.cb3 = QtGui.QComboBox(self)
                grid.addWidget(lb2, 2, 0)
                grid.addWidget(self.cb3, 2, 1, 1, 3)

        self.lb_from = QtGui.QLabel('Make your choice', self)
        self.lb_cost = QtGui.QLabel('Cost: 0', self)

        self.bt_buy   = QtGui.QPushButton('Buy', self)
        self.bt_close = QtGui.QPushButton('Close', self)

        grid.addWidget(self.lb_from, 2, 0, 1, 3)
        grid.addWidget(self.lb_cost, 3, 0, 1, 3)
        grid.addWidget(self.bt_buy,  4, 2, 1, 1)
        grid.addWidget(self.bt_close,  4, 3, 1, 1)

    def load_data(self):
        if self.tag == 'attrib':
            self.cb1.addItem('Stamina', ATTRIBS.STAMINA)
            self.cb1.addItem('Willpower', ATTRIBS.WILLPOWER)
            self.cb1.addItem('Reflexes', ATTRIBS.REFLEXES)
            self.cb1.addItem('Awareness', ATTRIBS.AWARENESS)
            self.cb1.addItem('Strength', ATTRIBS.STRENGTH)
            self.cb1.addItem('Perception', ATTRIBS.PERCEPTION)
            self.cb1.addItem('Agility', ATTRIBS.AGILITY)
            self.cb1.addItem('Intelligence', ATTRIBS.INTELLIGENCE)
        elif self.tag == 'void':
            self.on_void_select()
        elif self.tag == 'skill':
            c = self.dbconn.cursor()
            c.execute('''select distinct type from skills order by type''')
            for t in c.fetchall():
                self.cb1.addItem( t[0].capitalize(), t[0] )
            c.close()

    def connect_signals(self):
        if self.tag == 'attrib':
            self.cb1.currentIndexChanged.connect( self.on_attrib_select )
        if self.tag == 'skill':
            self.cb1.currentIndexChanged.connect( self.on_skill_type_select )
            self.cb2.currentIndexChanged.connect( self.on_skill_select )

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
        idx = self.cb1.currentIndex()
        attrib = self.cb1.itemData(idx)
        text   = self.cb1.itemText(idx)
        cur_value = self.pc.get_attrib_rank( attrib )
        new_value = cur_value + 1

        cost = self.pc.get_attrib_cost( attrib ) * new_value

        self.lb_from.setText('From %d to %d' % (cur_value, new_value))
        self.lb_cost.setText('Cost: %d exp' % cost)

        self.adv = advances.AttribAdv(attrib, cost)
        self.adv.desc = '%s, Rank %d to %d. Cost: %d xp' % ( text, cur_value, new_value, cost )

    def on_skill_type_select(self, text = ''):
        idx = self.cb1.currentIndex()
        type_ = self.cb1.itemData(idx)
        c = self.dbconn.cursor()
        c.execute('''select uuid, name from skills
                     where type=? order by name''', [type_])
        self.cb2.clear()
        for u, s in c.fetchall():
            self.cb2.addItem( s, u )
        c.close()

    def on_skill_select(self, text = ''):
        idx = self.cb2.currentIndex()
        uuid = self.cb2.itemData(idx)
        text   = self.cb2.itemText(idx)

        cur_value = self.pc.get_skill_rank( uuid )
        new_value = cur_value + 1

        cost = new_value

        self.lb_from.setText('From %d to %d' % (cur_value, new_value))
        self.lb_cost.setText('Cost: %d exp' % cost)

        self.adv = advances.SkillAdv(uuid, cost)
        self.adv.desc = '%s, Rank %d to %d. Cost: %d xp' % ( text, cur_value, new_value, cost )

    def buy_advancement(self):
        self.pc.add_advancement( self.adv )
        if self.tag == 'attrib':
            self.on_attrib_select()
        elif self.tag == 'void':
            self.on_void_select()
        elif self.tag == 'skill':
            self.on_skill_select()

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
                lb = 'Any %s skill (rank %d):' % (w.capitalize(), r)

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
            else:
                c.execute('''SELECT uuid, name FROM tmp_sc_sk_skills
                             WHERE tag=? group by uuid order by name''', [w])

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

### MAIN ###
import sys
from chmodel import AdvancedPcModel
def main():
    app = QtGui.QApplication(sys.argv)

    pc = AdvancedPcModel()
    dlg = BuyAdvDialog(pc, 'attrib')
    dlg.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
