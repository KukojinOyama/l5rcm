#!/usr/bin/python

import sys
from PySide import QtCore, QtGui

def find(f, seq):
  """Return first item in sequence where f(item) == True."""
  for item in seq:
    if f(item):
      return item

class CkNumWidget(QtGui.QWidget):
    def __init__(self, parent = None):
        super(CkNumWidget, self).__init__(parent)

        self.checks = []
        self.value = 0
        hbox = QtGui.QHBoxLayout(self)
        hbox.setSpacing(0)
        hbox.setContentsMargins(0,0,0,0)
        for i in xrange(0, 10):
            ck = QtGui.QCheckBox(self)
            self.checks.append( ck )
            hbox.addWidget( ck )
            ck.clicked.connect(self.on_ck_toggled)
            ck.setObjectName( str(i) )

    def on_ck_toggled(self):
        fred = find(lambda ck: ck == self.sender(), self.checks)
        flag = fred.isChecked()
        if flag:
            self.value = int(fred.objectName())
        else:
            self.value = int(fred.objectName()) - 1
        for i in xrange(0, 10):
            ck = self.checks[i]
            if flag:
                if int(ck.objectName()) <= self.value:
                    self.checks[i].setChecked(flag)
                else:
                    self.checks[i].setChecked(not flag)
            else:
                if int(ck.objectName()) <= self.value:
                    self.checks[i].setChecked(not flag)
                else:
                    self.checks[i].setChecked(flag)
        #print 'value is %d' % self.value

    def set_value(self, value):
        if value == self.value:
            return
        for i in xrange(0, 10):
            ck = self.checks[i]
            if int(ck.objectName()) <= value:
                self.checks[i].setChecked(True)
            else:
                self.checks[i].setChecked(False)
        self.value = value

    def get_value(self):
        return self.value

### MAIN ###
def main():
    app = QtGui.QApplication(sys.argv)

    dlg = QtGui.QDialog()
    vbox = QtGui.QVBoxLayout(dlg)
    vbox.addWidget( CkNumWidget(dlg) )
    dlg.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
