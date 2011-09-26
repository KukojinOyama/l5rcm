#!/usr/bin/python

import sys, sqlite3, os
import rules
from PySide import QtGui, QtCore
from cknumwidget import CkNumWidget
from chmodel import AdvancedPcModel, ATTRIBS, RINGS
from advdlg import BuyAdvDialog, SelWcSkills

APP_NAME = 'l5rcm'
APP_DESC = 'Legend of the Five Rings: Character Manager'
APP_VERSION = '1.0'
APP_ORG = 'openningia'

def new_small_le(parent = None, ro = True):
    le = QtGui.QLineEdit(parent)
    le.setSizePolicy( QtGui.QSizePolicy.Maximum,
                      QtGui.QSizePolicy.Maximum )
    le.setMaximumSize( QtCore.QSize(32, 24) )
    le.setReadOnly(ro)
    return le

def new_horiz_line(parent = None):
    line = QtGui.QFrame(parent);
    line.setObjectName("line");
    line.setGeometry(QtCore.QRect(320, 150, 118, 3))
    line.setFrameShape(QtGui.QFrame.Shape.HLine)
    line.setFrameShadow(QtGui.QFrame.Sunken)
    return line

def split_decimal(value):
    d = int(value)
    return (d, value-d)

class L5RMain(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super(L5RMain, self).__init__(parent)

        self.save_path = ''
        
        # Build interface and menus
        self.build_ui()
        self.build_menu()
        
        # Build page 1
        self.build_ui_page_1()
        
        self.connect_signals()

        # Connect to database
        self.db_conn = sqlite3.connect('l5rdb.sqlite')
    
    def build_ui(self):
        # Main interface widgets
        self.widgets = QtGui.QWidget(self)
        self.tabs = QtGui.QTabWidget(self)
        self.tabs.setTabPosition( QtGui.QTabWidget.TabPosition.West )
        self.setCentralWidget(self.widgets)
        
        self.nicebar = QtGui.QFrame(self)
        self.nicebar.setStyleSheet('''
        QWidget { background: beige;}
        QPushButton {
            color: #333;
            border: 2px solid rgb(200,200,200);
            border-radius: 7px;
            padding: 5px;
            background: qradialgradient(cx: 0.3, cy: -0.4,
            fx: 0.3, fy: -0.4, radius: 1.35, stop: 0 #fff,
            stop: 1 rgb(255,170,0));
            min-width: 80px;
            }
            
        QPushButton:hover {
            background: qradialgradient(cx: 0.3, cy: -0.4,
            fx: 0.3, fy: -0.4, radius: 1.35, stop: 0 #fff,
            stop: 1 rgb(255,100,30));            
        }
        
        QPushButton:pressed {
            background: qradialgradient(cx: 0.4, cy: -0.1,
            fx: 0.4, fy: -0.1, radius: 1.35, stop: 0 #fff,
            stop: 1 rgb(255,200,50));            
        }        
        ''')
        self.nicebar.setMinimumSize(0, 32)
        self.nicebar.setVisible(False)
       
        mvbox = QtGui.QVBoxLayout(self.centralWidget())
        logo = QtGui.QLabel(self)
        logo.setScaledContents(True)
        logo.setPixmap( QtGui.QPixmap('banner_s.png') )
        mvbox.addWidget(logo)
        mvbox.addWidget(self.nicebar)
        mvbox.addWidget(self.tabs)
        
        
    def build_ui_page_1(self):

        mfr = QtGui.QFrame(self)
        self.tabs.addTab(mfr, u"First Page")

        mgrid = QtGui.QGridLayout(mfr)
        mgrid.setColumnStretch(0, 2)
        mgrid.setColumnStretch(1, 1)

        def add_pc_info(row, col):
            fr_pc_info   = QtGui.QFrame(self)
            fr_pc_info.setSizePolicy(QtGui.QSizePolicy.Preferred,
                                    QtGui.QSizePolicy.Maximum)

            grid = QtGui.QGridLayout(fr_pc_info)
            self.tx_pc_name   = QtGui.QLineEdit(self)
            self.tx_pc_rank   = QtGui.QLineEdit(self)
            self.cb_pc_clan   = QtGui.QComboBox(self)
            self.cb_pc_family = QtGui.QComboBox(self)
            self.cb_pc_school = QtGui.QComboBox(self)
            self.tx_pc_exp    = QtGui.QLineEdit(self)
            self.tx_pc_ins    = QtGui.QLineEdit(self)

            # 1st column
            grid.addWidget( QtGui.QLabel("Name", self), 0, 0   )
            grid.addWidget( QtGui.QLabel("Clan", self), 1, 0   )
            grid.addWidget( QtGui.QLabel("Family", self), 2, 0 )
            grid.addWidget( QtGui.QLabel("School", self), 3, 0 )
            
            # 3rd column
            grid.addWidget( QtGui.QLabel("Rank", self), 0, 3        )
            grid.addWidget( QtGui.QLabel("Exp. Points", self), 1, 3 )
            grid.addWidget( QtGui.QLabel("Insight", self), 2, 3     )
                            
            # 2nd column
            grid.addWidget( self.tx_pc_name, 0, 1, 1, 2  )
            grid.addWidget( self.cb_pc_clan, 1, 1 , 1, 2 )
            grid.addWidget( self.cb_pc_family, 2, 1, 1, 2)
            grid.addWidget( self.cb_pc_school, 3, 1, 1, 2)
            
            # 4th column
            grid.addWidget( self.tx_pc_rank, 0, 4, 1, 2)
            grid.addWidget( self.tx_pc_exp, 1, 4, 1, 2 )
            grid.addWidget( self.tx_pc_ins, 2, 4, 1, 2 )

            #grid.setColumnStretch(0, 1)
            #grid.setColumnStretch(1, 2)
            #grid.setColumnStretch(2, 1)
            #grid.setColumnStretch(3, 2)
            #grid.setColumnStretch(4, 1)
            #grid.setColumnStretch(5, 1)

            self.tx_pc_rank.setReadOnly(True)
            self.tx_pc_exp.setReadOnly(True)
            self.tx_pc_ins.setReadOnly(True)

            fr_pc_info.setLayout(grid)
            mgrid.addWidget(fr_pc_info, row, col, 1, 3)

        def add_pc_attribs(row, col):
            fr = QtGui.QFrame(self)
            fr.setSizePolicy(QtGui.QSizePolicy.Preferred,
                            QtGui.QSizePolicy.Maximum)
            hbox = QtGui.QHBoxLayout(fr)
            #hbox.setContentsMargins(0,0,0,0)
            grp = QtGui.QGroupBox("Rings and Attributes", self)
            grid = QtGui.QGridLayout(grp)
            grid.setSpacing(1)

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
            attribs[0][1].setProperty('attrib_id', ATTRIBS.STAMINA)
            attribs[1][1].setProperty('attrib_id', ATTRIBS.WILLPOWER)
            # Air ring
            attribs.append( ("Reflexes", new_small_le(self)) )
            attribs.append( ("Awareness", new_small_le(self)) )
            attribs[2][1].setProperty('attrib_id', ATTRIBS.REFLEXES)
            attribs[3][1].setProperty('attrib_id', ATTRIBS.AWARENESS)
            # Water ring
            attribs.append( ("Strength", new_small_le(self)) )
            attribs.append( ("Perception", new_small_le(self)) )
            attribs[4][1].setProperty('attrib_id', ATTRIBS.STRENGTH)
            attribs[5][1].setProperty('attrib_id', ATTRIBS.PERCEPTION)
            # Fire ring
            attribs.append( ("Agility", new_small_le(self)) )
            attribs.append( ("Intelligence", new_small_le(self)) )
            attribs[6][1].setProperty('attrib_id', ATTRIBS.AGILITY)
            attribs[7][1].setProperty('attrib_id', ATTRIBS.INTELLIGENCE)

            self.attribs = attribs

            for i in xrange(0, 8, 2):
                grid.addWidget( QtGui.QLabel( attribs[i][0] ),
                                (i//2) , 2, 1, 1, QtCore.Qt.AlignLeft )
                grid.addWidget( attribs[i][1], (i//2), 3, 1, 1,
                                QtCore.Qt.AlignLeft )

                grid.addWidget( QtGui.QLabel( attribs[i+1][0] ),
                                (i//2), 4, 1, 1, QtCore.Qt.AlignLeft )
                grid.addWidget( attribs[i+1][1], (i//2), 5, 1, 1,
                                QtCore.Qt.AlignLeft )
            grid.addWidget( QtGui.QLabel("<b>Void Points</b>"), 4, 2, 1, 3,
                            QtCore.Qt.AlignHCenter )
            grid.addWidget( CkNumWidget(self), 5, 2, 1, 3,
                            QtCore.Qt.AlignHCenter)

            hbox.addWidget(grp)

            mgrid.addWidget(fr, row, col)

        def add_pc_flags(row, col):
            tx_flags = ["Honor", "Glory", "Status", "Shadowland Taint" ]
            ob_flags_p = []
            ob_flags_r = []
            fr = QtGui.QFrame(self)
            #fr.setFrameShape(QtGui.QFrame.StyledPanel)
            vbox = QtGui.QVBoxLayout(fr)
            vbox.setContentsMargins(0,0,0,0)
            vbox.setSpacing(0)
            row_ = 0
            for f in tx_flags:
                fr_ = QtGui.QFrame(self)
                lay = QtGui.QGridLayout(fr_)
                lay.setContentsMargins(0,0,0,0)
                lay.setSpacing(0)
                lay.addWidget(QtGui.QLabel('<b>%s</b>' %f), row, 0)
                l = new_small_le(self, False)
                lay.addWidget(l, row, 1)
                w = CkNumWidget(self)
                lay.addWidget(w, row+1, 0, 1, 2, QtCore.Qt.AlignHCenter)
                ob_flags_p.append(w)
                ob_flags_r.append(l)
                vbox.addWidget(fr_)
                row_ += 2
            self.pc_flags_points = ob_flags_p
            self.pc_flags_rank   = ob_flags_r
            mgrid.addWidget(fr, row, col)

        def add_pc_quantities(row, col):
            fr = QtGui.QFrame(self)
            fr.setSizePolicy(QtGui.QSizePolicy.Expanding,
                            QtGui.QSizePolicy.Preferred)
            hbox = QtGui.QHBoxLayout(fr)

            # initiative
            grp  = QtGui.QGroupBox('Initiative', self)
            grd  = QtGui.QFormLayout(grp)

            self.tx_base_init = QtGui.QLineEdit(self)
            self.tx_mod_init  = QtGui.QLineEdit(self)
            self.tx_cur_init  = QtGui.QLineEdit(self)

            grd.addRow( 'Base', self.tx_base_init)
            grd.addRow( 'Modifier', self.tx_mod_init)
            grd.addRow( 'Current', self.tx_cur_init)

            hbox.addWidget(grp, 1)

            # Armor TN
            grp = QtGui.QGroupBox('Armor TN', self)
            grd  = QtGui.QFormLayout(grp)

            self.tx_base_tn  = QtGui.QLineEdit(self)
            self.tx_armor_tn = QtGui.QLineEdit(self)
            self.tx_armor_rd = QtGui.QLineEdit(self)
            self.tx_cur_tn   = QtGui.QLineEdit(self)

            grd.addRow( 'Base', self.tx_base_tn)
            grd.addRow( 'Armor', self.tx_armor_tn)
            grd.addRow( 'Reduction', self.tx_armor_rd)
            grd.addRow( 'Current', self.tx_cur_tn)

            hbox.addWidget(grp, 1)

            # Wounds
            grp = QtGui.QGroupBox('Wounds', self)
            grd  = QtGui.QGridLayout(grp)

            wnd = []
            wnd.append( ("Healty",   new_small_le(self), new_small_le(self)) )
            wnd.append( ("Nicked",   new_small_le(self), new_small_le(self)) )
            wnd.append( ("Grazed",   new_small_le(self), new_small_le(self)) )
            wnd.append( ("Hurt",     new_small_le(self), new_small_le(self)) )
            wnd.append( ("Injured",  new_small_le(self), new_small_le(self)) )
            wnd.append( ("Grippled", new_small_le(self), new_small_le(self)) )
            wnd.append( ("Down",     new_small_le(self), new_small_le(self)) )
            wnd.append( ("Out",      new_small_le(self), new_small_le(self)) )

            self.wounds = wnd

            row_ = 0
            col_ = 0
            for i in xrange(0, len(wnd)):
                if i == 4:
                    col_ = 3
                    row_ = 0
                grd.addWidget( QtGui.QLabel(wnd[i][0], self), row_, col_ )
                grd.addWidget( wnd[i][1], row_, col_+1 )
                grd.addWidget( wnd[i][2], row_, col_+2 )
                row_ += 1

            hbox.addWidget(grp, 2)

            mgrid.addWidget(fr, row, col, 1, 2)

        add_pc_info(0, 0)
        mgrid.addWidget(new_horiz_line(self), 1, 0, 1, 3)
        add_pc_attribs(2, 0)
        add_pc_flags(2, 1)
        mgrid.addWidget(new_horiz_line(self), 3, 0, 1, 3)
        add_pc_quantities(4, 0)

    def build_menu(self):
        # File Menu
        m_file = self.menuBar().addMenu("&File");
        # actions: new, open, save
        new_act  = QtGui.QAction(u'&New PC', self)
        open_act = QtGui.QAction(u'&Open PC...', self)
        save_act = QtGui.QAction(u'&Save PC', self)
        exit_act = QtGui.QAction(u'E&xit', self)

        m_file.addAction(new_act)
        m_file.addAction(open_act)
        m_file.addAction(save_act)
        m_file.addSeparator()
        m_file.addAction(exit_act)

        # signals
        exit_act.triggered.connect( self.close )

        # Advancement menu
        m_adv = self.menuBar().addMenu("A&dvancement")
        # submenut
        m_buy_adv = m_adv.addMenu("&Buy")

        # actions buy advancement, view advancements
        viewadv_act  = QtGui.QAction(u'&View advancements...', self)
        resetadv_act = QtGui.QAction(u'&Reset advancements', self)
        buyattr_act  = QtGui.QAction(u'Attribute rank...', self)
        buyvoid_act  = QtGui.QAction(u'Void ring...', self)
        buyskill_act = QtGui.QAction(u'Skill rank...', self)
        buyemph_act  = QtGui.QAction(u'Skill emphasis...', self)
        buykata_act  = QtGui.QAction(u'Kata...', self)
        buykiho_act  = QtGui.QAction(u'Kiho...', self)
        buyspell_act = QtGui.QAction(u'Spell...', self)

        buyattr_act .setProperty('tag', 'attrib')
        buyvoid_act .setProperty('tag', 'void'  )
        buyskill_act.setProperty('tag', 'skill' )
        buyemph_act .setProperty('tag', 'emph'  )
        buykata_act .setProperty('tag', 'kata'  )
        buykiho_act .setProperty('tag', 'kiho'  )
        buyspell_act.setProperty('tag', 'spell' )

        m_adv.addAction(viewadv_act)
        m_buy_adv.addAction(buyattr_act)
        m_buy_adv.addAction(buyvoid_act)
        m_buy_adv.addAction(buyskill_act)
        m_buy_adv.addAction(buyemph_act)
        m_buy_adv.addAction(buykata_act)
        m_buy_adv.addAction(buyspell_act)
        m_adv.addSeparator()
        m_adv.addAction(resetadv_act)

        resetadv_act.triggered.connect( self.reset_adv           )
        buyattr_act .triggered.connect( self.act_buy_advancement )
        buyvoid_act .triggered.connect( self.act_buy_advancement )
        buyskill_act.triggered.connect( self.act_buy_advancement )
        buyemph_act .triggered.connect( self.act_buy_advancement )
        buykata_act .triggered.connect( self.act_buy_advancement )
        buykiho_act .triggered.connect( self.act_buy_advancement )
        buyspell_act.triggered.connect( self.act_buy_advancement )

    def connect_signals(self):
        # always notify change ( programmatically, user )
        self.cb_pc_clan  .currentIndexChanged.connect( self.on_clan_change   )
        self.cb_pc_family.currentIndexChanged.connect( self.on_family_change )
        self.cb_pc_school.currentIndexChanged.connect( self.on_school_change )
        
        # notify only user edit
        self.tx_mod_init.editingFinished.connect( self.update_from_model )
        
    def show_nicebar(self, widgets):        
        # nicebar layout
        hbox = QtGui.QHBoxLayout()
        hbox.setContentsMargins(9,1,9,1)        
       
        for w in widgets:
            hbox.addWidget(w)
        
        self.nicebar.setLayout(hbox)    
        self.nicebar.setVisible(True)
        
    def hide_nicebar(self):
        self.nicebar.setVisible(False)

    def reset_adv(self):
        self.pc.advans = []
        self.update_from_model()

    def on_clan_change(self, text):
        self.cb_pc_family.clear()
        index = self.cb_pc_clan.currentIndex()
        if index < 1:
            self.cb_pc_family.setCurrentIndex(-1)
        else:
            clan_id = self.cb_pc_clan.itemData(index)

            self.load_families(clan_id)
            self.load_schools(clan_id)
            self.cb_pc_family.setCurrentIndex(0)
            self.cb_pc_school.setCurrentIndex(0)

    def on_family_change(self, text):
        index = self.cb_pc_family.currentIndex()
        if index < 0:
            self.pc.set_family()
            self.update_from_model()
            return

        uuid  = self.cb_pc_family.itemData(index)
        if uuid == self.pc.family:
            return
        # should modify step_1 character
        # get family perk

        c = self.db_conn.cursor()
        c.execute('''select perk, perkval from families
                     where uuid=?''', [uuid])
        perk, perkval = c.fetchone()
        self.pc.set_family( uuid, perk, perkval )
        self.update_from_model()

    def on_school_change(self, text):
        index = self.cb_pc_school.currentIndex()
        if index <= 0:
            self.pc.set_school()
            self.update_from_model()
            return

        uuid  = self.cb_pc_school.itemData(index)
        if uuid == self.pc.school:
            return

        # should modify step_2 character
        # get school perk

        c = self.db_conn.cursor()
        c.execute('''select perk, perkval, honor from schools
                     where uuid=?''', [uuid])
        perk, perkval, honor = c.fetchone()
        self.pc.set_school( uuid, perk, perkval, honor )
        
        # TODO: disable advancments until pending skills
        c.execute('''select skill_uuid, skill_rank, wildcard
                     from school_skills
                     where school_uuid=?''', [uuid])
        for sk_uuid, sk_rank, wc in c.fetchall():
            if sk_uuid is not None:
                self.pc.add_school_skill(sk_uuid, sk_rank)
            else:
                self.pc.add_pending_wc_skill(wc, sk_rank)
        self.update_from_model()

    def act_buy_advancement(self):
        dlg = BuyAdvDialog(self.pc, self.sender().property('tag'), self.db_conn, self)
        dlg.exec_()
        self.update_from_model()
        
    def act_choose_skills(self):
        dlg = SelWcSkills(self.pc, self.db_conn, self)
        if dlg.exec_() == QtGui.QDialog.DialogCode.Accepted:
            self.pc.clear_pending_wc_skills()
            self.update_from_model()
        
    def new_character(self):
        self.pc = AdvancedPcModel()
        self.pc.load_default()
        self.load_clans()
        self.load_schools(0)
        self.update_from_model()

    def load_clans(self):
        c = self.db_conn.cursor()
        # clans
        self.cb_pc_clan.addItem( 'No Clan', 0 )
        c.execute('''select uuid, name from clans order by name asc''')
        for f in c.fetchall():
            self.cb_pc_clan.addItem( f[1], f[0] )

    def load_schools(self, clan_id):
        c = self.db_conn.cursor()
        self.cb_pc_school.clear()
        if clan_id <= 0:
            c.execute('''select uuid, name from schools
                         order by name asc''')
        else:
            c.execute('''select uuid, name from schools where clan_id=?
                         order by name asc''',
                         [clan_id])

        self.cb_pc_school.addItem( 'No School', 0 )
        for f in c.fetchall():
            self.cb_pc_school.addItem( f[1], f[0] )

    def load_families(self, clan_id):
        c = self.db_conn.cursor()
        self.cb_pc_family.clear()
        if clan_id <= 0:
            c.execute('''select uuid, name from families
                         order by name asc''')
        else:
            c.execute('''select uuid, name from families where clan_id=?
                         order by name asc''',
                         [clan_id])

        for f in c.fetchall():
            self.cb_pc_family.addItem( f[1], f[0] )

    def set_clan(self, clan_id):
        idx = self.cb_pc_clan.currentIndex()
        c_uuid = self.cb_pc_clan.itemData(idx)
        if c_uuid == clan_id:
            return
        for i in xrange(0, self.cb_pc_clan.count()):
            if self.cb_pc_clan.itemData(idx) == clan_id:
                self.cb_pc_clan.setCurrentIndex(i)
                return

    def set_school(self, school_id):
        idx = self.cb_pc_school.currentIndex()
        s_uuid = self.cb_pc_school.itemData(idx)
        if s_uuid == school_id:
            return
        for i in xrange(0, self.cb_pc_school.count()):
            if self.cb_pc_school.itemData(idx) == school_id:
                self.cb_pc_school.setCurrentIndex(i)
                return

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

        self.tx_pc_exp.setText( str( self.pc.get_px() ) )

        # rings
        for i in xrange(0, 5):
            self.rings[i][1].setText( str(self.pc.get_ring_rank(i)) )

        # attributes
        for i in xrange(0, 8):
            self.attribs[i][1].setText( str(self.pc.get_attrib_rank(i)) )

        # pc rank
        self.tx_pc_rank.setText( str(self.pc.get_insight_rank()) )
        self.tx_pc_ins .setText( str(self.pc.get_insight()) )

        # pc flags
        self.set_honor ( self.pc.get_honor()  )
        self.set_glory ( self.pc.get_glory()  )
        self.set_status( self.pc.get_status() )
        self.set_taint ( self.pc.get_taint()  )

        # armor tn
        self.tx_base_tn.setText ( str(self.pc.get_base_tn())  )
        self.tx_armor_tn.setText( str(self.pc.get_armor_tn()) )
        self.tx_armor_rd.setText( str(self.pc.get_armor_rd()) )
        self.tx_cur_tn.setText  ( str(self.pc.get_cur_tn())   )

        # health
        for i in xrange(0, 8):
            h = self.pc.get_health_rank(i)
            self.wounds[i][1].setText( str(h) )
            
        # initiative        
        # TODO: temporary implementation
        r, k = self.pc.get_base_initiative()
        self.tx_base_init.setText( rules.format_rtk(r, k) )
        rtk = self.tx_mod_init.text()
        r1, k1 = rules.parse_rtk(rtk)
        if r1 and k1:
            self.tx_cur_init.setText( rules.format_rtk(r+r1, k+k1) )
            self.pc.mod_init = (r1, k1)
        else:
            self.tx_cur_init.setText( self.tx_base_init.text() )
            
        # Show nicebar if pending wildcard skills
        wcs = self.pc.get_pending_wc_skills()
        if len(wcs) > 0:
            lb = QtGui.QLabel('Your school gives you the choice of certain skills', self)
            bt = QtGui.QPushButton('Choose Skills', self)
            bt.setSizePolicy( QtGui.QSizePolicy.Maximum,
                              QtGui.QSizePolicy.Preferred)
            bt.clicked.connect( self.act_choose_skills )                  
            self.show_nicebar([lb, bt])
        else:
            self.hide_nicebar()

    def ask_to_save(self):
         msgBox = QtGui.QMessageBox(self)
         msgBox.setText("The character has been modified.")
         msgBox.setInformativeText("Do you want to save your changes?")
         msgBox.addButton( QtGui.QMessageBox.Save )
         msgBox.addButton( QtGui.QMessageBox.Discard )
         msgBox.addButton( QtGui.QMessageBox.Cancel )
         msgBox.setDefaultButton(QtGui.QMessageBox.Save)
         return msgBox.exec_()

    def closeEvent(self, ev):
        if self.pc.is_dirty():
            resp = self.ask_to_save()
            if resp == QtGui.QMessageBox.Save:
                self.save_pc()
                pass
            elif resp == QtGui.QMessageBox.Cancel:
                ev.ignore()
            else:
                super(L5RMain, self).closeEvent(ev)
        else:
            super(L5RMain, self).closeEvent(ev)

    def select_save_path(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self, "Save Character",
                                QtCore.QDir.homePath(),
                                "Character files (*.pc)")
        if len(fileName) != 2:
            return ''
        if fileName[0].endswith('.pc'):
            return fileName[0]
        return fileName[0] + '.pc'

    def save_pc(self):
        if self.save_path == '' or not os.exists(self.save_path):
            self.save_path = self.select_save_path()

        if self.save_path is not None and len(self.save_path) > 0:
            self.pc.save_to(self.save_path)


### MAIN ###
def main():
    app = QtGui.QApplication(sys.argv)

    QtCore.QCoreApplication.setApplicationName(APP_NAME)
    QtCore.QCoreApplication.setApplicationVersion(APP_VERSION)
    QtCore.QCoreApplication.setOrganizationName(APP_ORG)

    l5rcm = L5RMain()
    l5rcm.setWindowTitle(APP_DESC + ' v' + APP_VERSION)
    l5rcm.show()
    l5rcm.new_character()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
