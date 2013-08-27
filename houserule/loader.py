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

import os
import sys
import importlib
import glob

class HouseRuleLoader(object):

    PACKAGE_NAME = 'houserules'

    def __init__(self):
        self.extension_list = []

    @property
    def search_path(self):
        return self._search_path

    @search_path.setter
    def search_path(self, value):
        self._search_path = os.path.realpath(value)
        if self._search_path not in sys.path:
             sys.path.append(self._search_path)
        self.reload ()


    def dispose(self):
        for e in self.extension_list:
            e.deactivate()
            del e
        self.extension_list = []

    def reload(self):

        self.dispose()

        hr_path  = os.path.join(self._search_path, self.PACKAGE_NAME)

        for ext_name in glob.iglob( os.path.join(hr_path,"*.py") ):
            file_name = os.path.basename(ext_name)
            mod_name  = os.path.splitext(file_name)[0]
            if mod_name == '__init__': continue

            try:
                mod = importlib.import_module('{}.{}'.format(self.PACKAGE_NAME,mod_name))
                ext = mod.create()

                if ext:
                    self.extension_list.append(ext)
                    print("loaded extension {}, {}".format(ext.id, ext.name))
                else:
                    raise Exception("Not a valid HouseRule")

            except Exception as e:
                print('cannot load extension from {} because {}'.format(ext_name, str(e)))

    def activate_all(self, ui):
        for e in self.extension_list:
            e.activate(ui)

    def update_all(self, ui, pc, dal):
        for e in self.extension_list:
            e.activate(ui, pc, dal)

    def deactivate_all(self):
        for e in self.extension_list:
            e.deactivate()
