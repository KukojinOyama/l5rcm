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

class SchoolSkill(object):
    
    @staticmethod
    def build_from_xml(elem):
        f = SchoolSkill()
        return f
        
class SchoolSkillWildcard(object):

    @staticmethod
    def build_from_xml(elem):
        f = SchoolSkillWildcard()
        f.rank = int(elem.attrib['rank'])
        f.wildcards = []
        for se in elem.iter():
            if se.tag == 'Wildcard':
                f.wildcards.append(se.text)        
        return f  
        
class SchoolTech(object):        

    @staticmethod
    def build_from_xml(elem):
        f = SchoolTech()
        f.name = elem.attrib['name']
        f.rank = int(elem.attrib['rank'])
        return f
        
class SchoolSpellWildcard(object):

    @staticmethod
    def build_from_xml(elem):
        f = SchoolSpellWildcard()
        return f
        
class SchoolRequirement(object):

    @staticmethod
    def build_from_xml(elem):
        f = SchoolRequirement()
        f.field = elem.attrib['field']
        f.type  = elem.attrib['type' ]
        f.min = int(elem.attrib['min']) if 'min' in elem.attrib else None
        f.max = int(elem.attrib['max']) if 'max' in elem.attrib else None
        f.trg = int(elem.attrib['trg']) if 'trg' in elem.attrib else None
        return f              

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
        hon_tag = elem.find('Honor')
        f.affinity   = aff_tag.text if aff_tag else None
        f.deficiency = def_tag.text if def_tag else None
        f.honor      = float(hon_tag) if hon_tag else 0.0
        
        # school skills
        f.skills     = []
        f.skills_pc  = []
        for se in elem.find('Skills').iter():
            if se.tag == 'Skill':
                f.skills.append(SchoolSkill.build_from_xml(se))
            elif se.tag == 'PlayerChoose':
                f.skills_pc.append(SchoolSkillWildcard.build_from_xml(se))

        # school techs
        f.techs = []
        for se in elem.find('Techs').iter():
            if se.tag == 'Tech':
                f.techs.append(SchoolTech.build_from_xml(se))
                
        # school spells
        f.spells = []
        for se in elem.find('Spells').iter():
            if se.tag == 'PlayerChoose':
                f.spells.append(SchoolSpellWildcard.build_from_xml(se))
                
        # requirements
        f.require = []
        for se in elem.find('Requirements').iter():
            if se.tag == 'Requirement':
                f.require.append(SchoolRequirement.build_from_xml(se))        
                
        return f

    def __eq__(self, obj):
        return obj and obj.name == self.name


