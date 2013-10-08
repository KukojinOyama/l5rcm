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

import models
from PySide import QtCore

class DebugObserver(QtCore.QObject):

    on_property_changed = QtCore.Signal(str, object, object)

    def __init__(self, parent = None):
        super(DebugObserver, self).__init__(parent)

    def property_changed(self, path, old_value, new_value):
        self.on_property_changed.emit( path, old_value, new_value )

    def list_create(self, obj, key):
        self.property_changed( "add list {0}/{1}".format(obj.obj_name(), key), None, obj[key] )

    def list_set(self, obj, key, old_value):
        self.property_changed( "set list {0}/{1}".format(obj.obj_name(), key), old_value, obj[key] )

    def list_del(self, obj, key, old_value):
        self.property_changed( "del list {0}/{1}".format(obj.obj_name(), key), old_value, None )

    def list_setslice(self, obj, start, end, sequence, old_value):
        pass

    def list_delslice(self, obj, start, old_value):
        pass

    def list_append(self, obj):
        self.list_create(obj, -1)

    def list_pop(self, obj, old_value):
        self.list_del(obj, 0, old_value)

    def list_extend(self, obj, new_value):
        pass

    def list_insert(self, obj, index, element):
        self.list_create(obj, index)

    def list_remove(self, obj, index, element):
        self.list_del(obj, index, element)

    def list_reverse(self, obj):
        pass

    def list_sort(self, obj, old_value):
        pass
