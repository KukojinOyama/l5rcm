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

from PySide import QtGui
from drcore import *
import random

class DiceRoller(QtGui.QDialog):
    def __init__(self, parent = None):
        super(DiceRoller, self).__init__(parent)
        self.build_ui()
        self.setWindowTitle('L5R: CM - Dice Roller')
        random.seed()

    def build_ui(self):
        vbox = QtGui.QVBoxLayout(self)
        
        grp_expr  = QtGui.QGroupBox("Expression ( e.g. (4k2+5)*2 )", self)
        v_        = QtGui.QVBoxLayout(grp_expr)
        le_expr   = QtGui.QLineEdit(self)       
        v_.addWidget(le_expr)
        
        grp_rules = QtGui.QGroupBox("Rules", self)
        v_        = QtGui.QVBoxLayout(grp_rules)
        rb_none   = QtGui.QRadioButton ("Explode None", self)
        rb_10     = QtGui.QRadioButton ("Explode 10", self)
        rb_9      = QtGui.QRadioButton ("Explode 9", self)
        rb_8      = QtGui.QRadioButton ("Explode 8", self)        
        for w in [rb_none, rb_10, rb_9, rb_8]:
            v_.addWidget(w)
            
        ck_1      = QtGui.QCheckBox    ("Reroll 1", self)
        ck_1.setChecked(False)
        v_.addWidget(ck_1)
        
        rb_10.setChecked(True)
        
        grp_dtl   = QtGui.QGroupBox("Details", self)
        v_        = QtGui.QVBoxLayout(grp_dtl)
        lv_dtl    = QtGui.QListView(self) 
        mod_dtl   = QtGui.QStringListModel(self)
        lv_dtl.setModel(mod_dtl)
        v_.addWidget(lv_dtl)        
        
        grp_tot   = QtGui.QGroupBox("Total", self)
        v_        = QtGui.QVBoxLayout(grp_tot)
        le_tot    = QtGui.QLineEdit(self) 
        le_tot.setReadOnly(True)
        v_.addWidget(le_tot)
        
        for w in [grp_expr, grp_rules, grp_dtl, grp_tot]:
            vbox.addWidget(w)
            
        le_expr.returnPressed.connect( self.solve_expr )
        
        self.le_expr = le_expr
        self.le_tot  = le_tot
        
        self.rb_none = rb_none
        self.rb_10   = rb_10
        self.rb_9    = rb_9
        self.rb_8    = rb_8
        self.ck_1    = ck_1
        
        self.mod_dtl = mod_dtl

    def solve_expr(self):
        self.clear_log()
        
        expr = self.le_expr.text()
        rpn  = ''
        val  = 0
        try:
            rpn = math_to_rpn(expr)
        except:
            print 'failed math_to_rpn, expr: %s' % expr
        
        if self.rb_none.isChecked():
            set_explode(999)
        elif self.rb_10.isChecked():
            set_explode(10)
        elif self.rb_9.isChecked():
            set_explode(9)
        elif self.rb_8.isChecked():
            set_explode(8)
            
        set_reroll_1(self.ck_1.isChecked())
            
        set_output_cb( self.add_to_log )
        
        try:
            val = rpn_solve(rpn)
        except:
            print 'failed rpn_solve, rpn: %s' % repr(rpn)
            
        self.le_tot.setText( str(val) )
        
    def clear_log(self):
        self.mod_dtl.setStringList([])
        
    def add_to_log(self, str_):
        if len(str_) > 0:
            self.mod_dtl.setStringList( self.mod_dtl.stringList() + [str_])
            