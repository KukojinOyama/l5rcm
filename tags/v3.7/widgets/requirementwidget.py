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
#import rules
import dal

from PySide import QtCore, QtGui

class RequirementsWidget(QtGui.QWidget):

    def __init__(self, parent = None):
        super(RequirementsWidget, self).__init__(parent)
       
        self.vbox        = QtGui.QVBoxLayout(self)
        self.checkboxes  = []
        
    def set_requirements(self, requirements):

        for ck in self.checkboxes:
            del ck
            
        for r in requirements:
            ck = QtGui.QCheckBox(r.text, self)
            if type(r) is dal.school.SchoolRequirementOption:
                ck.setEnabled(False)
            else:
                ck.setEnabled(r.type == 'more')
            self.vbox.addWidget(ck)
            self.checkboxes.append(ck)

        
### MAIN ###
def main():
    app = QtGui.QApplication(sys.argv)

    dlg  = QtGui.QDialog()
    vbox = QtGui.QVBoxLayout(dlg)
    w    = RequirementsWidget(dlg) 
    vbox.addWidget(w)
    dlg.show()
    
    # add some requirements
    d = dal.Data( ['data_packs'] )    
    from dal import query
    school = query.get_school(d, "mantis_tsuruchi_master_bowman")
    
    w.set_requirements( school.require )
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
