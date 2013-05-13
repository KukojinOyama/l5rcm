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

import models
from xmlutils import read_attribute, read_attribute_int, read_attribute_bool, read_sub_element_text
from requirements import Requirement, RequirementOption

class SchoolSkill(object):
    
    @staticmethod
    def build_from_xml(elem):
        f = SchoolSkill()
        f.id   = read_attribute    ( elem, 'id'       )
        f.rank = read_attribute_int( elem, 'rank'     )
        f.emph = read_attribute    ( elem, 'emphases' )
        return f
        
    def __eq__(self, obj):
        return obj and obj.id == self.id

    def __ne__(self, obj):
        return not self.__eq__(obj)
        
    def __hash__(self):
        return obj.id.__hash__()   

class SchoolSkillWildcard(object):
    @staticmethod
    def build_from_xml(elem):
        f = SchoolSkillWildcard()
        f.value    = elem.text
        f.modifier = read_attribute( elem, 'modifier', 'or' )
        return f 
        
class SchoolSkillWildcardSet(object):

    @staticmethod
    def build_from_xml(elem):
        f = SchoolSkillWildcardSet()
        f.rank = read_attribute_int( elem, 'rank' )
        f.wildcards = []
        for se in elem.iter():
            if se.tag == 'Wildcard':
                f.wildcards.append(SchoolSkillWildcard.build_from_xml(se))        
        return f  
        
class SchoolTech(object):        

    @staticmethod
    def build_from_xml(elem):
        f = SchoolTech()
        f.id   = read_attribute    ( elem, 'id'       )
        f.name = read_attribute    ( elem, 'name', '' )        
        f.rank = read_attribute_int( elem, 'rank'     )
        return f
     
    def __str__(self):
        return self.name or self.id

    def __unicode__(self):
        return self.name or self.id
        
    def __eq__(self, obj):
        return obj and obj.id == self.id

    def __ne__(self, obj):
        return not self.__eq__(obj)
        
    def __hash__(self):
        return obj.id.__hash__()
        
class SchoolSpell(object):
    
    @staticmethod
    def build_from_xml(elem):
        f = SchoolSpell()
        f.id = read_attribute( elem, 'id' )
        return f
        
    def __eq__(self, obj):
        return obj and obj.id == self.id

    def __ne__(self, obj):
        return not self.__eq__(obj)
        
    def __hash__(self):
        return obj.id.__hash__()      
        
class SchoolSpellWildcard(object):

    @staticmethod
    def build_from_xml(elem):
        f = SchoolSpellWildcard()
        f.count   = read_attribute_int( elem, 'count'   )
        f.element = read_attribute    ( elem, 'element' )
        f.tag     = read_attribute    ( elem, 'tag'     )
        return f
        
class SchoolKiho(object):

    @staticmethod
    def build_from_xml(elem):
        f = SchoolKiho()
        f.count   = read_attribute_int( elem, 'count' )   
        f.text    = elem.text
        return f
        
class SchoolTattoo(object):

    @staticmethod
    def build_from_xml(elem):
        f = SchoolTattoo()
        f.count   = read_attribute_int ( elem, 'count'   )
        f.allowed = read_attribute_bool( elem, 'allowed' )
        f.text    = elem.text
        return f        
        
class School(object):

    @staticmethod
    def build_from_xml(elem):
        f = School()
        f.id     = read_attribute( elem, 'id'     )
        f.name   = read_attribute( elem, 'name'   )
        f.clanid = read_attribute( elem, 'clanid' )
        
        f.trait  = read_sub_element_text( elem, 'Trait' )
        
        f.tags  = []
        for se in elem.find('Tags').iter():
            if se.tag == 'Tag':
                f.tags.append(se.text)
                        
        f.affinity    = read_sub_element_text( elem, 'Affinity'   )
        f.deficiency  = read_sub_element_text( elem, 'Deficiency' )
        f.honor       = float( read_sub_element_text( elem, 'Honor', "0.0" ) )
                
        # school skills
        f.skills     = []
        f.skills_pc  = []
        for se in elem.find('Skills').iter():
            if se.tag == 'Skill':
                f.skills.append(SchoolSkill.build_from_xml(se))
            elif se.tag == 'PlayerChoose':
                f.skills_pc.append(SchoolSkillWildcardSet.build_from_xml(se))

        # school techs
        f.techs = []
        for se in elem.find('Techs').iter():
            if se.tag == 'Tech':
                f.techs.append(SchoolTech.build_from_xml(se))
                
        # school spells
        f.spells    = []
        f.spells_pc = []
        for se in elem.find('Spells').iter():
            if se.tag == 'PlayerChoose':
                f.spells_pc.append(SchoolSpellWildcard.build_from_xml(se))
            elif se.tag == 'Spell':
                f.spells.append(SchoolSpell.build_from_xml(se))
                
        # requirements
        f.require = []        
        
        for se in elem.find('Requirements'):
            if se.tag == 'Requirement':
                f.require.append(Requirement.build_from_xml(se))        
            if se.tag == 'RequirementOption':
                f.require.append(RequirementOption.build_from_xml(se))  

        # kihos and tattoos
        f.kihos   = None
        f.tattoos = None
        if elem.find('Kihos') is not None:
            f.kihos = SchoolKiho.build_from_xml( elem.find('Kihos') )
        if elem.find('Tattoos') is not None:
            f.tattoos = SchoolTattoo.build_from_xml( elem.find('Tattoos') )
        
        return f

    def __str__(self):
        return self.name or self.id
    
    def __unicode__(self):
        return self.name or self.id
        
    def __eq__(self, obj):
        return obj and obj.id == self.id

    def __ne__(self, obj):
        return not self.__eq__(obj)
        
    def __hash__(self):
        return obj.id.__hash__()


