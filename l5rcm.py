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

import sys, sqlite3, os
import rules
import models
import widgets
import dialogs
import autoupdate
import tempfile
import exporters

from PySide import QtGui, QtCore
from models.chmodel import ATTRIBS, RINGS

APP_NAME    = 'l5rcm'
APP_DESC    = 'Legend of the Five Rings: Character Manager'
APP_VERSION = '1.9'
DB_VERSION  = '1.9'
APP_ORG     = 'openningia'

PROJECT_PAGE_LINK = 'http://code.google.com/p/l5rcm/'
BUGTRAQ_LINK      = 'http://code.google.com/p/l5rcm/issues/list'
PROJECT_PAGE_NAME = 'Project Page'
AUTHOR_NAME       = 'Daniele Simonetti'
L5R_RPG_HOME_PAGE = 'http://www.l5r.com/rpg/'
ALDERAC_HOME_PAGE = 'http://www.alderac.com/'


MY_CWD        = os.getcwd()
if not os.path.exists( os.path.join( MY_CWD, 'share/l5rcm') ):
    MY_CWD = sys.path[0]
    if not os.path.exists( os.path.join( MY_CWD, 'share/l5rcm') ):
        MY_CWD = os.path.dirname(sys.path[0])

def get_app_file(rel_path):
    if os.name == 'nt':
        return os.path.join( MY_CWD, 'share/l5rcm', rel_path )
    else:
        sys_path = '/usr/share/l5rcm'
        if os.path.exists( sys_path ):
            return os.path.join( sys_path, rel_path )
        return os.path.join( MY_CWD, 'share/l5rcm', rel_path )

def get_app_icon_path(size = (48,48)):
    size_str = '%dx%d' % size
    if os.name == 'nt':
        return os.path.join( MY_CWD, 'share/icons/l5rcm/%s' % size_str, APP_NAME + '.png' )
    else:
        sys_path = '/usr/share/icons/l5rcm/%s' % size_str
        if os.path.exists( sys_path ):
            return os.path.join( sys_path, APP_NAME + '.png' )
        return os.path.join( MY_CWD, 'share/icons/l5rcm/%s' % size_str, APP_NAME + '.png' )

def get_icon_path(name, size = (48,48)):
    size_str = '%dx%d' % size
    if os.name == 'nt':
        return os.path.join( MY_CWD, 'share/icons/l5rcm/%s' % size_str, name + '.png' )
    else:
        sys_path = '/usr/share/icons/l5rcm/%s' % size_str
        if os.path.exists( sys_path ):
            return os.path.join( sys_path, name + '.png' )
        return os.path.join( MY_CWD, 'share/icons/l5rcm/%s' % size_str, name + '.png' )

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

def new_item_groupbox(name, widget):
    grp  = QtGui.QGroupBox(name, widget.parent())
    vbox = QtGui.QVBoxLayout(grp)
    vbox.addWidget(widget)
    return grp

def new_small_plus_bt(parent = None):
    bt = QtGui.QToolButton(parent)
    bt.setText('+')
    bt.setMaximumSize(16,16)
    bt.setMinimumSize(16,16)
    bt.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
    return bt

def split_decimal(value):
    import decimal
    decimal.getcontext().prec = 2
    d = decimal.Decimal(value)
    i = int(d)
    return (i, d-i)

def pause_signals(widgets):
    for w in widgets: w.blockSignals(True)

def resume_signals(widgets):
    for w in widgets: w.blockSignals(False)


class L5RMain(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super(L5RMain, self).__init__(parent)

        self.save_path = ''

        # Build interface and menus
        self.build_ui()
        self.build_menu()

        # Connect to database
        self.db_conn = None
        try:
            self.db_conn = sqlite3.connect( get_app_file('l5rdb.sqlite') )
        except Exception as e:
            sys.stderr.write('unable to open database file %s\n' % get_app_file('l5rdb.sqlite'))
            sys.stderr.write("Current working dir : %s\n" % os.getcwd())

        # Build page 1
        self.build_ui_page_1()
        self.build_ui_page_2()
        self.build_ui_page_3()
        self.build_ui_page_4()
        self.build_ui_page_5()
        self.build_ui_page_6()

        self.connect_signals()

    def build_ui(self):
        # Main interface widgets
        self.widgets = QtGui.QWidget(self)
        self.tabs = QtGui.QTabWidget(self)
        self.tabs.setTabPosition( QtGui.QTabWidget.TabPosition.West )
        self.setCentralWidget(self.widgets)

        self.nicebar           = None
        self.lock_advancements = True

        mvbox = QtGui.QVBoxLayout(self.centralWidget())
        logo = QtGui.QLabel(self)
        logo.setScaledContents(True)
        logo.setPixmap( QtGui.QPixmap( get_app_file('banner_s.png') ) )
        mvbox.addWidget(logo)
        mvbox.addWidget(self.tabs)

        self.mvbox = mvbox

        # LOAD SETTINGS
        settings = QtCore.QSettings()
        geo = settings.value('geometry')
        if geo is not None:
            self.restoreGeometry(geo)
        #else:
        #    self.setGeometry(QtCore.QRect(100,100,680,800))

    def build_ui_page_1(self):

        mfr = QtGui.QFrame(self)
        self.tabs.addTab(mfr, u"Character")

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

            for i in xrange(0, 4):
                grid.addWidget( QtGui.QLabel( rings[i][0] ), i, 0 )
                grid.addWidget( rings[i][1], i, 1 )

            # void ring with plus button
            void_fr   = QtGui.QFrame(self)
            void_hbox = QtGui.QHBoxLayout(void_fr)
            void_hbox.setContentsMargins(0,0,0,0)
            void_bt  = new_small_plus_bt(self)
            void_hbox.addWidget(rings[4][1])
            void_hbox.addWidget(void_bt)
            void_bt.clicked.connect(self.on_void_increase)
            grid.addWidget( QtGui.QLabel( rings[4][0] ), 4, 0 )
            grid.addWidget( void_fr, 4, 1 )

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

            # map increase trait signals
            self.trait_sig_mapper = QtCore.QSignalMapper(self)

            def _attrib_frame(i):
                fr   = QtGui.QFrame(self)
                hbox = QtGui.QHBoxLayout(fr)
                hbox.setContentsMargins(0,0,0,0)
                # small plus button
                tag = attribs[i][0].lower()
                bt  = new_small_plus_bt(self)
                hbox.addWidget( attribs[i][1])
                hbox.addWidget( bt )
                self.trait_sig_mapper.setMapping(bt, tag)
                bt.connect(QtCore.SIGNAL("clicked()"), self.trait_sig_mapper, QtCore.SLOT("map()"))
                return fr

            for i in xrange(0, 8, 2):
                grid.addWidget( QtGui.QLabel( attribs[i][0] ),
                                (i//2) , 2, 1, 1, QtCore.Qt.AlignLeft )
                grid.addWidget( _attrib_frame(i), (i//2), 3, 1, 1,
                                QtCore.Qt.AlignLeft )

                grid.addWidget( QtGui.QLabel( attribs[i+1][0] ),
                                (i//2), 4, 1, 1, QtCore.Qt.AlignLeft )
                grid.addWidget( _attrib_frame(i+1), (i//2), 5, 1, 1,
                                QtCore.Qt.AlignLeft )
            grid.addWidget( QtGui.QLabel("<b>Void Points</b>"), 4, 2, 1, 3,
                            QtCore.Qt.AlignHCenter )

            self.void_points = widgets.CkNumWidget(count=10, parent=self)
            grid.addWidget( self.void_points, 5, 2, 1, 3,
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
                w = widgets.CkNumWidget(count=9, parent=self)
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

            self.tx_base_init.setReadOnly(True)
            self.tx_cur_init .setReadOnly(True)

            grd.addRow( 'Base', self.tx_base_init)
            grd.addRow( 'Modifier', self.tx_mod_init)
            grd.addRow( 'Current', self.tx_cur_init)

            hbox.addWidget(grp, 1)

            # Armor TN
            grp = QtGui.QGroupBox('Armor TN', self)
            grd  = QtGui.QFormLayout(grp)

            self.tx_armor_nm = QtGui.QLineEdit(self)
            self.tx_base_tn  = QtGui.QLineEdit(self)
            self.tx_armor_tn = QtGui.QLineEdit(self)
            self.tx_armor_rd = QtGui.QLineEdit(self)
            self.tx_cur_tn   = QtGui.QLineEdit(self)

            self.tx_armor_nm.setReadOnly(True)
            self.tx_base_tn .setReadOnly(True)
            self.tx_armor_tn.setReadOnly(True)
            self.tx_armor_rd.setReadOnly(True)
            self.tx_cur_tn  .setReadOnly(True)

            grd.addRow( 'Name', self.tx_armor_nm)
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
            self.wnd_lb = grp

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

    def _build_generic_page(self, models_):
        mfr    = QtGui.QFrame(self)
        vbox   = QtGui.QVBoxLayout(mfr)
        views_ = []

        for k, t, m, d, tb in models_:
            grp    = QtGui.QGroupBox(k, self)
            hbox   = QtGui.QHBoxLayout(grp)
            view   = None
            if t == 'table':
                view  = QtGui.QTableView(self)
                view.setSortingEnabled(True)
                view.horizontalHeader().setResizeMode(QtGui.QHeaderView.Interactive);
                view.horizontalHeader().setStretchLastSection(True)
                view.horizontalHeader().setCascadingSectionResizes(True)
            elif t == 'list':
                view = QtGui.QListView(self)
            view.setModel(m)
            if d is not None:
                view.setItemDelegate(d)

            if tb is not None:
                hbox.addWidget(tb)
            hbox.addWidget(view)
            vbox.addWidget(grp)
            views_.append(view)
        return mfr, views_

    def build_ui_page_2(self):
        self.sk_view_model = models.SkillTableViewModel(self.db_conn, self)
        self.ma_view_model = models.MaViewModel        (self.db_conn, self)

        # enable sorting through a proxy model
        sk_sort_model = models.ColorFriendlySortProxyModel(self)
        sk_sort_model.setDynamicSortFilter(True)
        sk_sort_model.setSourceModel(self.sk_view_model)

        # skills vertical toolbar
        vtb = widgets.VerticalToolBar(self)
        vtb.addStretch()
        vtb.addButton(QtGui.QIcon(get_icon_path('add',(16,16))),
                      'Add skill rank', self.buy_skill_rank)
        vtb.addButton(QtGui.QIcon(get_icon_path('buy',(16,16))),
                      'Buy another skill', self.show_buy_skill_dlg)
        vtb.addStretch()

        models_ = [ ("Skills", 'table', sk_sort_model, None, vtb),
                    ("Mastery Abilities",  'list', self.ma_view_model,
                    models.MaItemDelegate(self), None) ]

        frame_, views_ = self._build_generic_page(models_)

        if len(views_) > 0:
            self.skill_table_view = views_[0]

        self.tabs.addTab(frame_, u"Skills")

    def build_ui_page_3(self):
        self.sp_view_model = models.SpellTableViewModel(self.db_conn, self)
        self.th_view_model = models.TechViewModel      (self.db_conn, self)

        # enable sorting through a proxy model
        sp_sort_model = models.ColorFriendlySortProxyModel(self)
        sp_sort_model.setDynamicSortFilter(True)
        sp_sort_model.setSourceModel(self.sp_view_model)

        models_ = [ ("Spells", 'table', sp_sort_model, None, None),
                    ("Techs",  'list',  self.th_view_model,
                    models.TechItemDelegate(self), None) ]

        frame_, views_ = self._build_generic_page(models_)
        self.tabs.addTab(frame_, u"Techniques")

    def build_ui_page_4(self):
        mfr    = QtGui.QFrame(self)
        vbox   = QtGui.QVBoxLayout(mfr)

        #self.merit_view_model = models.AdvancementViewModel(self)
        self.merits_view_model = models.PerkViewModel(self.db_conn, 'merit')
        self.flaws_view_model  = models.PerkViewModel(self.db_conn, 'flaws')

        merit_view = QtGui.QListView(self)
        merit_view.setModel(self.merits_view_model)
        merit_view.setItemDelegate(models.PerkItemDelegate(self))
        vbox.addWidget(new_item_groupbox('Advantages', merit_view))

        flaw_view = QtGui.QListView(self)
        flaw_view.setModel(self.flaws_view_model)
        flaw_view.setItemDelegate(models.PerkItemDelegate(self))
        vbox.addWidget(new_item_groupbox('Disadvantages', flaw_view))

        self.tabs.addTab(mfr, u"Perks")

    def build_ui_page_5(self):
        mfr    = QtGui.QFrame(self)
        vbox   = QtGui.QVBoxLayout(mfr)

        fr_    = QtGui.QFrame(self)
        fr_h   = QtGui.QHBoxLayout(fr_)
        fr_h.setContentsMargins(0, 0, 0, 0)
        fr_h.addWidget(QtGui.QLabel("""<p><i>Click the button to refund
                                             the last advancement</i></p>""",
                                                                      self))
        bt_refund_adv = QtGui.QPushButton("Refund", self)
        bt_refund_adv.setSizePolicy( QtGui.QSizePolicy.Maximum,
                                     QtGui.QSizePolicy.Preferred )
        bt_refund_adv.clicked.connect(self.refund_advancement)
        fr_h.addWidget(bt_refund_adv)
        vbox.addWidget(fr_)

        self.adv_view_model = models.AdvancementViewModel(self)
        lview = QtGui.QListView(self)
        lview.setModel(self.adv_view_model)
        lview.setItemDelegate(models.AdvancementItemDelegate(self))
        vbox.addWidget(lview)

        self.adv_view = lview

        self.tabs.addTab(mfr, u"Advancements")

    def build_ui_page_6(self):
        mfr    = QtGui.QFrame(self)
        hbox   = QtGui.QHBoxLayout(mfr)
        hbox.setAlignment(QtCore.Qt.AlignCenter)
        #hbox.setMargin   (30)
        hbox.setSpacing  (30)

        logo = QtGui.QLabel(self);
        logo.setPixmap(QtGui.QPixmap(get_app_icon_path(( 64,64))))
        hbox.addWidget(logo, 0, QtCore.Qt.AlignTop)

        vbox = QtGui.QVBoxLayout()
        vbox.setAlignment(QtCore.Qt.AlignCenter)
        vbox.setSpacing  (30)
        hbox.addLayout   (vbox)

        info = """<html><style>a { color: palette(text); }</style><body><h1>%s</h1>
                  <p>Version %s</p>
                  <p><a href="%s">%s</a></p>
                  <p>Report bugs and send in your ideas <a href="%s">here</a></p>
                  <p>To know about Legend of the Five rings please visit
                  <a href="%s">L5R RPG Home Page</a>
                  </p>
                  <p>
                  All right on Legend of The Five Rings RPG are possession of
                  <p>
                  <a href="%s">Alderac Entertainment Group (AEG)</a>
                  </p>
                  </p>
                  <p style='color:palette(mid)'>&copy; 2011 %s</p>
                  <p>Special Thanks:</p>
                  <p style="margin-left: 10;">
                  Paul Tar, Jr aka Geiko (Minor Clans)
                  </p>
                  </body></html>""" % ( APP_DESC,
                                        QtGui.QApplication.applicationVersion(),
                                        PROJECT_PAGE_LINK, PROJECT_PAGE_NAME,
                                        BUGTRAQ_LINK, L5R_RPG_HOME_PAGE,
                                        ALDERAC_HOME_PAGE, AUTHOR_NAME)
        lb_info = QtGui.QLabel(info, self);
        lb_info.setOpenExternalLinks(True);
        lb_info.setWordWrap(True);
        hbox.addWidget(lb_info);

        self.tabs.addTab(mfr, u"About")

    def build_menu(self):
        # File Menu
        m_file = self.menuBar().addMenu("&File");
        # actions: new, open, save
        new_act         = QtGui.QAction(u'&New Character', self)
        open_act        = QtGui.QAction(u'&Open Character...', self)
        save_act        = QtGui.QAction(u'&Save Character...', self)
        export_text_act = QtGui.QAction(u'Ex&port as Text...', self)
        exit_act        = QtGui.QAction(u'E&xit', self)

        new_act .setShortcut( QtGui.QKeySequence.New  )
        open_act.setShortcut( QtGui.QKeySequence.Open )
        save_act.setShortcut( QtGui.QKeySequence.Save )
        exit_act.setShortcut( QtGui.QKeySequence.Quit )

        m_file.addAction(new_act)
        m_file.addAction(open_act)
        m_file.addAction(save_act)
        m_file.addSeparator()
        m_file.addAction(export_text_act)
        m_file.addSeparator()
        m_file.addAction(exit_act)

        new_act .triggered.connect( self.new_character  )
        open_act.triggered.connect( self.load_character )
        save_act.triggered.connect( self.save_character )
        exit_act.triggered.connect( self.close )

        export_text_act.triggered.connect( self.export_character_as_text )

        self.m_file = m_file

        # Advancement menu
        m_adv = self.menuBar().addMenu("A&dvancement")
        # submenut
        m_buy_adv = m_adv.addMenu("&Buy")

        # actions buy advancement, view advancements
        viewadv_act  = QtGui.QAction(u'&View advancements...', self)
        resetadv_act = QtGui.QAction(u'&Reset advancements', self)
        refund_act   = QtGui.QAction(u'Refund last advancement', self)
        buyattr_act  = QtGui.QAction(u'Attribute rank...', self)
        buyvoid_act  = QtGui.QAction(u'Void ring...', self)
        buyskill_act = QtGui.QAction(u'Skill rank...', self)
        buyemph_act  = QtGui.QAction(u'Skill emphasis...', self)
        buymerit_act = QtGui.QAction(u'Advantage...', self)
        buyflaw_act  = QtGui.QAction(u'Disadvantage...', self)
        # buykata_act  = QtGui.QAction(u'Kata...', self)
        # buykiho_act  = QtGui.QAction(u'Kiho...', self)

        refund_act .setShortcut( QtGui.QKeySequence.Undo  )

        buyattr_act .setProperty('tag', 'attrib')
        buyvoid_act .setProperty('tag', 'void'  )
        buyskill_act.setProperty('tag', 'skill' )
        buyemph_act .setProperty('tag', 'emph'  )
        buymerit_act.setProperty('tag', 'merit' )
        buyflaw_act .setProperty('tag', 'flaw'  )
        # buykata_act .setProperty('tag', 'kata'  )
        # buykiho_act .setProperty('tag', 'kiho'  )

        m_buy_adv.addAction(buyattr_act )
        m_buy_adv.addAction(buyvoid_act )
        m_buy_adv.addAction(buyskill_act)
        m_buy_adv.addAction(buyemph_act )
        m_buy_adv.addAction(buymerit_act)
        m_buy_adv.addAction(buyflaw_act )
        # m_buy_adv.addAction(buykata_act )

        m_adv    .addSeparator()
        m_adv    .addAction(viewadv_act )
        m_adv.addAction(refund_act)
        m_adv.addAction(resetadv_act)

        self.m_adv = m_adv
        self.m_buy = m_buy_adv

        viewadv_act .triggered.connect( self.switch_to_page_5    )
        resetadv_act.triggered.connect( self.reset_adv           )
        refund_act  .triggered.connect( self.refund_last_adv     )
        buyattr_act .triggered.connect( self.act_buy_advancement )
        buyvoid_act .triggered.connect( self.act_buy_advancement )
        buyskill_act.triggered.connect( self.act_buy_advancement )
        buyemph_act .triggered.connect( self.act_buy_advancement )
        # buykata_act .triggered.connect( self.act_buy_advancement )
        # buykiho_act .triggered.connect( self.act_buy_advancement )

        buymerit_act.triggered.connect( self.act_buy_perk )
        buyflaw_act .triggered.connect( self.act_buy_perk )

        # Tools menu
        #m_tools = self.menuBar().addMenu(u'&Tools')

        # Name generator submenu
        m_namegen = self.menuBar().addMenu(u'&Generate Name')

        # actions generate female, male names
        gen_male_act   = QtGui.QAction(u'Male', self)
        gen_female_act = QtGui.QAction(u'Female', self)

        # gender tag
        gen_male_act.setProperty  ('gender', 'male')
        gen_female_act.setProperty('gender', 'female')

        m_namegen.addAction(gen_male_act)
        m_namegen.addAction(gen_female_act)

        self.m_namegen = m_namegen

        gen_male_act  .triggered.connect( self.generate_name )
        gen_female_act.triggered.connect( self.generate_name )

        # Outfit menu
        m_outfit = self.menuBar().addMenu(u'Out&fit')

        # actions, select armor, add weapon, add misc item
        sel_armor_act      = QtGui.QAction(u'Wear Armor...'       , self)
        sel_cust_armor_act = QtGui.QAction(u'Wear Custom Armor...', self)
        add_weap_act       = QtGui.QAction(u'Add Weapon...'       , self)
        add_cust_weap_act  = QtGui.QAction(u'Add Custom Weapon...', self)
        # add_misc_item_act  = QtGui.QAction(u'Add Misc Item...'    , self)

        add_weap_act     .setEnabled(False)
        add_cust_weap_act.setEnabled(False)
        # add_misc_item_act.setEnabled(False)

        m_outfit.addAction(sel_armor_act     )
        m_outfit.addAction(sel_cust_armor_act)
        m_outfit.addAction(add_weap_act      )
        m_outfit.addAction(add_cust_weap_act )
        # m_outfit.addAction(add_misc_item_act )

        sel_armor_act     .triggered.connect( self.show_wear_armor      )
        sel_cust_armor_act.triggered.connect( self.show_wear_cust_armor )
        add_weap_act      .triggered.connect( self.show_add_weapon      )
        add_cust_weap_act .triggered.connect( self.show_add_cust_weapon )
        # add_misc_item_act .triggered.connect( self.show_add_misc_item   )

        # Rules menu
        m_rules = self.menuBar().addMenu(u'&Rules')

        # rules actions
        set_exp_limit_act  = QtGui.QAction(u'Set Experience Limit...' , self)
        set_wound_mult_act = QtGui.QAction(u'Set Health Multiplier...', self)
        unlock_school_act  = QtGui.QAction(u'Lock Schools...'         , self)
        unlock_advans_act  = QtGui.QAction(u'Lock Advancements...'    , self)
        damage_act         = QtGui.QAction(u'Cure/Inflict Damage...'  , self)

        unlock_school_act.setCheckable(True)
        unlock_advans_act.setCheckable(True)

        unlock_school_act.setChecked(True)
        unlock_advans_act.setChecked(True)

        self.unlock_schools_menu_item = unlock_school_act
        self.unlock_advans_menu_item  = unlock_advans_act

        m_rules.addAction(set_exp_limit_act )
        m_rules.addAction(set_wound_mult_act)
        m_rules.addAction(unlock_school_act )
        m_rules.addAction(unlock_advans_act )
        m_rules.addSeparator()
        m_rules.addAction(damage_act)

        set_exp_limit_act .triggered.connect( self.on_set_exp_limit      )
        set_wound_mult_act.triggered.connect( self.on_set_wnd_mult       )
        damage_act        .triggered.connect( self.on_damage_act         )
        unlock_school_act .triggered.connect( self.on_unlock_school_act  )
        unlock_advans_act .toggled  .connect( self.on_toggle_advans_act  )

    def connect_signals(self):

        # only user change
        self.cb_pc_clan  .activated.connect( self.on_clan_change   )

        # user and programmatically change
        self.cb_pc_family.currentIndexChanged.connect( self.on_family_change )
        self.cb_pc_school.currentIndexChanged.connect( self.on_school_change )

        # notify only user edit
        self.tx_mod_init.editingFinished.connect( self.update_from_model )

        # update model name
        self.tx_pc_name.editingFinished.connect( self.on_pc_name_change )

        for widget in self.pc_flags_points:
            widget.valueChanged.connect( self.on_flag_points_change )
        for tx in self.pc_flags_rank:
            tx.editingFinished.connect( self.on_flag_rank_change )

        self.void_points.valueChanged.connect( self.on_void_points_change )

        self.trait_sig_mapper.connect(QtCore.SIGNAL("mapped(const QString &)"),
                                      self,
                                      QtCore.SLOT("on_trait_increase(const QString &)"))

    def switch_to_page_1(self):
        self.tabs.setCurrentIndex(0)

    def switch_to_page_2(self):
        self.tabs.setCurrentIndex(1)

    def switch_to_page_3(self):
        self.tabs.setCurrentIndex(2)

    def switch_to_page_4(self):
        self.tabs.setCurrentIndex(3)

    def switch_to_page_5(self):
        self.tabs.setCurrentIndex(4)

    def show_nicebar(self, widgets):
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

        # nicebar layout
        hbox = QtGui.QHBoxLayout(self.nicebar)
        hbox.setContentsMargins(9,1,9,1)

        for w in widgets:
            hbox.addWidget(w)

        self.mvbox.insertWidget(1, self.nicebar)

        self.nicebar.setVisible(True)

    def hide_nicebar(self):
        if not self.nicebar:
            return
        self.nicebar.setVisible(False)
        del self.nicebar
        self.nicebar = None

    def reset_adv(self):
        self.pc.advans = []
        self.pc.reset_techs()
        self.pc.reset_spells()
        self.update_from_model()

    def refund_last_adv(self):
        if len(self.pc.advans) > 0:
            adv = self.pc.advans.pop()

            if self.pc.get_how_many_spell_i_miss() < 0:
                self.pc.pop_spells(-self.pc.get_how_many_spell_i_miss())
            if len(self.pc.get_techs()) > self.pc.get_insight_rank():
                self.pc.reset_techs()
            self.update_from_model()

    def refund_advancement(self, adv_idx = -1):
        if self.lock_advancements:
            return self.refund_last_adv()

        if adv_idx < 0:
            adv_idx = len(self.pc.advans) - self.adv_view.selectionModel().currentIndex().row() - 1

        if adv_idx >= len(self.pc.advans) or adv_idx < 0:
            return

        del self.pc.advans[adv_idx]

        if self.pc.get_how_many_spell_i_miss() < 0:
            self.pc.pop_spells(-self.pc.get_how_many_spell_i_miss())
        if len(self.pc.get_techs()) > self.pc.get_insight_rank():
            self.pc.reset_techs()
            self.update_from_model()

    def generate_name(self):
        gender = self.sender().property('gender')
        name = ''
        if gender == 'male':
            name = rules.get_random_name( get_app_file('male.txt') )
        else:
            name = rules.get_random_name( get_app_file('female.txt') )
        self.pc.name = name
        self.update_from_model()

    def on_trait_increase(self, text):
        attrib = models.attrib_from_name(text)
        cur_value = self.pc.get_attrib_rank( attrib )
        new_value = cur_value + 1
        ring_id = models.get_ring_id_from_attrib_id(attrib)
        ring_nm = models.ring_name_from_id(ring_id)
        cost = self.pc.get_attrib_cost( attrib ) * new_value
        if self.pc.has_rule('elem_bless_%s' % ring_nm):
            cost -= 1
        adv = models.AttribAdv(attrib, cost)
        adv.desc = '%s, Rank %d to %d. Cost: %d xp' % ( text, cur_value, new_value, cost )
        if (adv.cost + self.pc.get_px()) > self.pc.exp_limit:
            QtGui.QMessageBox.warning(self, "Not enough XP",
            "Cannot purchase.\nYou've reached the XP Limit.")
            return

        self.pc.add_advancement( adv )
        self.update_from_model()

    def on_void_increase(self):
        cur_value = self.pc.get_ring_rank( RINGS.VOID )
        new_value = cur_value + 1
        cost = self.pc.void_cost * new_value
        if self.pc.has_rule('enlightened'):
            cost -= 2
        adv = models.VoidAdv(cost)
        adv.desc = 'Void Ring, Rank %d to %d. Cost: %d xp' % ( cur_value, new_value, cost )
        if (adv.cost + self.pc.get_px()) > self.pc.exp_limit:
            QtGui.QMessageBox.warning(self, "Not enough XP",
            "Cannot purchase.\nYou've reached the XP Limit.")
            return

        self.pc.add_advancement( adv )
        self.update_from_model()

    def on_set_exp_limit(self):
        ok = False
        val, ok = QtGui.QInputDialog.getInt(self, 'Set Experience Limit',
                                       "XP Limit:", self.pc.exp_limit,
                                        0, 10000, 1)
        if ok:
            self.pc.exp_limit = val
            self.update_from_model()

    def on_set_wnd_mult(self):
        ok = False
        val, ok = QtGui.QInputDialog.getInt(self, 'Set Health Multiplier',
                                       "Multiplier:", self.pc.health_multiplier,
                                        2, 5, 1)
        if ok:
            self.pc.health_multiplier = val
            self.update_from_model()

    def on_damage_act(self):
        ok = False
        val, ok = QtGui.QInputDialog.getInt(self, 'Cure/Inflict Damage',
                                       "Wounds:", 1,
                                        -1000, 1000, 1)
        if ok:
            self.pc.wounds += val
            if self.pc.wounds < 0: self.pc.wounds = 0
            if self.pc.wounds > self.pc.get_max_wounds():
                self.pc.wounds = self.pc.get_max_wounds()

            self.update_from_model()

    def on_unlock_school_act(self):
        self.pc.toggle_unlock_schools()
        if self.pc.unlock_schools:
            self.load_schools ()
        else:
            self.load_schools(self.pc.clan)
        self.cb_pc_school.setCurrentIndex(0)

    def on_toggle_advans_act(self, flag):
        if flag == False:
            result = QtGui.QMessageBox.warning(self, "Advancements unlock",
                "Unlocking the advancements will permits you to Undo any"
                "advancement with no specific order.\n"
                "This may lead to incoerence and may permit \"cheating\".\n"
                "Continue anyway?",
                QtGui.QMessageBox.StandardButton.Yes or QtGui.QMessageBox.StandardButton.No,
                QtGui.QMessageBox.StandardButton.No)
            if result == QtGui.QMessageBox.StandardButton.Yes:
                self.lock_advancements = False
        else:
            self.lock_advancements = True

    def on_clan_change(self, text):
        #print 'on_clan_change %s' % text
        #self.cb_pc_family.clear()
        index = self.cb_pc_clan.currentIndex()
        if index < 0:
            self.pc.clan = 0
        else:
            clan_id = self.cb_pc_clan.itemData(index)

            #print 'set new clan. cur: %d new %d' % ( self.pc.clan, clan_id )
            self.pc.clan = clan_id

        self.load_families(self.pc.clan)
        if self.pc.unlock_schools:
            self.load_schools ()
        else:
            self.load_schools(self.pc.clan)
        self.cb_pc_family.setCurrentIndex(0)
        self.cb_pc_school.setCurrentIndex(0)

    def on_family_change(self, text):
        index = self.cb_pc_family.currentIndex()
        #print 'on family changed %s %d' % (text, index)
        if index <= 0:
            self.pc.set_family()
            self.update_from_model()
            return

        uuid  = self.cb_pc_family.itemData(index)
        if uuid == self.pc.family:
            return
        # should modify step_1 character
        # get family perk

        c = self.db_conn.cursor()
        c.execute('''select uuid, name from clans where uuid=?''', [self.pc.clan])
        clan_uuid, clan_name = c.fetchone()

        c.execute('''select name, perk, perkval from families
                     where uuid=?''', [uuid])
        for name, perk, perkval in c.fetchall():
            self.pc.set_family( uuid, perk, perkval, [name.lower(), clan_name.lower()] )
            self.update_from_model()
            break

        c.close()

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
        c.execute('''select name, perk, perkval, honor, tag from schools
                     where uuid=?''', [uuid])
        name, perk, perkval, honor, tag = c.fetchone()
        self.pc.set_school( uuid, perk, perkval, honor, [name.lower(), tag] )

        c.execute('''select skill_uuid, skill_rank, wildcard, emphases
                     from school_skills
                     where school_uuid=?''', [uuid])
        for sk_uuid, sk_rank, wc, emph in c.fetchall():
            if sk_uuid is not None:
                self.pc.add_school_skill(sk_uuid, sk_rank, emph)
            else:
                self.pc.add_pending_wc_skill(wc, sk_rank)

        # get school tech rank 1
        c.execute('''select uuid, effect from school_techs
                     where school_uuid=? and rank=1''', [uuid])

        for th_uuid, rule in c.fetchall():
            self.pc.set_free_school_tech( th_uuid, rule )
            break

        # if shugenja get universal spells
        # also player should choose some spells from list

        if tag == 'shugenja':
            count = 0
            c.execute('''select spell_uuid, wildcard from school_spells
                      where school_uuid=?''', [uuid])
            for sp_uuid, wc in c.fetchall():
                if sp_uuid is None:
                    ring, qty = rules.parse_spell_wildcard(wc)
                    print 'add pending wc spell %s' % wc
                    self.pc.add_pending_wc_spell(wc)
                    count += qty
                else:
                    self.pc.add_free_spell(sp_uuid)
                    count += 1

            print 'starting spells count are %d' % count
            self.pc.set_school_spells_qty(count)

        c.close()
        self.update_from_model()

    def on_pc_name_change(self):
        self.pc.name = self.tx_pc_name.text()

    def on_flag_points_change(self):
        fl  = self.sender()
        pt = fl.value
        if fl == self.pc_flags_points[0]:
            val = int(self.pc_flags_rank[0].text())
            self.pc.set_honor( float(val + float(pt)/10 ) )
        elif fl == self.pc_flags_points[1]:
            val = int(self.pc_flags_rank[1].text())
            self.pc.set_glory( float(val + float(pt)/10 ) )
        elif fl == self.pc_flags_points[2]:
            val = int(self.pc_flags_rank[2].text())
            self.pc.set_status( float(val + float(pt)/10 ) )
        else:
            val = int(self.pc_flags_rank[3].text())
            self.pc.set_taint( float(val + float(pt)/10 ) )

    def on_flag_rank_change(self):
        fl  = self.sender()
        val = int(fl.text())
        if fl == self.pc_flags_rank[0]:
            pt = self.pc_flags_points[0].value
            self.pc.set_honor( float(val + float(pt)/10 ) )
        elif fl == self.pc_flags_rank[1]:
            pt = self.pc_flags_points[1].value
            self.pc.set_glory( float(val + float(pt)/10 ) )
        elif fl == self.pc_flags_rank[2]:
            pt = self.pc_flags_points[2].value
            self.pc.set_status( float(val + float(pt)/10 ) )
        else:
            pt = self.pc_flags_points[3].value
            self.pc.set_taint( float(val + float(pt)/10 ) )

    def on_void_points_change(self):
        val = self.void_points.value
        self.pc.set_void_points(val)

    def act_buy_advancement(self):
        dlg = dialogs.BuyAdvDialog(self.pc, self.sender().property('tag'),
                                   self.db_conn, self)
        dlg.exec_()
        self.update_from_model()

    def show_buy_skill_dlg(self):
        dlg = dialogs.BuyAdvDialog(self.pc, 'skill',
                                   self.db_conn, self)
        dlg.exec_()
        self.update_from_model()

    def buy_skill_rank(self):
        # get selected skill
        sm_ = self.skill_table_view.selectionModel()
        if sm_.hasSelection():
            idx = sm_.currentIndex()
            skill_id = self.sk_view_model.data(idx)

            cur_value = self.pc.get_skill_rank( skill_id )
            new_value = cur_value + 1

            idx  = self.sk_view_model.index(idx.row(), 0)
            text = self.sk_view_model.data(idx, QtCore.Qt.DisplayRole)

            cost = new_value

            adv = models.SkillAdv(skill_id, cost)
            adv.desc = '%s, Rank %d to %d. Cost: %d xp' % ( text, cur_value, new_value, cost )

            if adv.cost + self.pc.get_px() > self.pc.exp_limit:
                QtGui.QMessageBox.warning(self, "Not enough XP",
                "Cannot purchase.\nYou've reached the XP Limit.")
                return

            self.pc.add_advancement(adv)
            self.update_from_model()
            sm_.setCurrentIndex(idx, QtGui.QItemSelectionModel.Select | \
                                     QtGui.QItemSelectionModel.Rows)

    def act_buy_perk(self):
        dlg = dialogs.BuyPerkDialog(self.pc, self.sender().property('tag'),
                                    self.db_conn, self)
        dlg.exec_()
        self.update_from_model()

    def act_choose_skills(self):
        dlg = dialogs.SelWcSkills(self.pc, self.db_conn, self)
        if dlg.exec_() == QtGui.QDialog.DialogCode.Accepted:
            self.pc.clear_pending_wc_skills()
            self.pc.clear_pending_wc_emphs ()
            self.update_from_model()

    def learn_next_school_tech(self):
        # for now do not support multiple school advantage
        # learn next technique for your school

        next_rank = len(self.pc.get_techs()) + 1

        c = self.db_conn.cursor()
        c.execute('''select uuid, name, effect from school_techs
                     where school_uuid=? and rank=?''', [self.pc.school, next_rank])
        for uuid, name, rule in c.fetchall():
            self.pc.add_tech(int(uuid), rule)

        c.close()

        self.switch_to_page_3 ()
        self.update_from_model()

    def check_if_tech_available(self):
        c = self.db_conn.cursor()
        c.execute('''select COUNT(uuid) from school_techs
                     where school_uuid=?''', [self.pc.school])
        count_ = c.fetchone()[0]
        c.close()
        return count_ > len(self.pc.get_techs())

    def check_school_tech_and_spells(self):
        # Show nicebar if can get another school tech
        if self.pc.can_get_other_techs() and self.check_if_tech_available():
            #print 'can get more techniques'
            lb = QtGui.QLabel("You reached enough insight Rank to learn another School Technique")
            bt = QtGui.QPushButton('Learn Technique')
            bt.setSizePolicy( QtGui.QSizePolicy.Maximum,
                              QtGui.QSizePolicy.Preferred)
            bt.clicked.connect( self.learn_next_school_tech )
            self.show_nicebar([lb, bt])
        elif self.pc.can_get_other_spells():
            lb = QtGui.QLabel("You reached enough insight Rank to learn other Spells")
            bt = QtGui.QPushButton('Learn Spells')
            bt.setSizePolicy( QtGui.QSizePolicy.Maximum,
                              QtGui.QSizePolicy.Preferred)
            bt.clicked.connect( self.learn_next_school_spells )
            self.show_nicebar([lb, bt])

    def check_rules(self):
        c = self.db_conn.cursor()
        for t in self.pc.get_techs():
            c.execute('''select uuid, effect from school_techs
                         where uuid=?''', [t])
            for uuid, rule in c.fetchall():
                self.pc.add_tech(int(uuid), rule)
                break

        for adv in self.pc.advans:
            if adv.type == 'perk':
                c.execute('''select uuid, rule from perks
                             where uuid=?''', [adv.perk])
                for uuid, rule in c.fetchall():
                    print 'found character rule %s' % rule
                    adv.rule = rule
                    break
        c.close()

    def learn_next_school_spells(self):
        dlg = dialogs.SelWcSpells(self.pc, self.db_conn, self)
        if dlg.exec_() == QtGui.QDialog.DialogCode.Accepted:
            self.pc.clear_pending_wc_spells()
            self.update_from_model()

    def show_wear_armor(self):
        dlg = dialogs.ChooseItemDialog(self.pc, 'armor', self.db_conn, self)
        if dlg.exec_() == QtGui.QDialog.DialogCode.Accepted:
            self.update_from_model()

    def show_wear_cust_armor(self):
        dlg = dialogs.CustomArmorDialog(self.pc, self)
        if dlg.exec_() == QtGui.QDialog.DialogCode.Accepted:
            self.update_from_model()

    def show_add_weapon(self):
        dlg = dialogs.ChooseItemDialog(self.pc, 'weapon', self.db_conn, self)
        if dlg.exec_() == QtGui.QDialog.DialogCode.Accepted:
            self.update_from_model()


    def show_add_cust_weapon(self):
        pass

    def show_add_misc_item(self):
        pass

    def new_character(self):
        self.save_path = ''
        self.pc = models.AdvancedPcModel()
        self.pc.load_default()
        self.load_clans()
        #self.load_schools(0)
        #self.load_families(0)
        self.update_from_model()

    def load_character(self):
        path = self.select_load_path()
        self.load_character_from(path)

    def load_character_from(self, path):
        pause_signals( [self.tx_pc_name, self.cb_pc_clan, self.cb_pc_family,
                        self.cb_pc_school] )

        self.save_path = path
        if self.pc.load_from(self.save_path):

            if float(self.pc.version) < float(DB_VERSION):
                # BACKUP CHARACTER
                backup_path = self.save_path + '.bak'
                self.pc.save_to(backup_path)
                # CONVERT CHARACTER
                import past
                past_db = 'l5rdb_%s.sqlite' % self.pc.version
                if not os.path.exists(get_app_file(past_db)):
                    past_db = 'l5rdb_past.sqlite'
                print 'converting character using database %s' % past_db
                cc = past.CharConvert(self.pc, get_app_file(past_db), get_app_file('l5rdb.sqlite') )
                cc.start()
                # SAVE CHARACTER
                self.save_character()
                # ADVISE USER
                self.advise_conversion(backup_path)

            self.load_families(self.pc.clan)
            if self.pc.unlock_schools:
                self.load_schools ()
            else:
                self.load_schools (self.pc.clan)

            self.check_rules()
            self.update_from_model()

        resume_signals( [self.tx_pc_name, self.cb_pc_clan, self.cb_pc_family,
                        self.cb_pc_school] )

    def save_character(self):
        if self.save_path == '' or not os.path.exists(self.save_path):
            self.save_path = self.select_save_path()

        if self.save_path is not None and len(self.save_path) > 0:
            self.pc.version = DB_VERSION
            self.pc.save_to(self.save_path)

    def load_clans(self):
        c = self.db_conn.cursor()
        # clans
        self.cb_pc_clan.clear()
        self.cb_pc_clan.addItem( 'No Clan', 0 )
        c.execute('''select uuid, name from clans order by name asc''')
        for f in c.fetchall():
            self.cb_pc_clan.addItem( f[1], f[0] )
        c.close()

    def load_schools(self, clan_id = -1):
        #print 'load schools for clan_id %d' % clan_id
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
        c.close()

    def load_families(self, clan_id):
        #print 'load families for clan_id %d' % clan_id

        c = self.db_conn.cursor()
        self.cb_pc_family.clear()
        if clan_id <= 0:
            return
        else:
            c.execute('''select uuid, name from families where clan_id=?
                         order by name asc''',
                         [clan_id])

        self.cb_pc_family.addItem( 'No Family', 0 )
        for f in c.fetchall():
            self.cb_pc_family.addItem( f[1], f[0] )
        c.close()

    def set_clan(self, clan_id):
        idx = self.cb_pc_clan.currentIndex()
        c_uuid = self.cb_pc_clan.itemData(idx)

        #print 'set clan. cur: %d new: %d' % (c_uuid, clan_id)

        if c_uuid == clan_id:
            return
        for i in xrange(0, self.cb_pc_clan.count()):
            if self.cb_pc_clan.itemData(i) == clan_id:
                self.cb_pc_clan.setCurrentIndex(i)
                return

    def set_family(self, family_id):
        idx = self.cb_pc_family.currentIndex()
        f_uuid = self.cb_pc_family.itemData(idx)
        if f_uuid == family_id:
            return
        for i in xrange(0, self.cb_pc_family.count()):
            if self.cb_pc_family.itemData(i) == family_id:
                self.cb_pc_family.setCurrentIndex(i)
                return

    def set_school(self, school_id):
        idx = self.cb_pc_school.currentIndex()
        s_uuid = self.cb_pc_school.itemData(idx)

        #print 'set school to %s, current school is %s' % (school_id, s_uuid)
        if s_uuid == school_id:
            return
        for i in xrange(0, self.cb_pc_school.count()):
            if self.cb_pc_school.itemData(i) == school_id:
                self.cb_pc_school.setCurrentIndex(i)
                return

    def set_void_points(self, value):
        if self.void_points.value == value:
            return
        self.void_points.set_value(value)

    def set_flag(self, flag, value):
        rank, points = split_decimal(value)
        # set rank
        self.pc_flags_rank[flag].setText( str(rank) )
        # set points
        self.pc_flags_points[flag].set_value( int(points*10) )

    def set_honor (self, value): self.set_flag(0, value)
    def set_glory (self, value): self.set_flag(1, value)
    def set_status(self, value): self.set_flag(2, value)
    def set_taint (self, value): self.set_flag(3, value)

    def update_from_model(self):

        pause_signals( [self.tx_pc_name, self.cb_pc_clan, self.cb_pc_family,
                        self.cb_pc_school] )

        self.tx_pc_name.setText( self.pc.name   )
        self.set_clan          ( self.pc.clan   )
        self.set_family        ( self.pc.family )
        self.set_school        ( self.pc.school )

        resume_signals( [self.tx_pc_name, self.cb_pc_clan, self.cb_pc_family,
                        self.cb_pc_school] )

        pc_xp = self.pc.get_px()
        self.tx_pc_exp.setText( '%d / %d' % ( pc_xp, self.pc.exp_limit ) )

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
        pause_signals( self.pc_flags_points )
        pause_signals( self.pc_flags_rank   )
        pause_signals( [self.void_points]   )

        self.set_honor ( self.pc.get_honor()  )
        self.set_glory ( self.pc.get_glory()  )
        self.set_status( self.pc.get_status() )
        self.set_taint ( self.pc.get_taint()  )

        self.set_void_points( self.pc.void_points )

        resume_signals( [self.void_points]   )
        resume_signals( self.pc_flags_points )
        resume_signals( self.pc_flags_rank   )

        # armor tn
        self.tx_armor_nm .setText( str(self.pc.get_armor_name())  )
        self.tx_base_tn  .setText( str(self.pc.get_base_tn())     )
        self.tx_armor_tn .setText( str(self.pc.get_armor_tn())    )
        self.tx_armor_rd .setText( str(self.pc.get_armor_rd())    )
        self.tx_cur_tn   .setText( str(self.pc.get_cur_tn())      )

        # health
        for i in xrange(0, 8):
            h = self.pc.get_health_rank(i)
            self.wounds[i][1].setText( str(h) )
            self.wounds[i][2].setText( '' )
        self.wnd_lb.setTitle('Health / Wounds (x%d)' % self.pc.health_multiplier)

        # wounds
        pc_wounds = self.pc.wounds
        hr        = 0
        while pc_wounds and hr < 8:
            w = min(pc_wounds, self.pc.get_health_rank(hr))
            self.wounds[hr][2].setText( str(w) )
            pc_wounds -= w
            hr += 1

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

        self.hide_nicebar()

        # Show nicebar if pending wildcard skills
        wcs = self.pc.get_pending_wc_skills()
        if len(wcs) > 0:
            lb = QtGui.QLabel('Your school gives you the choice of certain skills')
            bt = QtGui.QPushButton('Choose Skills')
            bt.setSizePolicy( QtGui.QSizePolicy.Maximum,
                              QtGui.QSizePolicy.Preferred)
            bt.clicked.connect( self.act_choose_skills )
            self.show_nicebar([lb, bt])
        #else:
        #    self.hide_nicebar()

        if not self.nicebar:
            self.check_school_tech_and_spells()

        # disable step 0-1-2 if any xp are spent
        has_adv = len(self.pc.advans) > 0
        self.cb_pc_clan  .setEnabled( not has_adv )
        self.cb_pc_school.setEnabled( not has_adv )
        self.cb_pc_family.setEnabled( not has_adv )

        # also disable schools lock/unlock
        self.unlock_schools_menu_item.setChecked( not self.pc.unlock_schools )
        self.unlock_schools_menu_item.setEnabled( not has_adv )

        # Update view-models
        self.sk_view_model    .update_from_model(self.pc)
        self.ma_view_model    .update_from_model(self.pc)
        self.adv_view_model   .update_from_model(self.pc)
        self.th_view_model    .update_from_model(self.pc)
        self.merits_view_model.update_from_model(self.pc)
        self.flaws_view_model .update_from_model(self.pc)
        self.sp_view_model    .update_from_model(self.pc)

    def advise_conversion(self, *args):
        settings = QtCore.QSettings()
        if settings.value('advise_conversion', 'true') == 'false':
            return
        msgBox = QtGui.QMessageBox(self)
        msgBox.setWindowTitle('L5R: CM')
        msgBox.setText("The character has been updated.")
        msgBox.setInformativeText("This character was created with an older version of the program.\n"
                                  "I've done my best to convert and update your character, hope you don't mind :).\n"
                                  "I also created a backup of your character file in\n\n%s." % args)
        do_not_prompt_again = QtGui.QCheckBox("Do not prompt again", msgBox)
        do_not_prompt_again.blockSignals(True) # PREVENT MSGBOX TO CLOSE ON CLICK
        msgBox.addButton(QtGui.QMessageBox.Ok)
        msgBox.addButton(do_not_prompt_again, QtGui.QMessageBox.ActionRole)
        msgBox.setDefaultButton(QtGui.QMessageBox.Ok)
        msgBox.exec_()
        if do_not_prompt_again.checkState() == QtCore.Qt.Checked:
            settings.setValue('advise_conversion', 'false')

    def ask_to_save(self):
         msgBox = QtGui.QMessageBox(self)
         msgBox.setWindowTitle('L5R: CM')
         msgBox.setText("The character has been modified.")
         msgBox.setInformativeText("Do you want to save your changes?")
         msgBox.addButton( QtGui.QMessageBox.Save )
         msgBox.addButton( QtGui.QMessageBox.Discard )
         msgBox.addButton( QtGui.QMessageBox.Cancel )
         msgBox.setDefaultButton(QtGui.QMessageBox.Save)
         return msgBox.exec_()

    def ask_to_upgrade(self, target_version):
         msgBox = QtGui.QMessageBox(self)
         msgBox.setWindowTitle('L5R: CM')
         msgBox.setText("L5R: CM v%s is available for download." % target_version)
         msgBox.setInformativeText("Do you want to open the download page?")
         msgBox.addButton( QtGui.QMessageBox.Yes )
         msgBox.addButton( QtGui.QMessageBox.No )
         msgBox.setDefaultButton(QtGui.QMessageBox.No)
         return msgBox.exec_()

    def closeEvent(self, ev):
        # SAVE GEOMETRY
        settings = QtCore.QSettings()
        settings.setValue('geometry', self.saveGeometry())

        if self.pc.is_dirty():
            resp = self.ask_to_save()
            if resp == QtGui.QMessageBox.Save:
                self.save_character()
                pass
            elif resp == QtGui.QMessageBox.Cancel:
                ev.ignore()
            else:
                super(L5RMain, self).closeEvent(ev)
        else:
            super(L5RMain, self).closeEvent(ev)

    def select_save_path(self):
        settings = QtCore.QSettings()
        last_dir = settings.value('last_open_dir', QtCore.QDir.homePath())
        fileName = QtGui.QFileDialog.getSaveFileName(self, "Save Character",
                                last_dir,
                                "L5R Character files (*.l5r)")
        if len(fileName) != 2:
            return ''

        last_dir = os.path.dirname(fileName[0])
        if last_dir != '':
            #print 'save last_dir: %s' % last_dir
            settings.setValue('last_open_dir', last_dir)

        if fileName[0].endswith('.l5r'):
            return fileName[0]
        return fileName[0] + '.l5r'

    def select_load_path(self):
        settings = QtCore.QSettings()
        last_dir = settings.value('last_open_dir', QtCore.QDir.homePath())
        fileName = QtGui.QFileDialog.getOpenFileName(self, "Load Character",
                                last_dir,
                                "L5R Character files (*.l5r)")
        if len(fileName) != 2:
            return ''
        last_dir = os.path.dirname(fileName[0])
        if last_dir != '':
            #print 'save last_dir: %s' % last_dir
            settings.setValue('last_open_dir', last_dir)
        return fileName[0]

    def select_export_file(self):
        char_name = self.pc.name

        settings = QtCore.QSettings()
        last_dir = settings.value('last_open_dir', QtCore.QDir.homePath())
        fileName = QtGui.QFileDialog.getSaveFileName(self, "Export Character",
                                os.path.join(last_dir,char_name),
                                "Text files(*.txt)")
        if len(fileName) != 2:
            return ''

        last_dir = os.path.dirname(fileName[0])
        if last_dir != '':
            settings.setValue('last_open_dir', last_dir)

        if fileName[0].endswith('.txt'):
            return fileName[0]
        return fileName[0] + '.txt'

    def check_updates(self):
        update_info = autoupdate.get_last_version()
        if update_info is not None and \
           autoupdate.need_update(APP_VERSION, update_info['version']) and \
           self.ask_to_upgrade(update_info['version']) == QtGui.QMessageBox.Yes:

            import osutil
            osutil.portable_open(PROJECT_PAGE_LINK)

    def export_character_as_text(self):
        file_ = self.select_export_file()
        if len(file_) > 0:
            self.export_as_text(file_)

    def export_as_text(self, export_file):
        exporter = exporters.TextExporter()
        exporter.set_form (self)
        exporter.set_model(self.pc     )
        #exporter.set_db   (self.db_conn)

        f = open(export_file, 'wt')
        if f is not None:
            exporter.export(f)
        f.close()



### MAIN ###
def main():
    app = QtGui.QApplication(sys.argv)

    QtCore.QCoreApplication.setApplicationName(APP_NAME)
    QtCore.QCoreApplication.setApplicationVersion(APP_VERSION)
    QtCore.QCoreApplication.setOrganizationName(APP_ORG)

    app.setWindowIcon( QtGui.QIcon( get_app_icon_path() ) )

    l5rcm = L5RMain()
    l5rcm.setWindowTitle(APP_DESC + ' v' + APP_VERSION)
    l5rcm.show()

    # check for updates
    l5rcm.check_updates()

    # initialize new character
    l5rcm.new_character()

    if len(sys.argv) > 1:
        print 'load character file %s' % sys.argv[1]
        l5rcm.load_character_from(sys.argv[1])
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
