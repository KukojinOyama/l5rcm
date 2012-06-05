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

import sys
import os
import sqlite3

import rules
import models
import widgets
import dialogs
import autoupdate
import tempfile
import exporters
import dbutil
import sinks

from PySide import QtGui, QtCore
from models.chmodel import ATTRIBS, RINGS

from l5rcmcore import *

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

def pause_signals(widgets):
    for w in widgets: w.blockSignals(True)

def resume_signals(widgets):
    for w in widgets: w.blockSignals(False)

class L5RMain(QtGui.QMainWindow, L5RCMCore):
    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self)
        L5RCMCore.__init__(self)

        # character file save path
        self.save_path = ''        
        
        # slot sinks
        self.sink1 = sinks.Sink1(self) # Menu Sink
        self.sink2 = sinks.Sink2(self) # MeritFlaw Sink
        self.sink3 = sinks.Sink3(self) # Weapons Sink
        self.sink4 = sinks.Sink4(self) # Weapons Sink

        # Build interface and menus
        self.build_ui()
        self.build_menu()

        # Build page 1
        self.build_ui_page_1()
        self.build_ui_page_2()
        self.build_ui_page_3()
        self.build_ui_page_4()
        self.build_ui_page_5()
        self.build_ui_page_6()
        self.build_ui_page_7()
        self.build_ui_page_8()
        self.build_ui_page_9()
        
        self.connect_signals()

    def build_ui(self):
        # Main interface widgets
        self.widgets = QtGui.QWidget(self)
        self.tabs = QtGui.QTabWidget(self)
        self.tabs.setTabPosition( QtGui.QTabWidget.TabPosition.West )
        self.setCentralWidget(self.widgets)

        self.nicebar = None        

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
        
        self.ic_idx = int(settings.value('insight_calculation', 1))-1
        ic_calcs    = [rules.insight_calculation_1,
                       rules.insight_calculation_2,
                       rules.insight_calculation_3]
        if self.ic_idx not in range(0, 3):
            self.ic_idx = 0
        self.ic_calc_method = ic_calcs[self.ic_idx]

    def build_ui_page_1(self):

        mfr = QtGui.QFrame(self)
        self.tabs.addTab(mfr, self.tr("Character"))

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
            grid.addWidget( QtGui.QLabel(self.tr("Name"  ), self), 0, 0 )
            grid.addWidget( QtGui.QLabel(self.tr("Clan"  ), self), 1, 0 )
            grid.addWidget( QtGui.QLabel(self.tr("Family"), self), 2, 0 )
            grid.addWidget( QtGui.QLabel(self.tr("School"), self), 3, 0 )

            # 3rd column
            grid.addWidget( QtGui.QLabel(self.tr("Rank")       , self), 0, 3 )
            grid.addWidget( QtGui.QLabel(self.tr("Exp. Points"), self), 1, 3 )
            grid.addWidget( QtGui.QLabel(self.tr("Insight")    , self), 2, 3 )

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
            grp = QtGui.QGroupBox(self.tr("Rings and Attributes"), self)
            grid = QtGui.QGridLayout(grp)
            grid.setSpacing(1)

            # rings
            rings = []
            rings.append( ( self.tr("Earth"), new_small_le(self) ) )
            rings.append( ( self.tr("Air"  ), new_small_le(self) ) )
            rings.append( ( self.tr("Water"), new_small_le(self) ) )
            rings.append( ( self.tr("Fire" ), new_small_le(self) ) )
            rings.append( ( self.tr("Void" ), new_small_le(self) ) )

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
            attribs.append( (self.tr("Stamina"  ), new_small_le(self)) )
            attribs.append( (self.tr("Willpower"), new_small_le(self)) )
            attribs[0][1].setProperty('attrib_id', ATTRIBS.STAMINA)
            attribs[1][1].setProperty('attrib_id', ATTRIBS.WILLPOWER)
            # Air ring
            attribs.append( (self.tr("Reflexes" ), new_small_le(self)) )
            attribs.append( (self.tr("Awareness"), new_small_le(self)) )
            attribs[2][1].setProperty('attrib_id', ATTRIBS.REFLEXES)
            attribs[3][1].setProperty('attrib_id', ATTRIBS.AWARENESS)
            # Water ring
            attribs.append( (self.tr("Strength"  ), new_small_le(self)) )
            attribs.append( (self.tr("Perception"), new_small_le(self)) )
            attribs[4][1].setProperty('attrib_id', ATTRIBS.STRENGTH)
            attribs[5][1].setProperty('attrib_id', ATTRIBS.PERCEPTION)
            # Fire ring
            attribs.append( (self.tr("Agility"     ), new_small_le(self)) )
            attribs.append( (self.tr("Intelligence"), new_small_le(self)) )
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
            grid.addWidget( QtGui.QLabel(self.tr("<b>Void Points</b>")), 
                            4, 2, 1, 3,
                            QtCore.Qt.AlignHCenter )

            self.void_points = widgets.CkNumWidget(count=10, parent=self)
            grid.addWidget( self.void_points, 5, 2, 1, 3,
                            QtCore.Qt.AlignHCenter)

            hbox.addWidget(grp)

            mgrid.addWidget(fr, row, col)

        def add_pc_flags(row, col):
            tx_flags = [self.tr("Honor" ), self.tr("Glory"           ), 
                        self.tr("Status"), self.tr("Shadowland Taint")]
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
                lay.addWidget(QtGui.QLabel('<b>%s</b>' % f), row, 0)
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
            
            monos_ = QtGui.QFont('Monospace')
            monos_.setStyleHint( QtGui.QFont.Courier )
            
            # fr.setFont(monos_)
            
            # initiative
            grp  = QtGui.QGroupBox(self.tr("Initiative"), self)
            grd  = QtGui.QFormLayout(grp)

            self.tx_base_init = QtGui.QLineEdit(self)
            self.tx_mod_init  = QtGui.QLineEdit(self)
            self.tx_cur_init  = QtGui.QLineEdit(self)

            self.tx_base_init.setReadOnly(True)
            self.tx_cur_init .setReadOnly(True)

            grd.addRow( self.tr("Base"    ), self.tx_base_init)
            grd.addRow( self.tr("Modifier"), self.tx_mod_init)
            grd.addRow( self.tr("Current" ), self.tx_cur_init)

            hbox.addWidget(grp, 1)

            # Armor TN
            grp = QtGui.QGroupBox(self.tr("Armor TN"), self)
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

            grd.addRow( self.tr("Name"     ), self.tx_armor_nm)
            grd.addRow( self.tr("Base"     ), self.tx_base_tn)
            grd.addRow( self.tr("Armor"    ), self.tx_armor_tn)
            grd.addRow( self.tr("Reduction"), self.tx_armor_rd)
            grd.addRow( self.tr("Current"  ), self.tx_cur_tn)

            hbox.addWidget(grp, 1)

            # Wounds
            grp = QtGui.QGroupBox(self.tr("Wounds"), self)
            grd  = QtGui.QGridLayout(grp)

            wnd = []
            wnd.append( (QtGui.QLabel(self), new_small_le(self), new_small_le(self)) )
            wnd.append( (QtGui.QLabel(self), new_small_le(self), new_small_le(self)) )
            wnd.append( (QtGui.QLabel(self), new_small_le(self), new_small_le(self)) )
            wnd.append( (QtGui.QLabel(self), new_small_le(self), new_small_le(self)) )
            wnd.append( (QtGui.QLabel(self), new_small_le(self), new_small_le(self)) )
            wnd.append( (QtGui.QLabel(self), new_small_le(self), new_small_le(self)) )
            wnd.append( (QtGui.QLabel(self), new_small_le(self), new_small_le(self)) )
            wnd.append( (QtGui.QLabel(self.tr("Out"), self), 
                         new_small_le(self), new_small_le(self)) )
            
            self.wounds = wnd
            self.wnd_lb = grp

            row_ = 0
            col_ = 0
            for i in xrange(0, len(wnd)):
                if i == 4:
                    col_ = 3
                    row_ = 0

                grd.addWidget( wnd[i][0], row_, col_ )
                grd.addWidget( wnd[i][0], row_, col_ )
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
                if d is not None and len(d) == 2:
                    col_ = d[0]
                    obj_ = d[1]
                    view.setItemDelegateForColumn(col_, obj_)
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
       
    def _build_spell_frame(self, model, layout = None):
        grp    = QtGui.QGroupBox(self.tr("Spells"), self)
        hbox   = QtGui.QHBoxLayout(grp)        
        
        fr_    = QtGui.QFrame(self)
        vbox   = QtGui.QVBoxLayout(fr_)
        vbox.setContentsMargins(3,3,3,3)
        
        # advantages/disadvantage vertical toolbar
        def _make_vertical_tb():
            vtb = widgets.VerticalToolBar(self)
            vtb.addStretch()
            
            cb_buy    = self.act_buy_spell
            cb_remove = self.act_del_spell
            cb_memo   = self.act_memo_spell
            
            self.add_spell_bt = vtb.addButton(
                                QtGui.QIcon(get_icon_path('buy',(16,16))), 
                                self.tr("Add new spell"), cb_buy)

            self.del_spell_bt = vtb.addButton(
                                QtGui.QIcon(get_icon_path('minus',(16,16))), 
                                self.tr("Remove spell"), cb_remove)
            
            self.memo_spell_bt = vtb.addButton(
                                 QtGui.QIcon(get_icon_path('book',(16,16))), 
                                 self.tr("Memorize/Forget spell"), cb_memo)
                                 
            
            # TODO: enable these buttons eventually
            self.add_spell_bt.setEnabled(False)
            self.del_spell_bt.setEnabled(False)
            
            vtb.addStretch()
            return vtb         
        
        # View
        view  = QtGui.QTableView(self)
        view.setSizePolicy( QtGui.QSizePolicy.Expanding,
                              QtGui.QSizePolicy.Expanding )         
        view.setSortingEnabled(True)
        view.horizontalHeader().setResizeMode(QtGui.QHeaderView.Interactive);
        view.horizontalHeader().setStretchLastSection(True)
        view.horizontalHeader().setCascadingSectionResizes(True)
        view.setModel(model)
        view.selectionModel().currentRowChanged.connect(self.on_spell_selected)
        self.spell_table_view = view
        
        # Affinity/Deficiency
        self.lb_affin = QtGui.QLabel(self.tr("None"), self)
        self.lb_defic = QtGui.QLabel(self.tr("None"), self)
        
        aff_fr = QtGui.QFrame(self)
        aff_fr.setSizePolicy( QtGui.QSizePolicy.Preferred,
                              QtGui.QSizePolicy.Maximum )        
        fl     = QtGui.QFormLayout(aff_fr)
        fl.addRow(self.tr("<b><i>Affinity</i></b>"  ), self.lb_affin)
        fl.addRow(self.tr("<b><i>Deficiency</i></b>"), self.lb_defic)
        fl.setHorizontalSpacing(60)
        fl.setVerticalSpacing  ( 5)
        fl.setContentsMargins(0, 0, 0, 0)
        
        
        vbox.addWidget(aff_fr)
        vbox.addWidget(view)
        
        hbox.addWidget(_make_vertical_tb())
        hbox.addWidget(fr_)
        
        if layout: layout.addWidget(grp)            
        
        return view
        
    def _build_tech_frame(self, model, layout = None):
        grp    = QtGui.QGroupBox(self.tr("Techs"), self)
        vbox   = QtGui.QVBoxLayout(grp)       
        
        # View
        view  = QtGui.QListView(self)
        view.setModel(model)
        view.setItemDelegate(models.TechItemDelegate(self))
        vbox.addWidget(view)
        
        if layout: layout.addWidget(grp) 
        
        return view

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
                      self.tr("Add skill rank"), self.on_buy_skill_rank)
        vtb.addButton(QtGui.QIcon(get_icon_path('buy',(16,16))),
                      self.tr("Buy skill emphasys"), self.show_buy_emph_dlg)                      
        vtb.addButton(QtGui.QIcon(get_icon_path('buy',(16,16))),
                      self.tr("Buy another skill"), self.show_buy_skill_dlg)
        vtb.addStretch()

        models_ = [ ("Skills", 'table', sk_sort_model, None, vtb),
                    (self.tr("Mastery Abilities"),  'list', self.ma_view_model,
                    models.MaItemDelegate(self), None) ]

        frame_, views_ = self._build_generic_page(models_)

        if len(views_) > 0:
            self.skill_table_view = views_[0]

        self.tabs.addTab(frame_, self.tr("Skills"))

    def build_ui_page_3(self):
        self.sp_view_model = models.SpellTableViewModel(self.db_conn, self)
        self.th_view_model = models.TechViewModel      (self.db_conn, self)

        # enable sorting through a proxy model
        sp_sort_model = models.ColorFriendlySortProxyModel(self)
        sp_sort_model.setDynamicSortFilter(True)
        sp_sort_model.setSourceModel(self.sp_view_model)
        
        frame_ = QtGui.QFrame(self)
        vbox   = QtGui.QVBoxLayout(frame_)
        #views_ = []
        
        self._build_spell_frame(sp_sort_model     , vbox)
        self._build_tech_frame (self.th_view_model, vbox)
        
        self.tabs.addTab(frame_, self.tr("Techniques"))

    def build_ui_page_4(self):
        mfr    = QtGui.QFrame(self)
        vbox   = QtGui.QVBoxLayout(mfr)

        # advantages/disadvantage vertical toolbar
        def _make_vertical_tb(tag, has_edit, has_remove):
            vtb = widgets.VerticalToolBar(self)
            vtb.addStretch()
            
            cb_buy  = (self.sink2.act_buy_merit if tag == 'merit'
                                        else self.sink2.act_buy_flaw)
            cb_edit = (self.sink2.act_edit_merit if tag == 'merit'
                                        else self.sink2.act_edit_flaw)
            cb_remove = (self.sink2.act_del_merit if tag == 'merit'
                                        else self.sink2.act_del_flaw)
            
            vtb.addButton(QtGui.QIcon(get_icon_path('buy',(16,16))), 
                         self.tr("Add Perk"), cb_buy)
                
            if has_edit:                
                vtb.addButton(QtGui.QIcon(get_icon_path('edit',(16,16))), 
                              self.tr("Edit Perk"), cb_edit)
            
            if has_remove:
                vtb.addButton(QtGui.QIcon(get_icon_path('minus',(16,16))), 
                              self.tr("Remove Perk"), cb_remove)
            
            vtb.addStretch()
            return vtb 

        self.merits_view_model = models.PerkViewModel(self.db_conn, 'merit')
        self.flaws_view_model  = models.PerkViewModel(self.db_conn, 'flaws')

        merit_view = QtGui.QListView(self)
        merit_view.setModel(self.merits_view_model)
        merit_view.setItemDelegate(models.PerkItemDelegate(self))
        merit_vtb  = _make_vertical_tb('merit', True, True)
        fr_        = QtGui.QFrame(self)
        hb_        = QtGui.QHBoxLayout(fr_)
        hb_.setContentsMargins(3,3,3,3)
        hb_.addWidget(merit_vtb)
        hb_.addWidget(merit_view)
        vbox.addWidget(new_item_groupbox(self.tr("Advantages"), fr_))

        flaw_view = QtGui.QListView(self)
        flaw_view.setModel(self.flaws_view_model)
        flaw_view.setItemDelegate(models.PerkItemDelegate(self))
        flaw_vtb  = _make_vertical_tb('flaw', True, True)
        fr_        = QtGui.QFrame(self)
        hb_        = QtGui.QHBoxLayout(fr_)
        hb_.setContentsMargins(3,3,3,3)
        hb_.addWidget(flaw_vtb)
        hb_.addWidget(flaw_view)        
        vbox.addWidget(new_item_groupbox(self.tr("Disadvantages"), fr_))
        
        self.merit_view = merit_view
        self.flaw_view  = flaw_view

        self.tabs.addTab(mfr, self.tr("Perks"))

    def build_ui_page_5(self):
        mfr    = QtGui.QFrame(self)
        vbox   = QtGui.QVBoxLayout(mfr)

        fr_    = QtGui.QFrame(self)
        fr_h   = QtGui.QHBoxLayout(fr_)
        fr_h.setContentsMargins(0, 0, 0, 0)
        fr_h.addWidget(QtGui.QLabel(self.tr("""<p><i>Click the button to refund
                                             the last advancement</i></p>"""), self))
        bt_refund_adv = QtGui.QPushButton(self.tr("Refund"), self)
        bt_refund_adv.setSizePolicy( QtGui.QSizePolicy.Maximum,
                                     QtGui.QSizePolicy.Preferred )
        bt_refund_adv.clicked.connect(self.sink1.refund_advancement)
        fr_h.addWidget(bt_refund_adv)
        vbox.addWidget(fr_)

        self.adv_view_model = models.AdvancementViewModel(self)
        lview = QtGui.QListView(self)
        lview.setModel(self.adv_view_model)
        lview.setItemDelegate(models.AdvancementItemDelegate(self))
        vbox.addWidget(lview)

        self.adv_view = lview

        self.tabs.addTab(mfr, self.tr("Advancements"))

    def build_ui_page_6(self):
        self.melee_view_model  = models.WeaponTableViewModel('melee' , self)
        self.ranged_view_model = models.WeaponTableViewModel('ranged', self)
        self.arrow_view_model  = models.WeaponTableViewModel('arrow' , self)
        
        def _make_sortable(model):
            # enable sorting through a proxy model
            sort_model_ = models.ColorFriendlySortProxyModel(self)
            sort_model_.setDynamicSortFilter(True)
            sort_model_.setSourceModel(model)
            return sort_model_
        
        # weapon vertical toolbar
        def _make_vertical_tb(has_custom, has_edit, has_qty, filter):
            vtb = widgets.VerticalToolBar(self)
            vtb.setProperty('filter', filter)
            vtb.addStretch()
            vtb.addButton(QtGui.QIcon(get_icon_path('buy',(16,16))), 
                          self.tr("Add weapon"), self.sink3.show_add_weapon)
            if has_custom:
                vtb.addButton(QtGui.QIcon(get_icon_path('custom',(16,16))), 
                              self.tr("Add custom weapon"), self.sink3.show_add_cust_weapon)
            if has_edit:
                vtb.addButton(QtGui.QIcon(get_icon_path('edit',(16,16))), 
                              self.tr("Edit weapon"), self.sink3.edit_selected_weapon)
            vtb.addButton(QtGui.QIcon(get_icon_path('minus',(16,16))), 
                          self.tr("Remove weapon"), self.sink3.remove_selected_weapon)                      
            if has_qty:
                vtb.addButton(QtGui.QIcon(get_icon_path('add',(16,16))), 
                              self.tr("Increase Quantity"), self.sink3.on_increase_item_qty)
                vtb.addButton(QtGui.QIcon(get_icon_path('minus',(16,16))), 
                              self.tr("Decrease Quantity"), self.sink3.on_decrease_item_qty)                              
            
            vtb.addStretch()
            return vtb            
        
        melee_vtb  = _make_vertical_tb(True, True, False, 'melee' )
        ranged_vtb = _make_vertical_tb(True, True, False, 'ranged')
        arrow_vtb  = _make_vertical_tb(False, False, True,'arrow' )
        
        models_ = [ (self.tr("Melee Weapons"), 'table', _make_sortable(self.melee_view_model), 
                    None, melee_vtb),
                    (self.tr("Ranged Weapons"), 'table', _make_sortable(self.ranged_view_model), 
                    None, ranged_vtb),
                    (self.tr("Arrows"), 'table', _make_sortable(self.arrow_view_model), 
                    None, arrow_vtb)]

        frame_, views_ = self._build_generic_page(models_)
        
        melee_vtb .setProperty('source', views_[0])
        ranged_vtb.setProperty('source', views_[1])
        arrow_vtb .setProperty('source', views_[2])
        
        self.tabs.addTab(frame_, self.tr("Weapons"))
    
    def build_ui_page_7(self):
        # modifiers
        self.mods_view_model  = models.ModifiersTableViewModel(self)
        self.mods_view_model.user_change.connect(self.update_from_model)
        
        def _make_sortable(model):
            # enable sorting through a proxy model
            sort_model_ = models.ColorFriendlySortProxyModel(self)
            sort_model_.setDynamicSortFilter(True)
            sort_model_.setSourceModel(model)
            return sort_model_
        
        # weapon vertical toolbar
        def _make_vertical_tb():
            vtb = widgets.VerticalToolBar(self)            
            vtb.addStretch()
            vtb.addButton(QtGui.QIcon(get_icon_path('buy',(16,16))), 
                          self.tr("Add modifier"), self.sink4.add_new_modifier)
            vtb.addButton(QtGui.QIcon(get_icon_path('minus',(16,16))), 
                          self.tr("Remove modifier"), self.sink4.remove_selected_modifier)
            
            vtb.addStretch()
            return vtb            
        
        vtb  = _make_vertical_tb()
        
        models_ = [ (self.tr("Modifiers"), 'table', _make_sortable(self.mods_view_model), 
                    None, vtb) ]

        frame_, views_ = self._build_generic_page(models_)
        self.mod_view = views_[0]
        
        self.mod_view.setItemDelegate(models.ModifierDelegate(self.db_conn, self))
        vtb .setProperty('source', self.mod_view)
        self.tabs.addTab(frame_, self.tr("Modifiers"))
    
    def build_ui_page_8(self):
        mfr  = QtGui.QFrame(self)
        vbox = QtGui.QVBoxLayout(mfr)
        #vbox.setAlignment(QtCore.Qt.AlignCenter)
        #vbox.setSpacing  (30)
        
        self.tx_pc_notes = widgets.SimpleRichEditor(self)
        vbox.addWidget(self.tx_pc_notes)
        
        self.tabs.addTab(mfr, self.tr("Notes"))
        
    def build_ui_page_9(self):
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
                  Paul Tar, Jr aka Geiko (Lots of cool stuff)
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

        self.tabs.addTab(mfr, self.tr("About"))

    def build_menu(self):
        # File Menu
        m_file = self.menuBar().addMenu(self.tr("&File"));
        # actions: new, open, save
        new_act         = QtGui.QAction(self.tr("&New Character"), self)
        open_act        = QtGui.QAction(self.tr("&Open Character..."), self)
        save_act        = QtGui.QAction(self.tr("&Save Character..."), self)
        export_pdf_act  = QtGui.QAction(self.tr("Ex&port as PDF..."), self)
        exit_act        = QtGui.QAction(self.tr("E&xit"), self)

        new_act .setShortcut( QtGui.QKeySequence.New  )
        open_act.setShortcut( QtGui.QKeySequence.Open )
        save_act.setShortcut( QtGui.QKeySequence.Save )
        exit_act.setShortcut( QtGui.QKeySequence.Quit )

        m_file.addAction(new_act)
        m_file.addAction(open_act)
        m_file.addAction(save_act)
        m_file.addSeparator()
        #m_file.addAction(export_text_act)
        m_file.addAction(export_pdf_act )
        m_file.addSeparator()
        m_file.addAction(exit_act)

        new_act .triggered.connect( self.sink1.new_character  )
        open_act.triggered.connect( self.sink1.load_character )
        save_act.triggered.connect( self.sink1.save_character )
        exit_act.triggered.connect( self.close )

        #export_text_act.triggered.connect( self.export_character_as_text )
        export_pdf_act .triggered.connect( self.sink1.export_character_as_pdf  )

        self.m_file = m_file

        # Advancement menu
        m_adv = self.menuBar().addMenu(self.tr("A&dvancement"))
        # submenut
        m_buy_adv = m_adv.addMenu(self.tr("&Buy"))

        # actions buy advancement, view advancements
        viewadv_act  = QtGui.QAction(self.tr("&View advancements..."  ), self)
        resetadv_act = QtGui.QAction(self.tr("&Reset advancements"    ), self)
        refund_act   = QtGui.QAction(self.tr("Refund last advancement"), self)
        buyattr_act  = QtGui.QAction(self.tr("Attribute rank..."      ), self)
        buyvoid_act  = QtGui.QAction(self.tr("Void ring..."           ), self)
        buyskill_act = QtGui.QAction(self.tr("Skill rank..."          ), self)
        buyemph_act  = QtGui.QAction(self.tr("Skill emphasis..."      ), self)
        buymerit_act = QtGui.QAction(self.tr("Advantage..."           ), self)
        buyflaw_act  = QtGui.QAction(self.tr("Disadvantage..."        ), self)
        buykata_act  = QtGui.QAction(self.tr("Kata..."                ), self)
        # buykiho_act  = QtGui.QAction(u'Kiho..."), self)

        refund_act .setShortcut( QtGui.QKeySequence.Undo  )

        buyattr_act .setProperty('tag', 'attrib')
        buyvoid_act .setProperty('tag', 'void'  )
        buyskill_act.setProperty('tag', 'skill' )
        buyemph_act .setProperty('tag', 'emph'  )
        buymerit_act.setProperty('tag', 'merit' )
        buyflaw_act .setProperty('tag', 'flaw'  )
        buykata_act .setProperty('tag', 'kata'  )
        # buykiho_act .setProperty('tag', 'kiho'  )

        m_buy_adv.addAction(buyattr_act )
        m_buy_adv.addAction(buyvoid_act )
        m_buy_adv.addAction(buyskill_act)
        m_buy_adv.addAction(buyemph_act )
        m_buy_adv.addAction(buymerit_act)
        m_buy_adv.addAction(buyflaw_act )
        m_buy_adv.addAction(buykata_act )

        m_adv    .addSeparator()
        m_adv    .addAction(viewadv_act )
        m_adv.addAction(refund_act)
        m_adv.addAction(resetadv_act)

        self.m_adv = m_adv
        self.m_buy = m_buy_adv

        viewadv_act .triggered.connect( self.sink1.switch_to_page_5    )
        resetadv_act.triggered.connect( self.sink1.reset_adv           )
        refund_act  .triggered.connect( self.sink1.refund_last_adv     )
        buyattr_act .triggered.connect( self.sink1.act_buy_advancement )
        buyvoid_act .triggered.connect( self.sink1.act_buy_advancement )
        buyskill_act.triggered.connect( self.sink1.act_buy_advancement )
        buyemph_act .triggered.connect( self.sink1.act_buy_advancement )
        buykata_act .triggered.connect( self.sink1.act_buy_advancement )
        # buykiho_act .triggered.connect( self.act_buy_advancement )

        buymerit_act.triggered.connect( self.sink1.act_buy_perk )
        buyflaw_act .triggered.connect( self.sink1.act_buy_perk )

        # Tools menu
        m_tools = self.menuBar().addMenu(self.tr("&Tools"))

        # Name generator submenu
        m_namegen = m_tools.addMenu(self.tr("&Generate Name"))

        # actions generate female, male names
        gen_male_act   = QtGui.QAction(self.tr("Male"), self)
        gen_female_act = QtGui.QAction(self.tr("Female"), self)

        # gender tag
        gen_male_act.setProperty  ('gender', 'male')
        gen_female_act.setProperty('gender', 'female')

        m_namegen.addAction(gen_male_act)
        m_namegen.addAction(gen_female_act)

        self.m_namegen = m_namegen

        gen_male_act  .triggered.connect( self.sink1.generate_name )
        gen_female_act.triggered.connect( self.sink1.generate_name )
        
        # Dice roller menu
        dice_roll_act = QtGui.QAction(self.tr("Dice &Roller..."), self)
        dice_roll_act  .triggered.connect( self.sink1.show_dice_roller )
        
        m_tools.addAction(dice_roll_act)

        # Outfit menu
        m_outfit = self.menuBar().addMenu(self.tr("Out&fit"))

        # actions, select armor, add weapon, add misc item
        sel_armor_act      = QtGui.QAction(self.tr("Wear Armor..."       ), self)
        sel_cust_armor_act = QtGui.QAction(self.tr("Wear Custom Armor..."), self)
        add_weap_act       = QtGui.QAction(self.tr("Add Weapon..."       ), self)
        add_cust_weap_act  = QtGui.QAction(self.tr("Add Custom Weapon..."), self)
        # add_misc_item_act  = QtGui.QAction(self.tr("Add Misc Item...")    , self)

        #add_weap_act     .setEnabled(False)
        #add_cust_weap_act.setEnabled(False)
        # add_misc_item_act.setEnabled(False)

        m_outfit.addAction(sel_armor_act     )
        m_outfit.addAction(sel_cust_armor_act)
        m_outfit.addAction(add_weap_act      )
        m_outfit.addAction(add_cust_weap_act )
        # m_outfit.addAction(add_misc_item_act )

        sel_armor_act     .triggered.connect( self.sink1.show_wear_armor      )
        sel_cust_armor_act.triggered.connect( self.sink1.show_wear_cust_armor )
        add_weap_act      .triggered.connect( self.sink3.show_add_weapon      )
        add_cust_weap_act .triggered.connect( self.sink3.show_add_cust_weapon )
        # add_misc_item_act .triggered.connect( self.sink1.show_add_misc_item   )

        # Rules menu
        m_rules = self.menuBar().addMenu(self.tr("&Rules"))

        # rules actions
        set_exp_limit_act  = QtGui.QAction(self.tr("Set Experience Limit..." ), self)
        set_wound_mult_act = QtGui.QAction(self.tr("Set Health Multiplier..."), self)
        unlock_school_act  = QtGui.QAction(self.tr("Lock Schools"            ), self)
        unlock_advans_act  = QtGui.QAction(self.tr("Lock Advancements"       ), self)
        buy_for_free_act   = QtGui.QAction(self.tr("Free Shopping"           ), self)
        damage_act         = QtGui.QAction(self.tr("Cure/Inflict Damage...")  , self)
        
        # insight calculation submenu
        m_insight_calc   = m_rules.addMenu(self.tr("Insight Calculation"))
        self.ic_act_grp  = QtGui.QActionGroup(self)
        ic_default_act   = QtGui.QAction(self.tr("Default"                     ), self)
        ic_no_rank1_1    = QtGui.QAction(self.tr("Ignore Rank 1 Skills"        ), self)
        ic_no_rank1_2    = QtGui.QAction(self.tr("Account Rank 1 School Skills"), self)
        ic_default_act.setProperty('method', rules.insight_calculation_1)
        ic_no_rank1_1 .setProperty('method', rules.insight_calculation_2)
        ic_no_rank1_2 .setProperty('method', rules.insight_calculation_3)
        ic_list = [ic_default_act, ic_no_rank1_1, ic_no_rank1_2]
        for act in ic_list:
            self.ic_act_grp.addAction(act)
            act.setCheckable(True)
            m_insight_calc.addAction (act)
        ic_list[self.ic_idx].setChecked(True)   

        unlock_school_act.setCheckable(True)
        unlock_advans_act.setCheckable(True)
        buy_for_free_act .setCheckable(True)

        unlock_school_act.setChecked(True)
        unlock_advans_act.setChecked(True)
        buy_for_free_act .setChecked(False)

        self.unlock_schools_menu_item = unlock_school_act
        self.unlock_advans_menu_item  = unlock_advans_act

        m_rules.addAction(set_exp_limit_act )
        m_rules.addAction(set_wound_mult_act)
        m_rules.addAction(unlock_school_act )
        m_rules.addAction(unlock_advans_act )
        m_rules.addAction(buy_for_free_act  )
        m_rules.addSeparator()
        m_rules.addAction(damage_act)

        set_exp_limit_act .triggered.connect( self.sink1.on_set_exp_limit       )
        set_wound_mult_act.triggered.connect( self.sink1.on_set_wnd_mult        )
        damage_act        .triggered.connect( self.sink1.on_damage_act          )
        unlock_school_act .triggered.connect( self.sink1.on_unlock_school_act   )
        unlock_advans_act .toggled  .connect( self.sink1.on_toggle_advans_act   )
        buy_for_free_act .toggled   .connect( self.sink1.on_toggle_buy_for_free )

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
                                      
        self.ic_act_grp.triggered.connect(self.on_change_insight_calculation)
        
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
     
    def on_trait_increase(self, text):
        '''raised when user click on the small '+' button near traits'''
        
        if ( self.increase_trait( models.attrib_from_name(text) ) ==
             CMErrors.NOT_ENOUGH_XP ):
             self.not_enough_xp_advise(self)       

    def on_void_increase(self):
        '''raised when user click on the small '+' button near void ring'''
        if ( self.increase_void() == CMErrors.NOT_ENOUGH_XP ):
             self.not_enough_xp_advise(self)        

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
        if uuid == self.pc.get_family():
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
        try:
            name, perk, perkval, honor, tag = c.fetchone()
        except:
            # no school
            self.pc.set_school(uuid, None, None, None)
            return
        
        school_tags = [ x.strip() for x in tag.split(';') ]
        clan_tag = str.format('{0} {1}', self.cb_pc_clan.currentText(),
                                         school_tags[0])
        school_tags.append(clan_tag.lower())
        school_tags.append(name.lower())
        
        self.pc.set_school( uuid, perk, perkval, honor, school_tags)

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

        if 'shugenja' in tag:
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
            
            # affinity / deficiency
            c.execute('''select affinity, deficiency from schools
                         where uuid=?''', [uuid])
            
            for affin, defic in c.fetchall():
                self.pc.set_affinity(affin)
                self.pc.set_deficiency(defic)
                self.pc.get_school().affinity = affin
                self.pc.get_school().deficiency = defic

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
       
    def on_buy_skill_rank(self):
        # get selected skill
        sm_ = self.skill_table_view.selectionModel()
        if sm_.hasSelection():
            model_   = self.skill_table_view.model()
            skill_id = model_.data(sm_.currentIndex(), QtCore.Qt.UserRole)
            
            err_ = self.buy_next_skill_rank(skill_id)
            if err_ != CMErrors.NO_ERROR:
                if err_ == CMErrors.NOT_ENOUGH_XP:
                    self.not_enough_xp_advise(self)
                return               
                
            idx = None
            for i in xrange(0, self.skill_table_view.model().rowCount()):
                idx = self.skill_table_view.model().index(i, 0)
                if model_.data(idx, QtCore.Qt.UserRole) == skill_id:
                    break
            if idx.isValid():
                sm_.setCurrentIndex(idx, (QtGui.QItemSelectionModel.Select |
                                         QtGui.QItemSelectionModel.Rows))

    def act_choose_skills(self):
        dlg = dialogs.SelWcSkills(self.pc, self.db_conn, self)
        if dlg.exec_() == QtGui.QDialog.DialogCode.Accepted:
            self.pc.clear_pending_wc_skills()
            self.pc.clear_pending_wc_emphs ()
            self.update_from_model()
            
    def act_memo_spell(self):
        # get selected spell
        sm_ = self.spell_table_view.selectionModel()
        if sm_.hasSelection():
            model_    = self.spell_table_view.model()
            spell_itm = model_.data(sm_.currentIndex(), QtCore.Qt.UserRole)
            
            err_ = CMErrors.NO_ERROR
            if spell_itm.memo:
                self.remove_advancement_item(spell_itm.adv)
            else:
                err_ = self.memo_spell(spell_itm.spell_id)
                
            if err_ != CMErrors.NO_ERROR:
                if err_ == CMErrors.NOT_ENOUGH_XP:
                    self.not_enough_xp_advise(self)
                return               
                
            idx = None
            for i in xrange(0, self.spell_table_view.model().rowCount()):
                idx = self.spell_table_view.model().index(i, 0)
                if (model_.data(idx, QtCore.Qt.UserRole).spell_id == 
                    spell_itm.spell_id):
                    break
            if idx.isValid():
                sm_.setCurrentIndex(idx, (QtGui.QItemSelectionModel.Select |
                                         QtGui.QItemSelectionModel.Rows))
    
    def act_buy_spell(self):
        pass
        
    def act_del_spell(self):
        # get selected spell
        sm_ = self.spell_table_view.selectionModel()
        if sm_.hasSelection():
            model_    = self.spell_table_view.model()
            spell_itm = model_.data(sm_.currentIndex(), QtCore.Qt.UserRole)            
            err_ = CMErrors.NO_ERROR            
            if spell_itm.memo: return
            self.remove_spell(spell_itm.spell_id)

    def on_spell_selected(self, current, previous):
        # get selected spell
        model_    = self.spell_table_view.model()
        spell_itm = model_.data(current, QtCore.Qt.UserRole)
            
        # toggle remove
        self.del_spell_bt.setEnabled(not spell_itm.memo)
        
                                         
    def learn_next_school_tech(self):
        # for now do not support multiple school advantage
        # learn next technique for your school

        next_rank = self.pc.get_school_rank() + 1

        c = self.db_conn.cursor()
        c.execute('''select uuid, name, effect from school_techs
                     where school_uuid=? and rank=?''', [self.pc.get_school_id(), next_rank])
        for uuid, name, rule in c.fetchall():
            self.pc.add_tech(int(uuid), rule)

        c.close()
        
        self.pc.recalc_ranks()        
        self.sink1.switch_to_page_3()
        self.update_from_model()
        
    def check_rank_advancement(self):
        if self.nicebar: return
        
        if self.pc.get_insight_rank() > self.last_rank:
            # HEY, NEW RANK DUDE!
            lb = QtGui.QLabel(self.tr("You reached the next rank, you have an opportunity"
                                      " to decide your destiny."), self)
            bt = QtGui.QPushButton(self.tr("Advance rank"), self)
            bt.setSizePolicy( QtGui.QSizePolicy.Maximum,
                              QtGui.QSizePolicy.Preferred)
            bt.clicked.connect( self.show_advance_rank_dlg )
            self.show_nicebar([lb, bt])
            
            # debug
            # dump_slots(self, 'after_a_while.txt')
            
    def check_school_tech_and_spells(self):
        if self.nicebar: return
        
        # Show nicebar if can get another school tech
        if (self.pc.can_get_other_techs() and 
            self.check_if_tech_available() and
            self.check_tech_school_requirements()):
            self.learn_next_school_tech()
        elif self.pc.can_get_other_spells():
            lb = QtGui.QLabel(self.tr("You now fit the requirements to learn other Spells"), self)
            bt = QtGui.QPushButton(self.tr("Learn Spells"), self)
            bt.setSizePolicy( QtGui.QSizePolicy.Maximum,
                              QtGui.QSizePolicy.Preferred)
            bt.clicked.connect( self.learn_next_school_spells )
            self.show_nicebar([lb, bt])

    def check_missing_requirements(self):
        if self.nicebar: return
        
        if not self.check_tech_school_requirements():
            lb = QtGui.QLabel(self.tr("You need at least one rank in all school skills"
                                      " to learn the next School Technique"), self)
            bt = QtGui.QPushButton(self.tr("Buy Requirements"), self)
            bt.setSizePolicy( QtGui.QSizePolicy.Maximum,
                              QtGui.QSizePolicy.Preferred)
            bt.clicked.connect( self.buy_school_requirements )
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
                    #print 'found character rule %s' % rule
                    adv.rule = rule
                    break
        c.close()

    def check_affinity_wc(self):
        if self.nicebar: return
        
        if (self.pc.get_affinity() and
            self.pc.get_affinity().startswith('*')):
            lb = QtGui.QLabel(self.tr("You school grant you to choose an elemental affinity."), self)
            bt = QtGui.QPushButton(self.tr("Choose Affinity"), self)
            bt.setSizePolicy( QtGui.QSizePolicy.Maximum,
                              QtGui.QSizePolicy.Preferred)
            bt.clicked.connect( self.show_select_affinity )
            self.show_nicebar([lb, bt])
        elif (self.pc.get_deficiency() and 
              self.pc.get_deficiency().startswith('*')):
            lb = QtGui.QLabel(self.tr("You school grant you to choose an elemental deficiency."), self)
            bt = QtGui.QPushButton(self.tr("Choose Deficiency"), self)
            bt.setSizePolicy( QtGui.QSizePolicy.Maximum,
                              QtGui.QSizePolicy.Preferred)
            bt.clicked.connect( self.show_select_deficiency )
            self.show_nicebar([lb, bt])
            
    def learn_next_school_spells(self):
        self.pc.recalc_ranks()
        
        dlg = dialogs.SelWcSpells(self.pc, self.db_conn, self)
        if dlg.exec_() == QtGui.QDialog.DialogCode.Accepted:
            self.pc.clear_pending_wc_spells()
            self.update_from_model()
            
    def show_advance_rank_dlg(self):
        dlg = dialogs.NextRankDlg(self.pc, self.db_conn, self)
        if dlg.exec_() == QtGui.QDialog.DialogCode.Accepted:
            self.last_rank = self.pc.get_insight_rank()
            self.update_from_model()
            
    def show_buy_skill_dlg(self):       
        dlg = dialogs.BuyAdvDialog(self.pc, 'skill',
                                   self.db_conn, self)
        dlg.exec_()
        self.update_from_model()   

    def show_buy_emph_dlg(self):
        # get selected skill
        sm_ = self.skill_table_view.selectionModel()
        if sm_.hasSelection():
            model_   = self.skill_table_view.model()
            skill_id = model_.data(sm_.currentIndex(), QtCore.Qt.UserRole)
            
            dlg = dialogs.BuyAdvDialog(self.pc, 'emph',
                                       self.db_conn, self)
            dlg.fix_skill_id(skill_id)
            dlg.exec_()
            self.update_from_model()             
                
    def show_select_affinity(self):
        chooses  = None
        if self.pc.get_affinity() == '*nonvoid':
            chooses = [ models.ring_name_from_id(x).capitalize() for x in xrange(0,4) ]
        else:
            chooses = [ models.ring_name_from_id(x).capitalize() for x in xrange(0,5) ]
        
        affinity, is_ok = QtGui.QInputDialog.getItem(self,
                                              "L5R: CM",
                                              self.tr("Select your elemental affinity"),
                                              chooses, 0, False)
        # print affinity, is_ok
        if is_ok:
            self.set_pc_affinity(affinity)
            
    def show_select_deficiency(self):
        chooses  = None
        if self.pc.get_deficiency() == '*nonvoid':
            chooses = [ models.ring_name_from_id(x).capitalize() for x in xrange(0,4) ]
        else:
            chooses = [ models.ring_name_from_id(x).capitalize() for x in xrange(0,5) ]
        
        deficiency, is_ok = QtGui.QInputDialog.getItem(self,
                                              "L5R: CM",
                                              self.tr("Select your elemental deficiency"),
                                              chooses, 0, False)
                                              
        if is_ok:
            self.set_pc_deficiency(deficiency)
                
    def load_character_from(self, path):
        pause_signals( [self.tx_pc_name, self.cb_pc_clan, self.cb_pc_family,
                        self.cb_pc_school] )

        self.save_path = path
        if self.pc.load_from(self.save_path):            
            try:
                self.last_rank = self.pc.last_rank
            except:
                self.last_rank = self.pc.get_insight_rank()
            
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
                self.sink1.save_character()
                # ADVISE USER
                self.advise_conversion(backup_path)

            self.load_families(self.pc.clan)
            if self.pc.unlock_schools:
                self.load_schools ()
            else:
                self.load_schools (self.pc.clan)

            self.tx_pc_notes.set_content(self.pc.extra_notes)
            self.pc.set_insight_calc_method(self.ic_calc_method)
            self.check_rules()
            self.update_from_model()

        resume_signals( [self.tx_pc_name, self.cb_pc_clan, self.cb_pc_family,
                        self.cb_pc_school] )

    def load_clans(self):
        c = self.db_conn.cursor()
        # clans
        self.cb_pc_clan.clear()
        self.cb_pc_clan.addItem( self.tr("No Clan"), 0 )
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
                         where NOT EXISTS (select ref_uuid from requirements
                                           where ref_uuid=uuid)
                         order by name asc''')
        else:
            c.execute('''select uuid, name from schools where clan_id=?
                         AND NOT EXISTS (select ref_uuid from requirements
                                         where ref_uuid=uuid)            
                         order by name asc''',
                         [clan_id])

        self.cb_pc_school.addItem( self.tr("No School"), 0 )
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

        self.cb_pc_family.addItem( self.tr("No Family"), 0 )
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

        if s_uuid == school_id:
            return
            
        #print 'set school to %s, current school is %s' % (school_id, s_uuid)
        
        found = False
        self.cb_pc_school.blockSignals(True)
        for i in xrange(0, self.cb_pc_school.count()):
            if self.cb_pc_school.itemData(i) == school_id:
                self.cb_pc_school.setCurrentIndex(i)
                found = True
                break
                
        if not found:
            self.cb_pc_school.addItem(
                 dbutil.get_school_name(self.db_conn, school_id),
                 school_id)
            #self.cb_pc_school.setCurrentIndex(self.cb_pc_school.count()-1)
        
        self.cb_pc_school.blockSignals(False)
        
    def set_void_points(self, value):
        if self.void_points.value == value:
            return
        self.void_points.set_value(value)

    def set_flag(self, flag, value):
        rank, points = rules.split_decimal(value)
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

        self.tx_pc_name.setText( self.pc.name            )
        self.set_clan          ( self.pc.clan            )
        self.set_family        ( self.pc.get_family   () )
        self.set_school        ( self.pc.get_school_id() )

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

        # armor
        self.tx_armor_nm .setText( str(self.pc.get_armor_name())  )
        self.tx_base_tn  .setText( str(self.pc.get_base_tn())     )
        self.tx_armor_tn .setText( str(self.pc.get_armor_tn())    )
        self.tx_armor_rd .setText( str(self.pc.get_full_rd())    )
        self.tx_cur_tn   .setText( str(self.pc.get_cur_tn())      )
        # armor description
        self.tx_armor_nm.setToolTip( str(self.pc.get_armor_desc()) )

        # health
        for i in xrange(0, 8):
            h = self.pc.get_health_rank(i)
            self.wounds[i][1].setText( str(h) )
            self.wounds[i][2].setText( '' )
        self.wnd_lb.setTitle(self.tr("Health / Wounds (x%d)") % self.pc.health_multiplier)
        
        self.update_wound_penalties()

        # wounds
        pc_wounds = self.pc.wounds
        hr        = 0
        while pc_wounds and hr < 8:
            w = min(pc_wounds, self.pc.get_health_rank(hr))
            self.wounds[hr][2].setText( str(w) )
            pc_wounds -= w
            hr += 1

        # initiative
        r, k = self.pc.get_base_initiative()
        self.tx_base_init.setText( rules.format_rtk(r, k) )
        rtk = self.tx_mod_init.text()
        r1, k1 = rules.parse_rtk(rtk)
        if r1 and k1:
            self.tx_cur_init.setText( rules.format_rtk(r+r1, k+k1) )
            self.pc.mod_init = (r1, k1)
        else:
            self.tx_cur_init.setText( self.tx_base_init.text() )
        
        # affinity / deficiency       
        self.lb_affin.setText(self.pc.get_affinity().capitalize())
        self.lb_defic.setText(self.pc.get_deficiency().capitalize())            

        self.hide_nicebar()

        # Show nicebar if pending wildcard skills
        wcs = self.pc.get_pending_wc_skills()
        wce = self.pc.get_pending_wc_emphs ()
        if len(wcs) > 0 or len(wce) > 0:
            lb = QtGui.QLabel(self.tr("Your school gives you the choice of certain skills"), self)
            bt = QtGui.QPushButton(self.tr("Choose Skills"), self)
            bt.setSizePolicy( QtGui.QSizePolicy.Maximum,
                              QtGui.QSizePolicy.Preferred)
            bt.clicked.connect( self.act_choose_skills )
            self.show_nicebar([lb, bt])
        #else:
        #    self.hide_nicebar()
        
        self.check_affinity_wc()
        self.check_rank_advancement()
        self.check_missing_requirements()
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
        self.melee_view_model .update_from_model(self.pc)
        self.ranged_view_model.update_from_model(self.pc)
        self.arrow_view_model .update_from_model(self.pc)
        self.mods_view_model  .update_from_model(self.pc)

    def update_wound_penalties(self):
        penalties = [0, 3, 5, 10, 15, 20, 40]        
        wounds    = [self.tr("Healthy"), self.tr("Nicked"), self.tr("Grazed"), 
                     self.tr("Hurt"), self.tr("Injured"), self.tr("Crippled"),
                     self.tr("Down")]
        if self.pc.has_rule('strength_of_earth'):
            # penalties are reduced by 3
            penalties = [ max(0,x-3) for x in penalties]
        
        for i in xrange(0, len(penalties)):            
            self.wounds[i][0].setText(
                str.format('{0} (+{1})', wounds[i], penalties[i]))
            
        # TODO toku bushi school removes some penalties
        
    def advise_conversion(self, *args):
        settings = QtCore.QSettings()
        if settings.value('advise_conversion', 'true') == 'false':
            return
        msgBox = QtGui.QMessageBox(self)
        msgBox.setWindowTitle('L5R: CM')
        msgBox.setText(self.tr("The character has been updated."))
        msgBox.setInformativeText(self.tr("This character was created with an older version of the program.\n"
                                          "I've done my best to convert and update your character, hope you don't mind :).\n"
                                          "I also created a backup of your character file in\n\n%s.") % args)
        do_not_prompt_again = QtGui.QCheckBox(self.tr("Do not prompt again"), msgBox)
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
         msgBox.setText(self.tr("The character has been modified."))
         msgBox.setInformativeText(self.tr("Do you want to save your changes?"))
         msgBox.addButton( QtGui.QMessageBox.Save )
         msgBox.addButton( QtGui.QMessageBox.Discard )
         msgBox.addButton( QtGui.QMessageBox.Cancel )
         msgBox.setDefaultButton(QtGui.QMessageBox.Save)
         return msgBox.exec_()

    def ask_to_upgrade(self, target_version):
         msgBox = QtGui.QMessageBox(self)
         msgBox.setWindowTitle('L5R: CM')
         msgBox.setText(self.tr("L5R: CM v%s is available for download.") % target_version)
         msgBox.setInformativeText(self.tr("Do you want to open the download page?"))
         msgBox.addButton( QtGui.QMessageBox.Yes )
         msgBox.addButton( QtGui.QMessageBox.No )
         msgBox.setDefaultButton(QtGui.QMessageBox.No)
         return msgBox.exec_()
         
    def not_enough_xp_advise(self, parent = None):
        if parent == None: parent = self
        QtGui.QMessageBox.warning(parent, self.tr("Not enough XP"),
        self.tr("Cannot purchase.\nYou've reached the XP Limit."))
        return
    

    def closeEvent(self, ev):
        # update interface last time, to set unsaved states
        self.update_from_model()
        
        # SAVE GEOMETRY
        settings = QtCore.QSettings()
        settings.setValue('geometry', self.saveGeometry())
        
        if self.pc.insight_calculation == rules.insight_calculation_2:
            settings.setValue('insight_calculation', 2)
        elif self.pc.insight_calculation == rules.insight_calculation_3:
            settings.setValue('insight_calculation', 3)
        else:
            settings.setValue('insight_calculation', 1)
        
        #print('is model dirty? {0}'.format(self.pc.is_dirty()))
        
        if self.pc.is_dirty():
            resp = self.ask_to_save()
            if resp == QtGui.QMessageBox.Save:
                self.sink1.save_character()
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
        fileName = QtGui.QFileDialog.getSaveFileName(
                                self, 
                                self.tr("Save Character"),
                                last_dir,
                                self.tr("L5R Character files (*.l5r)"))
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
        fileName = QtGui.QFileDialog.getOpenFileName(
                                self, 
                                self.tr("Load Character"),
                                last_dir,
                                self.tr("L5R Character files (*.l5r)"))
        if len(fileName) != 2:
            return ''
        last_dir = os.path.dirname(fileName[0])
        if last_dir != '':
            #print 'save last_dir: %s' % last_dir
            settings.setValue('last_open_dir', last_dir)
        return fileName[0]

    def select_export_file(self, file_ext = '.txt'):
        char_name = self.pc.name
        supported_ext     = ['.pdf']
        supported_filters = [self.tr("PDF Files(*.pdf)")]
        selected_filter   = supported_ext.index(file_ext)
        settings = QtCore.QSettings()
        last_dir = settings.value('last_open_dir', QtCore.QDir.homePath())
        fileName = QtGui.QFileDialog.getSaveFileName(
                                self, 
                                self.tr("Export Character"),
                                os.path.join(last_dir,char_name),
                                ";;".join(supported_filters))
        if len(fileName) != 2:
            return ''

        last_dir = os.path.dirname(fileName[0])
        if last_dir != '':
            settings.setValue('last_open_dir', last_dir)

        if fileName[0].endswith(file_ext):
            return fileName[0]
        return fileName[0] + file_ext

    def check_updates(self):
        update_info = autoupdate.get_last_version()
        if update_info is not None and \
           autoupdate.need_update(APP_VERSION, update_info['version']) and \
           self.ask_to_upgrade(update_info['version']) == QtGui.QMessageBox.Yes:

            import osutil
            osutil.portable_open(PROJECT_PAGE_LINK)

    def on_change_insight_calculation(self):
        method = self.sender().checkedAction().property('method')
        self.pc.set_insight_calc_method(method)
        self.update_from_model()
        
    def create_new_character(self):
        self.sink1.new_character()            

### MAIN ###
def dump_slots(obj, out_file):
    with open(out_file, 'wt') as fobj:
        mobj = obj.metaObject()
        for i in xrange( mobj.methodOffset(), mobj.methodCount() ):
            if mobj.method(i).methodType() == QtCore.QMetaMethod.Slot:
                fobj.write(mobj.method(i).signature() + ' ' + mobj.method(i).tag() + '\n')
def main():
    app = QtGui.QApplication(sys.argv)

    QtCore.QCoreApplication.setApplicationName(APP_NAME)
    QtCore.QCoreApplication.setApplicationVersion(APP_VERSION)
    QtCore.QCoreApplication.setOrganizationName(APP_ORG)

    app.setWindowIcon( QtGui.QIcon( get_app_icon_path() ) )
    
    # Setup translation
    settings = QtCore.QSettings()    
    use_machine_locale = settings.value('use_machine_locale', 1)
    app_translator = QtCore.QTranslator()
    qt_translator  = QtCore.QTranslator()             
    
    if use_machine_locale:        
        use_locale = QtCore.QLocale.system().name()
    else:
        use_locale = settings.value('use_locale')
        
    print('current locale is {0}'.format(use_locale))       
        
    qt_loc  = 'qt_{0}'.format(use_locale[:2])
    
    print(qt_loc)
    app_loc = get_app_file('i18n/{0}'.format(use_locale))
    
    print(QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath))
    
    qt_translator .load(qt_loc, QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath))
    app.installTranslator(qt_translator )
    app_translator.load(app_loc)    
    app.installTranslator(app_translator)
    
    # start main form

    l5rcm = L5RMain()
    l5rcm.setWindowTitle(APP_DESC + ' v' + APP_VERSION)
    l5rcm.show()

    # dump_slots(l5rcm, 'startup.txt')
    
    # check for updates
    l5rcm.check_updates()

    # initialize new character
    l5rcm.create_new_character()

    if len(sys.argv) > 1:
        #print 'load character file %s' % sys.argv[1]
        l5rcm.load_character_from(sys.argv[1])
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
