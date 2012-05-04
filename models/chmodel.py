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
import modifiers
import json
import os
import rules

from copy import deepcopy

# RINGS
class RINGS:
    EARTH = 0
    AIR   = 1
    WATER = 2
    FIRE  = 3
    VOID  = 4

    _names = dict(earth=0, air=1, water=2, fire=3, void=4)
    _ids   = ['earth', 'air', 'water', 'fire', 'void']

def ring_from_name(name):
    if name in RINGS._names:
        return RINGS._names[name]
    return -1

def ring_name_from_id(ring_id):
    if ring_id >= 0 and ring_id < len(RINGS._ids):
        return RINGS._ids[ring_id]

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
    _ids   = ['stamina', 'willpower', 'reflexes', 'awareness', 'strength',
              'perception', 'agility', 'intelligence']

def attrib_from_name(name):
    if name in ATTRIBS._names:
        return ATTRIBS._names[name]
    return -1

def attrib_name_from_id(attrib_id):
    if attrib_id >= 0 and attrib_id < len(ATTRIBS._ids):
        return ATTRIBS._ids[attrib_id]

def get_ring_id_from_attrib_id(attrib_id):
    if attrib_id >= ATTRIBS.STAMINA and attrib_id <= ATTRIBS.INTELLIGENCE:
        return attrib_id // 2
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
        self.void               = 0
        self.attribs            = [0, 0, 0, 0, 0, 0, 0, 0]
        self.skills             = {}
        self.emph               = {}
        self.pending_wc         = []
        self.pending_wc_emph    = []
        self.pending_wc_spell   = []
        self.tags               = []
        self.honor              = 0.0
        self.glory              = 0.0
        self.status             = 0.0
        self.taint              = 0.0
        self.affinity           = None
        self.deficiency         = None

        self.start_spell_count = 0
        self.school_tech = None

    def load_default(self):
        self.void    = 2
        self.attribs = [2, 2, 2, 2, 2, 2, 2, 2]
        self.rank    = 1
        self.glory   = 1.0
        self.status  = 1.0

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

class CharacterSchool(object):
    def __init__(self, school_id = 0):
        self.school_id   = school_id
        self.school_rank = 1
        self.techs       = []
        self.tech_rules  = []
        self.skills      = {}
        self.emph        = {}
        self.spells      = [] 
        self.tags        = []
        self.affinity    = None
        self.deficiency  = None

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
        self.version = '0.0'

        self.name      = ''
        self.clan      = 0
        self.school    = 0
        self.family    = 0

        self.insight   = 0
        self.advans    = []

        self.armor      = None
        self.weapons    = []
        self.schools    = []

        self.mastery_abilities = []

        self.attrib_costs = [4, 4, 4, 4, 4, 4, 4, 4]
        self.void_cost    = 6
        self.health_multiplier = 2
        self.spells_per_rank = 3
        self.exp_limit = 40
        self.wounds = 0
        self.mod_init = (0, 0)
        self.void_points = self.get_void_rank()
        self.unlock_schools = False
        self.extra_notes = ''
        self.insight_calculation = None
        
        self.modifiers = []
        
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
            
        weakness_flaw = 'weak_%s' % attrib_name_from_id(attrib)
        if self.has_rule(weakness_flaw):
            return d-1
        return d

    def get_void_rank(self):
        v = self.step_0.void + self.step_1.void + self.step_2.void

        for adv in self.advans:
            if adv.type != 'void':
                continue
            v += 1

        return v
        
    def get_family(self):
        return self.family
        
    def get_school(self, index = -1):
        if len(self.schools) == 0 or index >= len(self.schools):
            return None
        if index < 0: index = len(self.schools)-1
        return self.schools[index]
        
    def get_school_id(self, index = -1):
        try:
            return self.get_school(index).school_id
        except:
            return 0
        
    def get_school_rank(self, index = -1):
        try:
            return self.get_school(index).school_rank
        except:
            return 0

    def get_skill_rank(self, uuid):
        if uuid in self.get_school_skills():
            rank = self.get_school_skill_rank(uuid)
        else:
            rank = 0
        for adv in self.advans:
            if adv.type != 'skill' or adv.skill != uuid:
                continue
            rank += 1
        return rank
        
    def get_honor(self):
        return self.step_2.honor + self.honor

    def get_glory(self):
        if self.has_tag('monk'):
            return self.glory
        return self.step_0.glory + self.glory

    def get_status(self):
        if self.has_rule('social_disadvantage'):
            return self.status
        return self.step_0.status + self.status

    def get_taint(self):
        return self.taint
        
    def get_affinity(self):
        return self.step_2.affinity or 'None'

    def get_deficiency(self):
        return self.step_2.deficiency or 'None'
        
    def get_insight(self):
        if self.insight_calculation:
            return self.insight_calculation(self)
        return rules.insight_calculation_1(self)
        
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
            
    def get_base_rd(self):
        if self.has_rule('hida_bushi_2'):
            return self.get_ring_rank(RINGS.EARTH)
        return 0

    def get_armor_rd(self):
        return self.armor.rd if self.armor else 0
        
    def get_full_rd(self):
        return self.get_armor_rd() + self.get_base_rd()

    def get_armor_name(self):
        if self.armor is not None:
            return self.armor.name
        else:
            return 'No Armor'
            
    def get_armor_desc(self):
        if self.armor is not None:
            return self.armor.desc
        else:
            return ''      

    def get_cur_tn(self):
        return self.get_base_tn() + self.get_armor_tn()

    def get_health_rank(self, idx):
        if idx == 0:
            return self.get_ring_rank(RINGS.EARTH) * 5 + self.get_health_rank_mod()
        return self.get_ring_rank(RINGS.EARTH) * self.health_multiplier + self.get_health_rank_mod()
        
    def get_health_rank_mod(self):
        if self.has_rule('daidoji_bushi_1'):
            return max(1, int(self.get_honor()-4))
        return 0

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

    def get_pending_wc_emphs(self):
        return self.step_2.pending_wc_emph

    def get_pending_wc_spells(self):
        return self.step_2.pending_wc_spell

    def get_school_skills(self):
        school_ = self.get_school(0)
        if school_ is None: return []
        return [ int(x) for x in school_.skills.keys() ]

    def get_school_skill_rank(self, uuid):
        s_id = str(uuid)
        school_ = self.get_school(0)
        if school_ is None or s_id not in school_.skills: return 0        
        return school_.skills[s_id]

    def get_skills(self, school = True):
        l = []
        if school:
            l = self.get_school_skills()
        for adv in self.advans:
            if adv.type != 'skill' or \
              adv.skill in self.get_school_skills() or \
              adv.skill in l:
                continue
            l.append(adv.skill)
        return l

    def get_skill_emphases(self, skill_id):
        emph = []
        s_id = str(skill_id)        
        # search school skills
        school_ = self.get_school(0)        
        if school_ is not None and s_id in school_.emph:
            emph += school_.emph[s_id]
        for adv in self.advans:
            if adv.type != 'emph' or adv.text in emph:
                continue
            if adv.skill == skill_id:
                emph.append(adv.text)
        return emph

    def get_techs(self):                
        ls = []
        for s in self.schools:
            ls += s.techs
        if self.step_2.school_tech is not None and \
           self.step_2.school_tech not in ls:
               ls.insert(0, self.step_2.school_tech)
        return ls

    def get_spells(self):
        ls = []
        for s in self.schools:
            ls += s.spells
        return ls
        
    def get_memorized_spells(self):
        for adv in self.advans:
            if adv.type != 'memo_spell':
                continue
            yield adv.spell
            
    def get_perks(self):
        for adv in self.advans:
            if adv.type != 'perk':
                continue
            yield adv.perk

    def get_merits(self):
        for adv in self.advans:
            if adv.type != 'perk' or adv.cost < 0:
                continue
            yield adv

    def get_flaws(self):
        for adv in self.advans:
            if adv.type != 'perk' or adv.cost > 0:
                continue
            yield adv
            
    def get_kata(self):
        for adv in self.advans:
            if adv.type != 'kata':
                continue
            yield adv

    def get_kiho(self):
        for adv in self.advans:
            if adv.type != 'kiho':
                continue
            yield adv
            
    def has_kata(self, kata_id):
        for adv in self.advans:
            if adv.type == 'kata' and kata_id == adv.kata:
                return True
        return False
        
    def has_tag(self, tag):
        school_tags = []
        for s in self.schools:
            school_tags += s.tags
        return tag in self.tags or \
               self.step_1.has_tag(tag) or \
               tag in school_tags

    def has_rule(self, rule):
        school_rules = []
        for s in self.schools:
            school_rules += s.tech_rules
        
        for adv in self.advans:
            if hasattr(adv, 'rule') and adv.rule == rule:
                return True
        return rule in school_rules
        
    def cnt_rule(self, rule):
        school_rules = []
        for s in self.schools:
            school_rules += s.tech_rules
        count = 0
        for adv in (self.advans+school_rules):
            if hasattr(adv, 'rule') and adv.rule == rule:
                count += 1
        return count
        
    def can_get_other_techs(self):
        #if not self.has_tag('bushi') and \
        #   not self.has_tag('monk') and \
        #   not self.has_tag('courtier') and \
        #   not self.has_tag('ninja'):
        #   return False

        return len(self.get_techs()) < self.get_insight_rank()

    def get_school_spells_qty(self):
        return self.step_2.start_spell_count

    def can_get_other_spells(self):
        if not self.has_tag('shugenja'):
            return

        # must count also the school spells
        target_spells = self.get_school_spells_qty() + (self.get_insight_rank()-1) * self.spells_per_rank
        return len(self.get_spells()) < target_spells

    def get_how_many_spell_i_miss(self):
        if not self.has_tag('shugenja'):
            return 0

        # must count also the school spells
        target_spells = self.get_school_spells_qty() + (self.get_insight_rank()-1) * self.spells_per_rank
        return target_spells - len(self.get_spells())

    def pop_spells(self, count):
        print 'pop %d spells' % count
        spells_count = len(self.get_spells())
        print 'i got %d spells' % spells_count
        if count >= spells_count:            
            for s in self.schools:
                print 'resetting school spells'
                s.spells = []
        else:
            for s in reversed(self.schools):
                if s.school_id == self.get_school_id(0) and s.school_rank == 1:
                    break
                while count > 0 and len(s.spells) > 0:
                    s.spells.pop()
                    count -= 1
                if count <= 0:
                    break
            print 'now i got %s spells' % len(self.get_spells())
            
    def remove_spell(self, spell_id):
        for s in self.schools:
            try:
                s.spells.remove(spell_id)
            except:
                pass
        
    def get_weapons(self):
        return self.weapons
        
    def get_modifiers(self, filter_type = None):
        if not filter_type:
            return self.modifiers
        return filter(lambda x: x.type == filter_type, self.modifiers)

    def add_school_skill(self, skill_uid, skill_rank, emph = None):
        s_id = str(skill_uid)
        school_ = self.get_school(0)
        if school_ is None:
            return
            
        if s_id in school_.skills:
            school_.skills[s_id] += skill_rank
        else:
            school_.skills[s_id] = skill_rank
        if emph is not None:
            if s_id not in school_.emph:
                school_.emph[s_id] = []

            if emph.startswith('*'):
                self.add_pending_wc_emph( s_id )
            else:
                school_.emph[s_id].append(emph)

        self.unsaved = True

    def add_pending_wc_skill(self, wc, skill_rank):
        self.step_2.pending_wc.append( (wc, skill_rank) )
        self.unsaved = True

    def add_pending_wc_spell(self, wc):
        self.step_2.pending_wc_spell.append( wc )
        self.unsaved = True

    def add_pending_wc_emph(self, wc):
        self.step_2.pending_wc_emph.append( wc )
        self.unsaved = True

    def clear_pending_wc_skills(self):
        self.step_2.pending_wc = []
        self.unsaved = True

    def clear_pending_wc_spells(self):
        self.step_2.pending_wc_spell = []
        self.unsaved = True

    def clear_pending_wc_emphs(self):
        self.step_2.pending_wc_emph = []
        self.unsaved = True

    def add_weapon(self, item):
        self.weapons.append( item )
        
    def add_modifier(self, item):
        self.modifiers.append(item)

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
        if self.get_school_id() == school_id:
            return           
        self.step_2  = BasePcModel()
        self.schools = []
        self.unsaved = True
        self.school  = school_id
        self.clear_pending_wc_skills()
        self.clear_pending_wc_spells()
        self.clear_pending_wc_emphs ()                
        if school_id == 0:
            return
            
        self.schools = [ CharacterSchool(school_id) ]
        self.step_2.honor = honor

        for t in tags:
            self.get_school().add_tag(t)

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

    def set_free_school_tech(self, tech_uuid, rule = None):
        school_ = self.get_school(0)
        if school_ is None:
            return
        self.step_2.school_tech = tech_uuid
        school_.techs.append(tech_uuid)
        #if rule is not None:
        school_.tech_rules.append(rule or 'N/A')

    def add_tech(self, tech_uuid, rule = None):
        school_ = self.get_school(0)
        if school_ is None:
            return
        #print 'add tech %s, rule %s' % ( repr(tech_uuid), rule )
        if tech_uuid not in self.get_techs():
            school_.techs.append(tech_uuid)
        if rule is not None and not self.has_rule(rule):
            school_.tech_rules.append(rule)
        self.unsaved = True

    def set_school_spells_qty(self, qty):
        self.step_2.start_spell_count = qty

    def add_free_spell(self, spell_uuid):
        school_ = self.get_school(0)
        if school_ is None or spell_uuid in self.get_spells():
            return 
        school_.spells.append(spell_uuid)
        self.unsaved = True

    def add_spell(self, spell_uuid):
        school_ = self.get_school()
        if school_ is None or spell_uuid in self.get_spells():
            return 
        school_.spells.append(spell_uuid)
        self.unsaved = True

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
        self.status = value - self.step_0.status
        self.unsaved = True

    def set_taint(self, value):
        self.taint = value
        self.unsaved = True
        
    def set_affinity(self, value):
        self.step_2.affinity = value
        
    def set_deficiency(self, value):
        self.step_2.deficiency = value

    def add_advancement(self, adv):
        self.advans.append(adv)
        self.unsaved = True

    def pop_advancement(self):
        self.advans.pop()
        self.unsaved = True

    def toggle_unlock_schools(self):
        self.unlock_schools = not self.unlock_schools
        self.unsaved = True
        
    def recalc_ranks(self):
        insight_ = self.get_insight_rank()
        print 'I got %d schools' % len(self.schools)
        for s in self.schools:
            print 'school %d, rank %d' % ( s.school_id, s.school_rank )
        tot_rank = sum( [x.school_rank for x in self.schools] )
        
        print 'insight rank: %d, tot_rank: %d' % ( insight_, tot_rank ) 
        if tot_rank > insight_:
            diff_ = tot_rank - insight_
            print 'diff ranks: %d' % diff_
            for s in reversed(self.schools):
                while diff_ > 0 and s.school_rank > 0:
                    if s.school_id == self.get_school_id(0) and s.school_rank == 1:
                        break
                    print 'school %d rank from %d to %d' % (s.school_id, s.school_rank, s.school_rank-1)

                    if len(s.techs) > 0:
                        s.techs.pop()
                    if len(s.tech_rules) > 0:
                        s.tech_rules.pop()
                    
                    #print s.techs
                    #print s.tech_rules
                    
                    self.pop_spells(self.spells_per_rank)
                    
                    diff_         -= 1
                    s.school_rank -= 1

                if diff_ <= 0:
                    return
                    
        elif tot_rank < insight_:
            if self.get_school() is not None:
                self.get_school().school_rank += (insight_-tot_rank)                
                print 'school %d is now rank %d' % (self.get_school_id(), self.get_school_rank())
                
    def set_insight_calc_method(self, func):
        self.insight_calculation = func
                
### LOAD AND SAVE METHODS ###

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

        def _load_obj(in_dict, out_obj):
            for k in in_dict.iterkeys():
                out_obj.__dict__[k] = in_dict[k]

        fp = open(file_, 'rt')
        if fp:
            obj = json.load(fp)
            fp.close()

            _load_obj(deepcopy(obj), self)

            self.step_0 = BasePcModel()
            self.step_1 = BasePcModel()
            self.step_2 = BasePcModel()

            _load_obj(deepcopy(obj['step_0']), self.step_0)
            _load_obj(deepcopy(obj['step_1']), self.step_1)
            _load_obj(deepcopy(obj['step_2']), self.step_2)

            # schools
            self.schools = []
            if 'schools' in obj:
                for s in obj['schools']:
                    item = CharacterSchool()
                    _load_obj(deepcopy(s), item)
                    self.schools.append(item)
            
            self.advans = []
            for ad in obj['advans']:
                a = adv.Advancement(None, None)
                _load_obj(deepcopy(ad), a)
                self.advans.append(a)

            # armor
            self.armor = outfit.ArmorOutfit()
            if obj['armor'] is not None:
                _load_obj(deepcopy(obj['armor']), self.armor)

            self.weapons = []
            if 'weapons' in obj:
                # weapons
                for w in obj['weapons']:
                    item = outfit.WeaponOutfit()
                    _load_obj(deepcopy(w), item)
                    self.add_weapon(item)
                    
            self.modifiers = []
            if 'modifiers' in obj:
                for m in obj['modifiers']:
                    item = modifiers.ModifierModel()
                    _load_obj(deepcopy(m), item)
                    self.add_modifier(item)
                    
            self.unsaved  = False
            return True
        return False
