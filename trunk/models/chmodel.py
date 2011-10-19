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

import advances as adv
import outfit
import json
import os

from copy import deepcopy

# RINGS
class RINGS:
    EARTH = 0
    AIR   = 1
    WATER = 2
    FIRE  = 3
    VOID  = 4

    _names = dict(earth=0, air=1, water=2, fire=3, void=4)

def ring_from_name(name):
    if name in RINGS._names:
        return RINGS._names[name]
    return -1

class ATTRIBS:
    # earth ring
    STAMINA      = 0
    WILLPOWER    = 1

    # air ring
    REFLEXES     = 2
    AWARENESS    = 3

    # water ring
    STRENGTH     = 4
    PERCEPTION   = 5

    # fire ring
    AGILITY      = 6
    INTELLIGENCE = 7

    _names = dict(stamina=0, willpower=1, reflexes=2, awareness=3,
                  strength=4, perception=5, agility=6, intelligence=7)

def attrib_from_name(name):
    if name in ATTRIBS._names:
        return ATTRIBS._names[name]
    return -1

class MyJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)

def encode_pc_model(obj):
    if isinstance(obj, BasePcModel) or \
       isinstance(obj, AdvancedPcModel):
        return obj.__dict__
    return json.JSONEncoder.default(self, obj)

class BasePcModel(object):
    def __init__(self):
        self.void        = 0
        self.attribs     = [0, 0, 0, 0, 0, 0, 0, 0]
        self.skills      = {}
        self.emph        = {}
        self.pending_wc  = []
        self.tags        = []
        self.honor       = 0.0
        self.glory       = 0.0
        self.status      = 0.0
        self.taint       = 0.0
        self.school_tech = None

    def load_default(self):
        self.void    = 2
        self.attribs = [2, 2, 2, 2, 2, 2, 2, 2]
        self.rank    = 1
        self.glory   = 2.0
        
    def add_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)
    
    def has_tag(self, tag):
        return tag in self.tags
        
    def del_tag(self, tag):
        if tag in self.tags:
            self.tags.removeone(tag)
            
    def clear_tags(self):
        self.tags = []

class AdvancedPcModel(BasePcModel):
    def __init__(self):
        super(AdvancedPcModel, self).__init__()

        # clan selection
        self.step_0 = BasePcModel()
        # family selection
        self.step_1 = BasePcModel()
        # school selection
        self.step_2 = BasePcModel()

        self.unsaved = False

        self.name      = ''
        self.clan      = 0
        self.school    = 0
        self.family    = 0

        self.insight   = 0
        self.advans    = []

        self.armor     = None
        self.weapons   = []
        self.techs     = []
        
        self.mastery_abilities = []

        self.attrib_costs = [4, 4, 4, 4, 4, 4, 4, 4]
        self.void_cost    = 6
        self.health_multiplier = 2
        self.exp_limit = 40
        self.wounds = 0        
        self.mod_init = (0, 0)
        self.void_points = self.get_void_rank()
        self.unlock_schools = False

    def load_default(self):
        self.step_0.load_default()

    def is_dirty(self):
        return self.unsaved

    def get_ring_rank(self, idx):
        if idx == RINGS.VOID:
            return self.get_void_rank()

        idx_1 = idx*2
        idx_2 = idx_1 + 1
        a, b   = self.get_attrib_rank(idx_1), self.get_attrib_rank(idx_2)

        return min(a, b)
           
    def get_attrib_rank(self, attrib):
        a = self.step_0.attribs[attrib]
        b = self.step_1.attribs[attrib]
        c = self.step_2.attribs[attrib]

        d = a+b+c

        for adv in self.advans:
            if adv.type != 'attrib':
                continue
            if adv.attrib == attrib: d += 1

        return d

    def get_void_rank(self):
        v = self.step_0.void + self.step_1.void + self.step_2.void

        for adv in self.advans:
            if adv.type != 'void':
                continue
            v += 1

        return v

    def get_skill_rank(self, uuid):
        if uuid in self.get_school_skills():
            rank = self.step_2.skills[uuid]
        else:
            rank = 0
        for adv in self.advans:
            if adv.type != 'skill' or adv.skill != uuid:
                continue
            rank += 1
        return rank
        
    def get_perk_info(self, uuid):
        for adv in self.advans:
            if adv.type != 'perk' or adv.perk != uuid:
                continue
            return adv.rank, adv.cost, adv.tag, adv.extra

    def get_honor(self):
        return self.step_2.honor + self.honor

    def get_glory(self):
        return self.step_0.glory + self.glory

    def get_status(self):
        return self.status

    def get_taint(self):
        return self.taint

    def get_insight(self):
        n = 0
        for i in xrange(0, 5):
            n += self.get_ring_rank(i)*10
        for s in self.get_skills():
            n += self.get_skill_rank(s)
        return n

    def get_insight_rank(self):
        value = self.get_insight()

        if value > 299: return 8
        if value > 274: return 7
        if value > 249: return 6
        if value > 224: return 5
        if value > 199: return 4
        if value > 174: return 3
        if value > 149: return 2
        return 1

    def get_base_tn(self):
        # reflexes * 5 + 5
        return self.get_attrib_rank(ATTRIBS.REFLEXES)*5+5

    def get_armor_tn(self):
        if self.armor is not None:
            return self.armor.tn
        else:
            return 0

    def get_armor_rd(self):
        if self.armor is not None:
            return self.armor.rd
        else:
            return 0
            
    def get_armor_name(self):
        if self.armor is not None:
            return self.armor.name
        else:
            return 'No Armor'

    def get_cur_tn(self):
        return self.get_base_tn() + self.get_armor_tn()

    def get_health_rank(self, idx):
        if idx == 0:
            return self.get_ring_rank(RINGS.EARTH) * 5
        return  self.get_ring_rank(RINGS.EARTH) * self.health_multiplier
        
    def get_max_wounds(self):
        max_ = 0
        for i in xrange(0, 8):
            max_ += self.get_health_rank(i)
        return max_

    def get_base_initiative(self):
        return ( self.get_insight_rank() +
                 self.get_attrib_rank(ATTRIBS.REFLEXES),
                 self.get_attrib_rank(ATTRIBS.REFLEXES))

    def get_px(self):
        count = 0
        for a in self.advans:
            count += a.cost
        return count

    def get_attrib_cost(self, idx):
        return self.attrib_costs[idx]

    def get_pending_wc_skills(self):
        return self.step_2.pending_wc

    def get_school_skills(self):
        return [ int(x) for x in self.step_2.skills.keys() ]

    def get_skills(self, school = True):
        l = []
        if school:
            l = self.get_school_skills()
        for adv in self.advans:
            if adv.type != 'skill' or \
              adv.skill in self.step_2.skills.keys() or \
              adv.skill in l:
                continue
            l.append(adv.skill)
        return l

    def get_skill_emphases(self, skill_id):
        emph = []
        # search school skills
        if skill_id in self.step_2.emph:
            emph += self.step_2.emph[skill_id]
        for adv in self.advans:
            if adv.type != 'emph' or adv.text in emph:
                continue
            if adv.skill == skill_id:
                emph.append(adv.text)
        return emph
        
    def get_techs(self):
        ls = []
        if self.step_2.school_tech is not None:
            ls.append( self.step_2.school_tech )
        ls += self.techs
        return ls
        
    def get_perks(self):
        for adv in self.advans:
            if adv.type != 'perk':
                continue
            yield adv.perk
            
    def get_merits(self):
        for adv in self.advans:
            if adv.type != 'perk' or adv.cost < 0:
                continue
            yield adv.perk
            
    def get_flaws(self):
        for adv in self.advans:
            if adv.type != 'perk' or adv.cost > 0:
                continue
            yield adv.perk              
        
    def get_spells(self):
        return []
       
    def has_tag(self, tag):
        return tag in self.tags or \
               self.step_1.has_tag(tag) or \
               self.step_2.has_tag(tag)
        
    def can_get_other_techs(self):
        if not self.has_tag('bushi') and \
           not self.has_tag('monk') and \
           not self.has_tag('courtier') and \
           not self.has_tag('ninja'):
           return False
           
        return len(self.get_techs()) < self.get_insight_rank()
                
    def can_get_other_spells(self):
        if not self.has_tag('shugenja'):
            return
            
        target_spells = self.get_insight_rank() * 3
        return len(self.get_spells()) < target_spells

    def add_school_skill(self, skill_uid, skill_rank, emph = None):
        if skill_uid in self.step_2.skills:
            self.step_2.skills[skill_uid] += skill_rank
        else:
            self.step_2.skills[skill_uid] = skill_rank
        if emph is not None:
            if skill_uid not in self.step_2.emph:
                self.step_2.emph[skill_uid] = []
            self.step_2.emph[skill_uid].append(emph)

        self.unsaved = True

    def add_pending_wc_skill(self, wc, skill_rank):
        self.step_2.pending_wc.append( (wc, skill_rank) )
        self.unsaved = True

    def clear_pending_wc_skills(self):
        self.step_2.pending_wc = []
        self.unsaved = True
        
    def add_weapon(self, item):
        self.weapons.append( item )
        
    def set_family(self, family_id = 0, perk = None, perkval = 1, tags = []):
        if self.family == family_id:
            return
        self.step_1  = BasePcModel()
        self.unsaved = True
        self.family  = family_id
        if family_id == 0:
            return

        for t in tags:       
            self.step_1.add_tag(t)            
            
        # void ?
        if perk == 'void':
            self.step_1.void += perkval
            return True
        else:
            a = attrib_from_name(perk)
            if a >= 0:
                self.step_1.attribs[a] += perkval
                return True
        return False        

    def set_school(self, school_id = 0, perk = None, perkval = 1,
                         honor = 0.0, tags = []):
        if self.school == school_id:
            return
        self.step_2  = BasePcModel()
        self.unsaved = True
        self.school  = school_id
        self.clear_pending_wc_skills()
        # also reset tech
        self.techs = []
        if school_id == 0:
            return

        self.step_2.honor = honor

        for t in tags:       
            self.step_2.add_tag(t)

        # void ?
        if perk == 'void':
            self.step_2.void += perkval
            return True
        else:
            a = attrib_from_name(perk)
            if a >= 0:
                self.step_2.attribs[a] += perkval
                return True
        return False
        
    def set_free_school_tech(self, tech_uuid):
        self.step_2.school_tech = tech_uuid
        
    def add_tech(self, tech_uuid):
        if tech_uuid not in self.techs:
            self.techs.append(tech_uuid)
            
    def set_void_points(self, value):
        self.void_points = value
        self.unsaved = True
                
    def set_honor(self, value):
        self.honor = value - self.step_2.honor
        self.unsaved = True

    def set_glory(self, value):
        self.glory = value - self.step_0.glory
        self.unsaved = True

    def set_status(self, value):
        self.status = value
        self.unsaved = True

    def set_taint(self, value):
        self.taint = value
        self.unsaved = True

    def add_advancement(self, adv):
        self.advans.append(adv)
        self.unsaved = True

    def pop_advancement(self):
        self.advans.pop()
        self.unsaved = True
        
    def toggle_unlock_schools(self):
        self.unlock_schools = not self.unlock_schools
        self.unsaved = True

    def save_to(self, file):
        self.unsaved = False

        print 'saving to %s' % file

        fp = open(file, 'wt')
        if fp:
            json.dump( self, fp, cls=MyJsonEncoder, indent=2 )
            fp.close()
            return True
        return False

    def load_from(self, file_):
        if len(file_) == 0 or not os.path.exists(file_):
            return False
            
        fp = open(file_, 'rt')
        if fp:
            obj = json.load(fp)
            fp.close()

            self.__dict__ = deepcopy(obj)

            self.step_0 = BasePcModel()
            self.step_1 = BasePcModel()
            self.step_2 = BasePcModel()

            self.step_0.__dict__ = deepcopy(obj['step_0'])
            self.step_1.__dict__ = deepcopy(obj['step_1'])
            self.step_2.__dict__ = deepcopy(obj['step_2'])

            self.advans = []
            for ad in obj['advans']:
                a = adv.Advancement(None, None)
                a.__dict__ = deepcopy(ad)                
                self.advans.append(a)
                
            # armor
            self.armor = outfit.ArmorOutfit()
            if obj['armor'] is not None:
                self.armor.__dict__ = deepcopy(obj['armor'])
            
            # weapons
            for w in obj['weapons']:
                item = outfit.WeaponOutfit()
                item.__dict__ = deepcopy(w)
                self.add_weapon(item)

            self.unsaved  = False           
            
            return True
        return False
