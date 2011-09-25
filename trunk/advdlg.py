#!/usr/bin/python

import advances

from PySide import QtCore, QtGui
from chmodel import ATTRIBS, RINGS

class BuyAdvDialog(QtGui.QDialog):
    def __init__(self, pc, tag, parent = None):
        super(BuyAdvDialog, self).__init__(parent)
        self.tag = tag
        self.adv = None
        self.pc  = pc
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

        labels = dict(attrib=('Choose Attribute', None),
                      skill= ('Choose Skill', None),
                      emph=  ('Choose Skill', 'Choose Emphasys'),
                      kata=  ('Choose Kata', None),
                      kiho=  ('Choose Kiho', None),
                      spell= ('Choose Spell', None))

        self.setWindowTitle( titles[self.tag] )

        lb1 = None
        lb2 = None

        self.cb1 = None
        self.cb2 = None

        if self.tag in labels:
            if labels[self.tag][0] is not None:
                lb1 = QtGui.QLabel(labels[self.tag][0], self)
                self.cb1 = QtGui.QComboBox(self)
                grid.addWidget(lb1, 0, 0)
                grid.addWidget(self.cb1, 0, 1, 1, 3, QtCore.Qt.AlignHCenter)
            if labels[self.tag][1] is not None:
                lb2 = QtGui.QLabel(labels[self.tag][1], self)
                self.cb2 = QtGui.QComboBox(self)
                grid.addWidget(lb2, 1, 0)
                grid.addWidget(self.cb2, 1, 1, 1, 3, QtCore.Qt.AlignHCenter)

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


    def connect_signals(self):
        if self.tag == 'attrib':
            self.cb1.currentIndexChanged.connect( self.on_attrib_select )

        self.bt_buy.clicked.connect  ( self.buy_advancement )
        self.bt_close.clicked.connect( self.close           )

    def on_void_select(self):
        cur_value = self.pc.get_ring_rank( RINGS.VOID )
        new_value = cur_value + 1

        cost = self.pc.void_cost * new_value

        self.lb_from.setText('From %d to %d' % (cur_value, new_value))
        self.lb_cost.setText('Cost: %d exp' % cost)

        self.adv = advances.VoidAdv(cost)

    def on_attrib_select(self, text = ''):
        idx = self.cb1.currentIndex()
        attrib = self.cb1.itemData(idx)
        cur_value = self.pc.get_attrib_rank( attrib )
        new_value = cur_value + 1

        cost = self.pc.get_attrib_cost( attrib ) * new_value

        self.lb_from.setText('From %d to %d' % (cur_value, new_value))
        self.lb_cost.setText('Cost: %d exp' % cost)

        self.adv = advances.AttribAdv(attrib, cost)

    def buy_advancement(self):
        self.pc.add_advancement( self.adv )
        if self.tag == 'attrib':
            self.on_attrib_select()
        elif self.tag == 'void':
            self.on_void_select()

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
