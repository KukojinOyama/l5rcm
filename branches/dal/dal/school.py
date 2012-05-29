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

class School(object):

    @staticmethod
    def build_from_xml(elem):
        f = School()
        f.name = elem.attrib['name']
        f.clan  = elem.find('Clan').text
        f.trait = elem.find('Trait').text
        f.tags  = []
        for se in elem.find('Tags').iter():
            if se.tag == 'Tag':
                f.tags.append(se.text.lower()) # Tags are lower case
        aff_tag = elem.find('Affinity')
        def_tag = elem.find('Deficiency')
        f.affinity   = aff_tag.text if aff_tag else None
        f.deficiency = def_tag.text if def_tag else None
        return f  

