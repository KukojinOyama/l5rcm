# -*- coding: utf-8 -*-
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

"""
{
    "id": "core",
    "display_name": "Core book",
    "language": "en_US",
    "authors": ["Daniele Simonetti"],
    "version": "3.9",
    "update-uri": "",
    "download-uri": "",
    "min-cm-version": "3.8"
}
"""

from PySide import QtCore, QtGui

class ManifestWidget(QtGui.QWidget):
    def __init__(self, model, parent = None):
        super(ManifestWidget, self).__init__(parent)

        self.fl = QtGui.QFormLayout(self)

        self.le_id      = QtGui.QLineEdit(self)
        self.le_name    = QtGui.QLineEdit(self)
        self.le_lang    = QtGui.QLineEdit(self)
        self.le_authors = QtGui.QLineEdit(self)
        self.le_version = QtGui.QLineEdit(self)
        self.le_min_ver = QtGui.QLineEdit(self)

        self.fl.addRow(             "Id", self.le_id     )
        self.fl.addRow(           "Name", self.le_name   )
        self.fl.addRow(       "Language", self.le_lang   )
        self.fl.addRow(        "Authors", self.le_authors)
        self.fl.addRow(        "Version", self.le_version)
        self.fl.addRow("Min. CM Version", self.le_min_ver)

        self.fl.setContentsMargins(12,12,12,12)

        self.model = model

    def load(self):
        obj = self.model.object
        self.le_id     .setText( obj.id                 )
        self.le_name   .setText( obj.display_name       )
        self.le_lang   .setText( obj.language           )
        self.le_authors.setText( ', '.join(obj.authors) )
        self.le_version.setText( obj.version            )
        self.le_min_ver.setText( obj.min_version        )

    def apply(self):
        print("")

