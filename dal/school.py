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
from __init__ import read_attribute, read_attribute_int, read_attribute_bool, read_sub_element_text

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
        
class SchoolSpell(object):
    
    @staticmethod
    def build_from_xml(elem):
        f = SchoolSpell()
        f.id = read_attribute( elem, 'id' )
        return f
        
    def __eq__(self, obj):
        return obj and obj.id == self.id         
        
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
        
class SchoolRequirement(object):

    @staticmethod
    def build_from_xml(elem):
        f = SchoolRequirement()
        f.field = read_attribute    ( elem, 'field'   )
        f.type  = read_attribute    ( elem, 'type'    )
        f.min   = read_attribute_int( elem, 'min', -1 )
        f.max   = read_attribute_int( elem, 'min', 999)
        f.trg   = read_attribute    ( elem, 'trg'     )
        f.text = elem.text
        return f
        
    def __str__(self):
        return self.text
        
    def __unicode__(self):
        return self.text
        
    def in_range(self, value):
        return value >= self.min and value <= self.max
        
    def match(self, pc, dstore):
        import models              
        
        if self.field.startswith('*'):
            return self.match_wildcard(pc, dstore)        
        if self.field == 'honor':
            return self.in_range( pc.get_honor() )            
        if self.field == 'status':
            return self.in_range( pc.get_status() )
        if self.field == 'glory':
            return self.in_range( pc.get_glory() )
        if self.type == 'ring':
            return self.in_range( pc.get_ring_rank(self.field) )
        if self.type == 'trait':
            return self.in_range( pc.get_trait_rank(self.field) )
        if self.type == 'skill':
            skill_id = self.field
            if not skill_id: return True
            if self.trg and self.trg not in pc.get_skill_emphases(skill_id):
                return False # missing emphases
            if (skill_id not in pc.get_skills() or
                not self.in_range( pc.get_skill_rank(skill_id) )):                
                return False
            pc.set_skill_rank(skill_id, 0)
            return True
        if self.type == 'tag':
            return pc.has_tag(self.field)
        if self.type == 'rule':
            return pc.has_rule(self.field)         
        return True
        
    def match_wc_ring(self, pc, dstore):
        r = False
        if self.field == '*any': # any ring 
            for i in xrange(0, 5):
                ring_id = models.ring_name_from_id(i)
                if self.in_range( pc.get_ring_rank(ring_id) ):
                    pc.set_ring_rank(ring_id, 0)
                    r = True
                    break
        return r
        
    def match_wc_trait(self, pc, dstore):
        r = False
        if self.field == '*any': # any trait 
            for i in xrange(0, 8):
                trait_id = models.attrib_name_from_id(i)
                if self.in_range( pc.get_trait_rank(trait_id) ):
                    pc.set_trait_rank(trait_id, 0)
                    r = True
                    break
        return r
        
    def match_wc_skill(self, pc, dstore):
        r = False
        if self.field == '*any': # any skills
            for k in pc.get_skills():
                if self.in_range( pc.get_skill_rank(k) ):                
                    r = True
                    pc.set_skill_rank(k, 0)
        else:
            import dal
            import dal.query
            
            tag = self.field[1:]
            for k in pc.get_skills():
                sk = dal.query.get_skill(dstore, k)
                if tag not in sk.tags:
                    continue                    
                if self.in_range( pc.get_skill_rank(k) ):
                    r = True
                    pc.set_skill_rank(k, 0)
                    break
        return r
        
    def match_wc_school(self, pc, dstore):
        r = False
        if self.field == '*any': # any school
            for k in pc.get_schools():
                if self.in_range( pc.get_school_rank(k) ):
                    r = True
                    pc.set_school_rank(k, 0)
        else:
            import dal
            import dal.query
            
            tag = self.field[1:]
            for k in pc.get_schools():
                sk = dal.query.get_school(dstore, k)  
                if not sk:
                    print('school not found', k)
                    continue
                if tag not in sk.tags:
                    print(tag, 'not in', sk.tags)
                    continue                    
                if self.in_range( pc.get_school_rank(k) ):
                    r = True
                    pc.set_school_rank(k, 0)
                    break
        return r        

    def match_wildcard(self, model, dstore):
        got_req = -1
        if self.type == 'ring':
            return self.match_wc_ring(model, dstore)
        if self.type == 'trait':
            return self.match_wc_trait(model, dstore)
        if self.type == 'skill':
            return self.match_wc_skill(model, dstore)
        if self.type == 'school':
            return self.match_wc_school(model, dstore)
        return True    
        
class SchoolRequirementOption(object):
    @staticmethod
    def build_from_xml(elem):
        f = SchoolRequirementOption()
        f.require = []
        f.text = elem.attrib['text'] if ('text' in elem.attrib) else ''
        for se in elem.iter():
            if se.tag == 'Requirement':
                f.require.append(SchoolRequirement.build_from_xml(se))
        return f
        
    def match(self, model, dstore):
        # at least one should match
        for r in self.require:
            if r.match(model, dstore):
                return True
        return False

    def __str__(self):
        return self.text
        
    def __unicode__(self):
        return self.text

class School(object):

    @staticmethod
    def build_from_xml(elem):
        f = School()
        f.id     = read_attribute( elem, 'id'     )
        f.name   = read_attribute( elem, 'name'   )
        f.clanid = read_attribute( elem, 'clanid' )
        f.trait  = read_attribute( elem, 'clanid' )
        
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
                f.require.append(SchoolRequirement.build_from_xml(se))        
            if se.tag == 'RequirementOption':
                f.require.append(SchoolRequirementOption.build_from_xml(se))  

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


