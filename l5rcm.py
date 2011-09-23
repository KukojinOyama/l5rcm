#!/usr/bin/python

import sys, sqlite3
from PySide import QtGui, QtCore
from cknumwidget import CkNumWidget
from chmodel import AdvancedPcModel

APP_NAME = 'l5rcm'
APP_VERSION = '1.0'
APP_ORG = 'openningia'

def new_small_le(parent = None):
    le = QtGui.QLineEdit(parent)
    le.setSizePolicy( QtGui.QSizePolicy.Maximum,
                      QtGui.QSizePolicy.Maximum )
    le.setMaximumSize( QtCore.QSize(32, 24) )
    return le

def split_decimal(value):
    d = int(value)
    return (d, value-d)

class L5RMain(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super(L5RMain, self).__init__(parent)
        self.widgets = QtGui.QWidget(self)
        self.setCentralWidget(self.widgets)
        self.build_ui()
        self.connect_signals()
        self.db_conn = sqlite3.connect('l5rdb.sqlite')

    def build_ui(self):
        mgrid = QtGui.QGridLayout()
        
        def add_pc_info():
            fr_pc_info   = QtGui.QFrame(self)
            fr_pc_info.setSizePolicy(QtGui.QSizePolicy.Preferred,
                                    QtGui.QSizePolicy.Maximum)
            grid = QtGui.QGridLayout(fr_pc_info)
            self.tx_pc_name   = QtGui.QLineEdit(self)
            self.tx_pc_rank   = QtGui.QLineEdit(self)
            self.cb_pc_clan   = QtGui.QComboBox(self)
            self.cb_pc_school = QtGui.QComboBox(self)
            self.tx_pc_exp    = QtGui.QLineEdit(self)
            self.tx_pc_ins    = QtGui.QLineEdit(self)
            grid.addWidget( QtGui.QLabel("Name", self), 0, 0 )
            grid.addWidget( QtGui.QLabel("Clan", self), 1, 0 )
            grid.addWidget( QtGui.QLabel("School", self), 2, 0 )
            grid.addWidget( QtGui.QLabel("Rank", self), 0, 2 )
            grid.addWidget( QtGui.QLabel("Experience Points", self), 1, 2 )
            grid.addWidget( QtGui.QLabel("Insight", self), 2, 2 )
            
            grid.addWidget( self.tx_pc_name, 0, 1 )
            grid.addWidget( self.cb_pc_clan, 1, 1 )
            grid.addWidget( self.cb_pc_school, 2, 1 )
            grid.addWidget( self.tx_pc_rank, 0, 3 )
            grid.addWidget( self.tx_pc_exp, 1, 3 )
            grid.addWidget( self.tx_pc_ins, 2, 3 )
            
            fr_pc_info.setLayout(grid)
            mgrid.addWidget(fr_pc_info, 0, 0, 1, 3)
            
        def add_pc_attribs():
            fr = QtGui.QFrame(self)
            fr.setSizePolicy(QtGui.QSizePolicy.Preferred,
                            QtGui.QSizePolicy.Maximum)
            hbox = QtGui.QHBoxLayout(fr)
            #hbox.setContentsMargins(0,0,0,0)
            grp = QtGui.QGroupBox("Rings and Attributes", self)
            grid = QtGui.QGridLayout(grp)
            # rings
            rings = []
            rings.append( ( "Earth", new_small_le(self) ) )
            rings.append( ( "Air", new_small_le(self) ) )
            rings.append( ( "Water", new_small_le(self) ) )
            rings.append( ( "Fire", new_small_le(self) ) )
            rings.append( ( "Void", new_small_le(self) ) )
            
            # keep reference to the rings
            self.rings= rings

            for i in xrange(0, 5):
                grid.addWidget( QtGui.QLabel( rings[i][0] ), i, 0 )
                grid.addWidget( rings[i][1], i, 1 )
            
            attribs = []
            # Earth ring
            attribs.append( ("Stamina", new_small_le(self)) )
            attribs.append( ("Willpower", new_small_le(self)) )
            # Air ring
            attribs.append( ("Reflexes", new_small_le(self)) )
            attribs.append( ("Awareness", new_small_le(self)) )
            # Water ring
            attribs.append( ("Strength", new_small_le(self)) )
            attribs.append( ("Perception", new_small_le(self)) )
            # Fire ring
            attribs.append( ("Agility", new_small_le(self)) )
            attribs.append( ("Intelligence", new_small_le(self)) )

            self.attribs = attribs
            
            for i in xrange(0, 8, 2):
                grid.addWidget( QtGui.QLabel( attribs[i][0] ),
                                (i//2) , 2, 1, 1, QtCore.Qt.AlignRight )
                grid.addWidget( attribs[i][1], (i//2), 3, 1, 1,
                                QtCore.Qt.AlignRight )
                
                grid.addWidget( QtGui.QLabel( attribs[i+1][0] ),
                                (i//2), 4, 1, 1, QtCore.Qt.AlignRight )
                grid.addWidget( attribs[i+1][1], (i//2), 5, 1, 1,
                                QtCore.Qt.AlignRight )
            grid.addWidget( QtGui.QLabel("Void Points"), 4, 2)
            grid.addWidget( CkNumWidget(self), 4, 3, 1, 3, 
                            QtCore.Qt.AlignHCenter)
            
            hbox.addWidget(grp)
            
            mgrid.addWidget(fr, 1, 0, 1, 1)
        
        def add_pc_flags():
            tx_flags = ["Honor", "Glory", "Status", "Shadowland Taint" ]
            ob_flags_p = []
            ob_flags_r = []
            fr = QtGui.QFrame(self)
            #fr.setFrameShape(QtGui.QFrame.StyledPanel)
            vbox = QtGui.QVBoxLayout(fr)
            #vbox.setContentsMargins(0,0,0,0)
            #vbox.setSpacing(0)
            row = 0            
            for f in tx_flags:
                fr_ = QtGui.QFrame(self)
                lay = QtGui.QGridLayout(fr_)
                lay.setContentsMargins(0,0,0,0)
                lay.setSpacing(0)
                lay.addWidget(QtGui.QLabel('<b>%s</b>' %f), row, 0)
                l= new_small_le(self)
                lay.addWidget(l, row, 1)
                w = CkNumWidget(self)
                lay.addWidget(w, row+1, 0, 1, 2, QtCore.Qt.AlignHCenter)
                ob_flags_p.append(w)
                ob_flags_r.append(l)
                vbox.addWidget(fr_)
                row += 2
            self.pc_flags_points = ob_flags_p
            self.pc_flags_rank   = ob_flags_r
            mgrid.addWidget(fr, 1, 2, 1, 1)

        add_pc_info()
        add_pc_attribs()
        add_pc_flags()
        self.centralWidget().setLayout(mgrid)
        
    def connect_signals(self):
        pass
        
    def new_character(self):
        self.pc = AdvancedPcModel()
        self.pc.load_default()
        self.load_data()
        self.update_from_model()

    def load_data(self):
        c = self.db_conn.cursor()        
        # clans
        self.cb_pc_clan.addItem( 'No Clan', 0 )
        c.execute('''select uuid, name from clans''')
        for f in c.fetchall():
            self.cb_pc_clan.addItem( f[1], f[0] )    
        

    def set_clan(self, clan_id):
        pass

    def set_school(self, school_id):
        pass

    def set_flag(self, flag, value):
        rank, points = split_decimal(value)
        # set rank
        self.pc_flags_rank[flag].setText( str(rank) )
        # set points
        self.pc_flags_points[flag].set_value(points*10)

    def set_honor (self, value): self.set_flag(0, value)
    def set_glory (self, value): self.set_flag(1, value)
    def set_status(self, value): self.set_flag(2, value)
    def set_taint (self, value): self.set_flag(3, value)
        
    def update_from_model(self):
        self.tx_pc_name   = self.pc.name
        self.set_clan     ( self.pc.clan   )
        self.set_school   ( self.pc.school )

        # rings
        for i in xrange(0, 5):
            self.rings[i][1].setText( str(self.pc.get_ring_rank(i)) )
        
        # attributes
        for i in xrange(0, 8):
            self.attribs[i][1].setText( str(self.pc.get_attrib_rank(i)) )

        # pc rank
        self.tx_pc_rank.setText( str(self.pc.rank) )
        self.tx_pc_ins .setText( str(self.pc.get_insight()) )

        # pc flags
        self.set_honor ( self.pc.honor  )
        self.set_glory ( self.pc.glory  )
        self.set_status( self.pc.status )
        self.set_taint ( self.pc.taint  )
        
            
### MAIN ###
def main():
    app = QtGui.QApplication(sys.argv)

    QtCore.QCoreApplication.setApplicationName(APP_NAME)
    QtCore.QCoreApplication.setApplicationVersion(APP_VERSION)
    QtCore.QCoreApplication.setOrganizationName(APP_ORG)

    l5rcm = L5RMain()   
    l5rcm.show()
    l5rcm.new_character()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()
