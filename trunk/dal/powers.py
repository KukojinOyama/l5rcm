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

class PowerRequirement(object):

    @staticmethod
    def build_from_xml(elem):
        f = PowerRequirement()
        f.field = elem.attrib['field']
        f.type  = elem.attrib['type' ]
        f.min = int(elem.attrib['min']) if ('min' in elem.attrib) else None
        f.max = int(elem.attrib['max']) if ('max' in elem.attrib) else None
        f.trg = elem.attrib['trg'] if ('trg' in elem.attrib) else None
        f.text = elem.text
        return f  

class Kiho(object):

    @staticmethod
    def build_from_xml(elem):
        f = Kiho()
        f.name    = elem.attrib['name']
        f.id      = elem.attrib['id']
        f.element = elem.attrib['element']
        f.type    = elem.attrib['type']
        f.mastery = int(elem.attrib['mastery'])
        f.desc    = elem.find('Description').text if (elem.find('Description') is not None) else ''
        return f        
        
    def __str__(self):
        return self.name or self.id
        
    def __unicode__(self):
        return self.name

    def __eq__(self, obj):
        return obj and obj.id == self.id

class Kata(object):

    @staticmethod
    def build_from_xml(elem):
        f = Kata()
        f.name    = elem.attrib['name']
        f.id      = elem.attrib['id']
        f.element = elem.attrib['element']
        f.mastery = int(elem.attrib['mastery'])
        f.desc    = elem.find('Description').text if (elem.find('Description') is not None) else ''
        # requirements
        f.require = []
        for se in elem.find('Requirements').iter():
            if se.tag == 'Requirement':
                f.require.append(PowerRequirement.build_from_xml(se))         
        return f        
        
    def __str__(self):
        return self.name or self.id
        
    def __unicode__(self):
        return self.name

    def __eq__(self, obj):
        return obj and obj.id == self.id

