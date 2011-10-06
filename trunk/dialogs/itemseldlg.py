#!/usr/bin/python

from PySide import QtCore, QtGui
import rules

class ChooseItemDialog(QtGui.QDialog):
    def __init__(self, pc, tag, conn, parent = None):
        super(ChooseItemDialog, self).__init__(parent)
        self.tag = tag
        self.adv = None
        self.pc  = pc
        self.dbconn = conn
        self.build_ui()
        self.load_data()

    def build_ui(self):    
        # depending on the tag ( armor or weapon )
        # we build a different interface
        
        self.bt_accept = QtGui.QPushButton('Ok'    , self)
        self.bt_cancel = QtGui.QPushButton('Cancel', self)
        
        grid = QtGui.QGridLayout(self)
        grid.setColumnStretch(0, 2)
        
        if self.tag == 'armor':
            self.setWindowTitle("Wear Armor")
            grp     = QtGui.QGroupBox("Select Armor", self)
            vbox    = QtGui.QVBoxLayout(grp)
            self.cb = QtGui.QComboBox(self)
            self.cb.currentIndexChanged.connect( self.on_armor_select )
            vbox.addWidget(self.cb)           
            grid.addWidget(grp, 0, 0)
            
            grp     = QtGui.QGroupBox("Stats", self)
            vbox    = QtGui.QVBoxLayout(grp)
            #self.stats = []
            #for i in xrange(0, 4):
            #    self.stats.append( QtGui.QLabel(self) )               
            self.stats = QtGui.QLabel(self)
            self.stats.setWordWrap(True)
            vbox.addWidget(self.stats)
                                
            grid.setRowStretch(1, 2)    
            grid.addWidget(grp, 1, 0, 1, 4)
            grid.addWidget(self.bt_accept, 2, 2)
            grid.addWidget(self.bt_cancel, 2, 3)
        elif self.tag == 'weapon':
            self.setWindowTitle("Add Weapon")
            grp     = QtGui.QGroupBox("Weapon Skill", self)
            vbox    = QtGui.QVBoxLayout(grp)
            self.cb1 = QtGui.QComboBox(self)
            self.cb1.currentIndexChanged.connect( self.on_weap_skill_select )
            vbox.addWidget(self.cb1)           
            grid.addWidget(grp, 0, 0)

            grp     = QtGui.QGroupBox("Weapon", self)
            vbox    = QtGui.QVBoxLayout(grp)
            self.cb2 = QtGui.QComboBox(self)
            self.cb2.currentIndexChanged.connect( self.on_weap_select )
            vbox.addWidget(self.cb2)           
            grid.addWidget(grp, 1, 0)
            
            grp     = QtGui.QGroupBox("Stats", self)
            vbox    = QtGui.QVBoxLayout(grp)
            self.stats = []
            for i in xrange(0, 7):
                self.stats.append( QtGui.QLabel(self) )
            
            for s in self.stats:
                s.setWordWrap(True)
                vbox.addWidget(s)
            
            grid.setRowStretch(2, 2)
            grid.addWidget(grp, 2, 0, 1, 4)
            grid.addWidget(self.bt_accept, 3, 2)
            grid.addWidget(self.bt_cancel, 3, 3)
            
        self.grid = grid
        
    def load_data(self):
        c = self.dbconn.cursor()
        if self.tag == 'armor':
            c.execute('''select uuid, name from armors''')
            for uuid, name in c.fetchall():
                self.cb.addItem(name, uuid)
        elif self.tag == 'weapon':
            c.execute('''select skills.uuid, name, tag from skills
                         inner join tags on tags.uuid=skills.uuid
                         where tag="weapon"''')
            for uuid, name, tag in c.fetchall():
                self.cb1.addItem(name, uuid)
                
    def on_armor_select(self, text = ''):
        # list stats
        selected = self.cb.currentIndex()
        if selected < 0:
            return
        armor_uuid = self.cb.itemData(selected)
        
        c = self.dbconn.cursor()
        c.execute('''select tn, rd, special, cost from armors
                     where uuid=?''', [armor_uuid])
        
        for tn, rd, special, cost in c.fetchall():
            c.execute('''select desc from effects
                         where tag=?''', [special])
            rule_text = ''
            for desc in c.fetchall():
                rule_text = str(desc)
                break
                
            stats_text = '''<p><pre>%-20s %s</pre></p>
                            <p><pre>%-20s %s</pre></p>
                            <p><pre>%-20s %s</pre></p>
                            <p><i>%s</i></p>''' % \
                            ( 'Armor TN ',tn,
                              'Reduction',rd,
                              'Cost     ',cost,
                              rule_text )
            self.stats.setText(stats_text)            
            break
        
        #self.stats[3].setIndent(10)
        self.stats.setSizePolicy( QtGui.QSizePolicy.Minimum,            
                                  QtGui.QSizePolicy.Minimum )
    
    def on_weap_skill_select(self, text = ''):
        self.cb2.clear()
        selected = self.cb1.currentIndex()
        if selected < 0:
            return
        sk_uuid = self.cb1.itemData(selected)
        
        c = self.dbconn.cursor()
        c.execute('''select uuid, name from weapons
                     where skill_uuid=?''', [sk_uuid])
                     
        for uuid, name in c.fetchall():
            self.cb2.addItem(name, uuid)
        
    def on_weap_select(self, text = ''):
        # list stats
        selected = self.cb2.currentIndex()
        if selected < 0:
            return
        weap_uuid = self.cb2.itemData(selected)
        
        for s in self.stats:
            s.setText('')
            s.setSizePolicy( QtGui.QSizePolicy.Preferred, 
                             QtGui.QSizePolicy.Ignored )
                    
        c = self.dbconn.cursor()
        c.execute('''select dr, dr_alt, range, strength,
                     min_strength, effect_id, cost
                     from weapons
                     where uuid=?''', [weap_uuid])
        
        for dr, dr_alt, rng, str_, mstr_, eff, cost in c.fetchall():
            c.execute('''select desc from effects
                         where uuid=?''', [eff])
            rule_text = ''
            for desc in c.fetchall():
                rule_text = desc
                break
            r = 0            
            if dr is not None:
                self.stats[r].setText( '<pre>%-24s %s</pre>' % ('Primary DR  ',dr) )                
                r += 1
            if dr_alt is not None:
                self.stats[r].setText( '<pre>%-24s %s</pre>' % ('Secondary DR',dr_alt) )
                r += 1
            if rng is not None:               
               self.stats[r].setText( '<pre>%-24s %s</pre>' % ('Range        ',rng) )
               r += 1
            if str_ is not None:
               self.stats[r].setText( '<pre>%-24s %s</pre>' % ('Strength     ',str_) )
               r += 1
            if mstr_ is not None:
               self.stats[r].setText( '<pre>%-24s %s</pre>' % ('Min. Strength',mstr_) )
               r += 1
            if cost is not None:
               self.stats[r].setText( '<pre>%-24s %s</pre>' % ('Cost         ',cost) )
               r += 1
            if eff is not None:
               self.stats[r].setText( '<i>%s</i>' % rule_text )
               self.stats[r].setIndent(10)
               self.stats[r].setSizePolicy( QtGui.QSizePolicy.Minimum,            
                                            QtGui.QSizePolicy.Minimum )                       
               r += 1

            break
      
        #for i in xrange(0,r):
        #    self.stats[i].setVisible(True)
        self.grid.update()        

