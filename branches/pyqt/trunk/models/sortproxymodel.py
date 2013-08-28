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

from PyQt4 import QtGui, QtCore



class ColorFriendlySortProxyModel(QtGui.QSortFilterProxyModel):
    def __init__(self, parent = None):
        super(ColorFriendlySortProxyModel, self).__init__(parent)

    def data(self, index, role):
        # respect alternate row color
        if role == QtCore.Qt.BackgroundRole:
            return self.sourceModel().bg_color[ index.row() % 2 ]            
        return super(ColorFriendlySortProxyModel, self).data(index, role)
