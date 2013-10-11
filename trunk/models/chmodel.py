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
import dal.school
import json
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
    else:
        print("unknown trait_id: {0}".format(attrib_id))
        return None

def get_ring_id_from_attrib_id(attrib_id):
    if attrib_id >= ATTRIBS.STAMINA and attrib_id <= ATTRIBS.INTELLIGENCE:
        return attrib_id // 2
    return -1

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
        self.infamy             = 0.0
        self.status             = 0.0
        self.taint              = 0.0

        self.start_spell_count = 0

    def load_default(self):
        self.void    = 2
        self.attribs = [2, 2, 2, 2, 2, 2, 2, 2]
        self.rank    = 1
        self.status  = 1.0
        self.glory   = 1.0

    def add_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)

    def has_tag(self, tag):
        return tag in self.tags

    def del_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)

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
        self.outfit      = []
        self.affinity    = None
        self.deficiency  = None

        # alternate path
        self.is_path     = False
        self.path_rank   = 0

    def add_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)

    def has_tag(self, tag):
        return tag in self.tags

    def del_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)

    def clear_tags(self):
        self.tags = []

    def __str__(self):
        return self.school_id

class AdvancedPcModel(BasePcModel):

    observer = None

    def __init__(self):
        super(AdvancedPcModel, self).__init__()

        # clan selection
        self.step_0 = BasePcModel()
        # family selection
        self.step_1 = BasePcModel()
        # school selection
        self.step_2 = BasePcModel()

        self._unsaved = False
        self._version = '0.0'

        self._name      = ''
        self._clan      = None
        self._family    = None

        self._advans    = []

        self._armor      = None
        self._weapons    = []
        self._schools    = []

        self._mastery_abilities = []
        self._current_school_id = ''

        self._attrib_costs = [4, 4, 4, 4, 4, 4, 4, 4]
        self._void_cost    = 6
        self._health_multiplier = 2
        self._spells_per_rank = 3
        self._pending_spells_count = 0;
        self._exp_limit = 40
        self._wounds = 0
        self._mod_init = (0, 0)
        self._void_points = self.get_void_rank()
        self._unlock_schools = False
        self._extra_notes = ''
        self._insight_calculation = None
        self._free_kiho_count = 0

        self._modifiers  = []
        self._properties = {}


    # DEBUG
    def set_observer(self, observer):
        self.observer = observer

        from debug import observable_list
        self._advans            = observable_list('advancements'     , self._advans           , observer)
        self._weapons           = observable_list('weapons'          , self._weapons          , observer)
        self._schools           = observable_list('schools'          , self._schools          , observer)
        self._mastery_abilities = observable_list('mastery_abilities', self._mastery_abilities, observer)
        self._modifiers         = observable_list('modifiers'        , self._modifiers        , observer)

    # PROPERTIES
    def has_property(self, name):
        return name not in self.properties

    def get_property(self, name, default = ''):
        if name not in self.properties:
            self.properties[name] = default
        return self.properties[name]

    def set_property(self, name, value):
        self.properties[name] = value
        self.set_dirty()

    def notify_change(self, property_name, old_value, new_value, sender):
        if old_value != new_value and self.observer is not None:
            self.observer.property_changed(property_name, old_value, new_value)

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self.notify_change('version', self._version, value, self)
        self._version = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self.notify_change('name', self._name, value, self)
        self._name = value
        self.set_dirty()

    @property
    def clan(self):
        return self._clan

    @clan.setter
    def clan(self, value):
        self.notify_change('clan', self._clan, value, self)
        self._clan = value
        # brotherhood monks get glory penalty ( NOT clan monks )
        if value == 'monks':
            self.step_0.glory = 0.0
        self.set_dirty()

    @property
    def family(self):
        return self._family

    @family.setter
    def family(self, value):
        self.notify_change('family', self._family, value, self)
        self._family = value
        self.set_dirty()

    @property
    def armor(self):
        return self._armor

    @armor.setter
    def armor(self, value):
        self.notify_change('armor', self._armor, value, self)
        self._armor = value
        self.set_dirty()

    @property
    def current_school_id(self):
        return self._current_school_id

    @current_school_id.setter
    def current_school_id(self, value):
        self.notify_change('current_school_id', self._current_school_id, value, self)
        self._current_school_id = value
        self.set_dirty()

    @property
    def void_cost(self):
        return self._void_cost

    @void_cost.setter
    def void_cost(self, value):
        self.notify_change('void_cost', self._void_cost, value, self)
        self._void_cost = value
        self.set_dirty()

    @property
    def health_multiplier(self):
        return self._health_multiplier

    @health_multiplier.setter
    def health_multiplier(self, value):
        self.notify_change('health_multiplier', self._health_multiplier, value, self)
        self._health_multiplier = value
        self.set_dirty()

    @property
    def spells_per_rank(self):
        return self._spells_per_rank

    @spells_per_rank.setter
    def spells_per_rank(self, value):
        self.notify_change('spells_per_rank', self._spells_per_rank, value, self)
        self._spells_per_rank = value
        self.set_dirty()

    @property
    def pending_spells_count(self):
        return self._pending_spells_count

    @pending_spells_count.setter
    def pending_spells_count(self, value):
        self.notify_change('pending_spells_count', self._pending_spells_count, value, self)
        self._pending_spells_count = value
        self.set_dirty()

    @property
    def exp_limit(self):
        return self._exp_limit

    @exp_limit.setter
    def exp_limit(self, value):
        self.notify_change('exp_limit', self._exp_limit, value, self)
        self._exp_limit = value
        self.set_dirty()

    @property
    def wounds(self):
        return self._wounds

    @wounds.setter
    def wounds(self, value):
        self.notify_change('wounds', self._wounds, value, self)
        self._wounds = value
        self.set_dirty()

    @property
    def void_points(self):
        return self._void_points

    @void_points.setter
    def void_points(self, value):
        self.notify_change('void_points', self._void_points, value, self)
        self._void_points = value
        self.set_dirty()

    @property
    def unlock_schools(self):
        return self._unlock_schools

    @unlock_schools.setter
    def unlock_schools(self, value):
        self.notify_change('unlock_schools', self._unlock_schools, value, self)
        self._unlock_schools = value
        self.set_dirty()

    @property
    def extra_notes(self):
        return self._extra_notes

    @extra_notes.setter
    def extra_notes(self, value):
        self.notify_change('extra_notes', self._extra_notes, value, self)
        self._extra_notes = value
        self.set_dirty()

    @property
    def insight_calculation(self):
        return self._insight_calculation

    @insight_calculation.setter
    def insight_calculation(self, value):
        self.notify_change('insight_calculation', self._insight_calculation, value, self)
        self._insight_calculation = value

    @property
    def can_advance_rank(self):
        return (
            #self.get_insight_rank() > 1 and
            len ([x for x in self.advans if x.type == 'rank' and x.insight_rank == self.get_insight_rank()]) == 0 )

    @property
    def can_get_another_tech(self):
        rank_adv = self.get_current_rank_advancement()
        return rank_adv and rank_adv.tech_id == None

    @property
    def free_kiho_count(self):
        return self._free_kiho_count

    @free_kiho_count.setter
    def free_kiho_count(self, value):
        self.notify_change('free_kiho_count', self._free_kiho_count, value, self)
        self._free_kiho_count = value
        self.set_dirty()

    ### lists are not settable ###
    @property
    def advans(self):
        return self._advans

    @property
    def weapons(self):
        return self._weapons

    @property
    def schools(self):
        return self._schools

    @property
    def mastery_abilities(self):
        return self._mastery_abilities

    @property
    def attrib_costs(self):
        return self._attrib_costs

    @property
    def properties(self):
        return self._properties

    @property
    def modifiers(self):
        return self._modifiers

    # METHODS

    def load_default(self):
        self.step_0.load_default()

    def is_dirty(self):
        return self._unsaved

    def set_dirty(self):
        self.notify_change('unsaved', self._unsaved, True, self)
        self._unsaved = True

    def clean_dirty(self):
        self.notify_change('unsaved', self._unsaved, False, self)
        self._unsaved = False

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

        advancements = [x for x in self.advans if x.type == 'attrib' and x.attrib == attrib]
        d += len(advancements)

        return d

    def get_mod_attrib_rank(self, attrib):
        a = self.step_0.attribs[attrib]
        b = self.step_1.attribs[attrib]
        c = self.step_2.attribs[attrib]

        d = a+b+c

        advancements = [x for x in self.advans if x.type == 'attrib' and x.attrib == attrib]
        d += len(advancements)

        weakness_flaw = 'weak_%s' % attrib_name_from_id(attrib)
        if self.has_rule(weakness_flaw):
            return d-1
        return d

    def get_void_rank(self):
        v = self.step_0.void + self.step_1.void + self.step_2.void

        advancements = [x for x in self.advans if x.type == 'void']
        v += len(advancements)

        return v

    def get_current_school(self):
        school = [x for x in self.schools if x.school_id == self.current_school_id]
        if len(school):
            return school[0]
        return None

    # ???
    def get_school(self, index = -1):
        if len(self.schools) == 0 or index >= len(self.schools):
            return None
        if index < 0:
            return self.get_current_school()
        return self.schools[index]

    # ???
    def get_school_id(self, index = -1):
        try:
            return self.get_school(index).school_id
        except Exception as e:
            return None

    def get_school_rank(self, school_id = None):
        if not school_id:
            school_id = self.current_school_id
        try:
            return max ( [x.school_rank for x in self.get_rank_advancements() if x.school_id == school_id] )
        except:
            return 1

    def get_skill_rank(self, uuid):
        if uuid in self.get_school_skills():
            rank = self.get_school_skill_rank(uuid)
        else:
            rank = 0

        rank += len([x for x in self.advans if x.type == 'skill' and x.skill == uuid])

        return rank

### GLORY ###
    def get_honor(self):
        return self.step_0.honor + self.step_1.honor + self.step_2.honor + self.honor

    def get_base_glory(self):
        #if self.has_tag('monk'):
        #    return self.glory
        return self.step_0.glory + self.step_1.glory + self.step_2.glory + self.glory

    def get_glory(self):
        if self.has_rule('fame'):
            return self.get_base_glory() + 1
        return self.get_base_glory()
### ----- ###

### STATUS ###
    def get_status(self):
        value = self.step_0.status + self.step_1.status + self.step_2.status + self.status
        if self.has_rule('social_disadvantage'):
            value -= self.step_0.status
        return value
### ------ ###

### MAGIC AFFINITY ###
    def get_affinity(self):
        return set(
            [x.affinity for x in self.get_rank_advancements() if x.affinity is not None])
        #return [ x.affinity for x in self.schools if x.affinity is not None ]

    def get_deficiency(self):
        return set(
            [x.deficiency for x in self.get_rank_advancements() if x.deficiency is not None])

    def set_affinity(self, value): pass
        #self.get_school().affinity = value
        #self.set_dirty()

    def set_deficiency(self, value): pass
        #self.get_school().deficiency = value
        #self.set_dirty()
### -------------- ###

### INSIGHT ###
    def get_insight(self):
        if self.insight_calculation:
            return self.insight_calculation(self)
        return rules.insight_calculation_1(self)

    def get_insight_rank(self):
        value = self.get_insight()

        if value > 349:
            return int((value - 349)/25 + 10)
        if value > 324: return 9
        if value > 299: return 8
        if value > 274: return 7
        if value > 249: return 6
        if value > 224: return 5
        if value > 199: return 4
        if value > 174: return 3
        if value > 149: return 2
        return 1

### ------- ###


### ARMOR ###
    def get_base_tn(self):
        # reflexes * 5 + 5
        return self.get_mod_attrib_rank(ATTRIBS.REFLEXES)*5+5

    def get_armor_tn(self):
        if self.armor is not None:
            return self.armor.tn
        else:
            return 0

    def get_base_rd(self):
        if self.has_rule('crab_the_mountain_does_not_move'):
            return self.get_ring_rank(RINGS.EARTH)
        return 0

    def get_armor_rd(self):
        return self.armor.rd if self.armor else 0

    def get_full_rd(self):
        return self.get_armor_rd() + self.get_base_rd() + self.get_armor_rd_mod()

    def get_armor_tn_mod(self):
        return sum( x.value[2] for x in self.get_modifiers('artn') if x.active and len(x.value) > 2)

    def get_armor_rd_mod(self):
        return sum( x.value[2] for x in self.get_modifiers('arrd') if x.active and len(x.value) > 2)

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
        return self.get_base_tn() + self.get_armor_tn() + self.get_armor_tn_mod()
### ----- ###


### HEALTH ###
    def get_health_rank(self, idx):
        if idx == 0:
            return self.get_ring_rank(RINGS.EARTH) * 5 + self.get_health_rank_mod()
        return self.get_ring_rank(RINGS.EARTH) * self.health_multiplier + self.get_health_rank_mod()

    def get_health_rank_mod(self):
        mod = 0
        if self.has_rule('crane_the_force_of_honor'):
            mod = max(1, int(self.get_honor()-4))

        for x in self.get_modifiers('hrnk'):
            if x.active and len(x.value) > 2:
                mod += x.value[2]
        return mod

    def get_max_wounds(self):
        max_ = 0
        for i in xrange(0, 8):
            max_ += self.get_health_rank(i)
        return max_
### ------ ###


### INITIATIVE ###
    def get_base_initiative(self):
        return (self.get_insight_rank() +
                self.get_mod_attrib_rank(ATTRIBS.REFLEXES),
                self.get_mod_attrib_rank(ATTRIBS.REFLEXES))

    def get_init_modifiers (self):
        r, k, b = 0, 0, 0
        mods = [x for x in
                self.get_modifiers('anyr') + self.get_modifiers('init')
                if x.active]
        for m in mods:
            r += m.value[0]
            k += m.value[1]
            if len(m.value) > 2:
                b += m.value[2]
        return r,k,b

    def get_tot_initiative (self):
        r, k = self.get_base_initiative()
        b    = 0
        r1, k1, b1 = self.get_init_modifiers ()
        return r+r1, k+k1, b+b1
### ---------- ###

### EXPERIENCE ###
    def get_px(self):
        return sum( [x.cost for x in self.advans ] )

    def get_attrib_cost(self, idx):
        return self.attrib_costs[idx]
### ---------- ###

### WILDCARDS ###
    def get_pending_wc_skills(self):
        return self.step_2.pending_wc

    def get_pending_wc_emphs(self):
        return self.step_2.pending_wc_emph

    def get_pending_wc_spells(self):
        return self.step_2.pending_wc_spell

    def add_pending_wc_skill(self, wc):
        self.step_2.pending_wc.append( wc )
        self.set_dirty()

    def add_pending_wc_spell(self, wc):
        self.step_2.pending_wc_spell.append( wc )
        self.set_dirty()

    def add_pending_wc_emph(self, wc):
        self.step_2.pending_wc_emph.append( wc )
        self.set_dirty()

    def clear_pending_wc_skills(self):
        self.step_2.pending_wc = []
        self.set_dirty()

    def clear_pending_wc_spells(self):
        self.step_2.pending_wc_spell = []
        self.set_dirty()

    def clear_pending_wc_emphs(self):
        self.step_2.pending_wc_emph = []
        self.set_dirty()
### --------- ###

### SKILLS ###
    def get_school_skills_dict(self):
        skills = {}
        for sl in [x.skills for x in self.get_rank_advancements()]:
            skills += sl
        return skills

    def get_school_skills(self):
        return self.get_school_skills_dict().keys()
        #school_ = self.get_school(0)
        #if school_ is None: return []
        #return school_.skills.keys()

    def get_school_skill_rank(self, uuid):
        sd = self.get_school_skills_dict()
        if uuid not in sd: return 0
        return sd[uuid]

    def get_skills(self, school = True):
        l = []
        if school:
            l = self.get_school_skills()
        for obj in self.advans:
            if (obj.type != 'skill' or
                obj.skill in self.get_school_skills() or
                obj.skill in l): continue
            l.append(obj.skill)
        return l

    def get_skill_emphases(self, skill_id):
        emph = []
        s_id = str(skill_id)
        # search school skills
        school_ = self.get_school(0)
        if school_ is not None and s_id in school_.emph:
            emph += school_.emph[s_id]
        for obj in self.advans:
            if obj.type != 'emph' or obj.text in emph:
                continue
            if obj.skill == skill_id:
                emph.append(obj.text)
        return emph

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
        self.set_dirty()
### ------ ###

### TECHNIQUES ###
    def get_techs(self):
        ls = []
        for s in self.schools:
            ls += s.techs

        for s in self.get_rank_advancements():
            tech_replacement = self.get_tech_replacement(s.school_id, s.tech_id)
            if tech_replacement:
                ls.append(tech_replacement)
            elif s.tech_id:
                ls.append(s.tech_id)

        return ls

    def get_tech_replacement(self, school_id, tech_id):
        for s in [x for x in self.advans if x.type == 'alternate_path']:
            if (s.original_school_id == school_id and
                s.original_tech_id   == tech_id ):
                return s.tech_id
        return None

    def add_tech(self, tech_uuid, rule = None):
        school_ = self.get_school()
        if school_ is None:
            return

        if tech_uuid not in self.get_techs():
            school_.techs.append(tech_uuid)
            self.set_dirty()
        if rule is not None and not self.has_rule(rule):
            school_.tech_rules.append(rule)
            self.set_dirty()

    def remove_tech(self, tech_id):
        for s in self.schools:
            if tech_id in s.techs:
                s.techs.remove(tech_id)
                self.set_dirty()

### ---------- ###

### SPELLS ###
    def get_spells(self):
        ls = []
        for s in self.schools:
            ls += s.spells
        for a in self.get_rank_advancements():
            ls += a.spells
        for e in self.get_extra_spells():
            ls.append(e)
        return ls

    def get_extra_spells(self):
        for obj in self.advans:
            if obj.type == 'spell':
                yield obj.spell

    def get_memorized_spells(self):
        for obj in self.advans:
            if obj.type == 'memo_spell':
                yield obj.spell

    def can_get_other_spells(self):
        if not self.has_tag('shugenja'):
            return False
        return self.pending_spells_count > 0 or len(self.get_pending_wc_spells())

    def get_how_many_spell_i_miss(self):
        if not self.has_tag('shugenja'):
            return 0
        return self.pending_spells_count

    def remove_spell(self, spell_id):
        for s in self.schools:
            try:
                s.spells.remove(spell_id)
            except:
                pass
        self.set_dirty()

    def add_free_spell(self, spell_uuid):
        school_ = self.get_school(0)
        if school_ is None or spell_uuid in self.get_spells():
            return
        school_.spells.append(spell_uuid)
        self.set_dirty()

    def add_spell(self, spell_uuid):
        if spell_uuid in self.get_spells():
            return
        cur_rank_adv = self.get_current_rank_advancement()
        if cur_rank_adv:
            cur_rank_adv.spells.append(spell_uuid)
        else:
            self.add_free_spell(spell_uuid)
        self.set_dirty()

### ------ ###


### ADVANTAGES ###
    def get_perks(self):
        for obj in self.advans:
            if obj.type != 'perk':
                continue
            yield obj.perk

    def get_merits(self):
        for obj in self.advans:
            if obj.type != 'perk' or obj.cost < 0 or obj.tag == 'flaw': # cannot use != 'merit' for backward compatibility
                continue
            yield obj

    def get_flaws(self):
        for obj in self.advans:
            if obj.type != 'perk' or obj.cost > 0 or obj.tag == 'merit': # cannot use != 'flaw' for backward compatibility
                continue
            yield obj
### ---------- ###


### KATA / KIHO ###
    def get_kata(self):
        return [x.kata for x in self.advans if x.type == 'kata']

    def get_kiho(self):
        kl  = [x.kiho for x in self.advans if x.type == 'kiho']
        for a in self.get_rank_advancements():
            kl += a.kiho
        return kl

    def has_kiho(self, kiho_id):
        return kiho_id in self.get_kiho()

    def has_kata(self, kata_id):
        return kata_id in self.get_kata()

### ----------- ###

### TAGS AND RULES ###
    def has_tag(self, tag):
        school_tags = []
        for s in self.schools:
            school_tags += s.tags
        return (tag in self.tags or
                self.step_1.has_tag(tag) or
                tag in school_tags)

    def has_rule(self, rule):
        school_rules = []
        for s in self.schools:
            school_rules += s.tech_rules

        for obj in self.advans:
            if hasattr(obj, 'rule') and obj.rule == rule:
                return True
        return rule in school_rules

    def cnt_rule(self, rule):
        school_rules = []
        for s in self.schools:
            school_rules += s.tech_rules
        count = 0
        for obj in (self.advans+school_rules):
            if hasattr(obj, 'rule') and obj.rule == rule:
                count += 1
        return count
### -------------- ###

### OUTFIT ###
    def get_school_outfit(self):
        if self.get_school(0):
            return self.get_school(0).outfit
        return []

    def add_weapon(self, item):
        self.weapons.append( item )
        self.set_dirty()
### ------ ###

### MODIFIERS ###
    def get_modifiers(self, filter_type = None):
        if not filter_type:
            return self.modifiers
        return filter(lambda x: x.type == filter_type, self.modifiers)

    def add_modifier(self, item):
        self.modifiers.append(item)
        self.set_dirty()
### --------- ###


### FAMILY ###
    def set_family(self, family_id = 0, perk = None, perkval = 1, tags = []):
        if self.family == family_id:
            return
        self.step_1  = BasePcModel()
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
### ------ ###

### SCHOOL ###
    def set_school(self, school_id = 0, perk = None, perkval = 1,
                         honor = 0.0, tags = []):
        if self.current_school_id == school_id:
            return

        self.step_2  = BasePcModel()

        self._schools = []

        self.clear_pending_wc_skills()
        self.clear_pending_wc_spells()
        self.clear_pending_wc_emphs ()
        if school_id == 0:
            return

        self._schools = [ CharacterSchool(school_id) ]

        self.step_2.honor = honor

        self.current_school_id = school_id

        for t in tags:
            self.get_school().add_tag(t)

        # reset money
        self.set_property('money', (0,0,0))

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
        #self.step_2.school_tech = tech_uuid
        school_.techs.append(tech_uuid)
        #if rule is not None:
        school_.tech_rules.append(rule or 'N/A')
        self.set_dirty()

    def set_school_outfit(self, outfit, money):
        self.get_school(0).outfit = outfit
        self.set_property('money', money)
        self.set_dirty()

    def set_school_spells_qty(self, qty):
        self.step_2.start_spell_count = qty
        self.set_dirty()

### ------ ###

### RINGS - ATTRIBUTES - TRAITS ###

    def set_honor(self, value):
        base_honor = self.step_0.honor + self.step_1.honor + self.step_2.honor
        self.honor = value - base_honor
        self.set_dirty()

    def set_glory(self, value):
        base_glory = self.step_0.glory + self.step_1.glory + self.step_2.glory
        self.glory = value - base_glory
        self.set_dirty()

    def set_status(self, value):
        base_status = self.step_0.status + self.step_1.status + self.step_2.status
        self.status = value - base_status
        self.set_dirty()
### --------------------------- ###

### ADVANCEMENT ###
    def add_advancement(self, adv):
        self.advans.append(adv)
        self.set_dirty()

    def pop_advancement(self):
        self.advans.pop()
        self.set_dirty()

    def get_rank_advancements(self):
        return [x for x in self.advans if x.type == 'rank']

    def get_current_rank_advancement(self):
        l = [x for x in self.advans if x.type == 'rank' and not x.completed]
        if len(l) > 0: return l[0]
        return None
### ----------- ###

    def toggle_unlock_schools(self):
        self.unlock_schools = not self.unlock_schools
        self.set_dirty()

class CharacterLoader(object):

    SAVE_FILE_VERSION = "4.0"

    def __init__(self):
        self.old_save = False
        self.version  = None
        self.sdata    = {}
        self.pc       = AdvancedPcModel()

    def model(self):
        return self.pc

    def load_from_file(self, file_):

        obj = None
        try:
            with open(file_, 'rt') as fp:
                if not fp: return False
                obj = json.load(fp)
        except IOError as e:
            print('cannot read file {}, {}'.format(file_, e))

        if not obj: return False

        res = self.load_from_string(obj)
        if not res: return False


        if self.old_save:
            self.save_to_file(self.pc, file_)

        return True

    def load_from_string(self, obj):

        try:
            self.load_step_0( obj )
            self.load_step_1( obj )
            self.load_step_2( obj )

            self.load_character_info( obj )
            self.load_game_info     ( obj )
            self.load_schools       ( obj )
            self.load_advancements  ( obj )
            self.load_outfit        ( obj )
            self.load_modifiers     ( obj )
        except Exception as e:
            print('load from string error: {0}'.format(e))

        try:
            if self.pc.get_current_school() is None and len(self.pc.schools) > 0:
                print('missing current school. old save?')
                self.pc.current_school_id = self.pc.schools[-1].school_id
                self.old_save = True
        except:
            print('cannot recover current school')

        self.pc.clean_dirty()
        return True

    def _load_obj(self, in_dict, out_obj):
        for k in in_dict.iterkeys():
            out_obj.__dict__[k] = in_dict[k]

    def load_step_0( self, obj ):
        if 'step_0' not in obj:
            return

        # load attributes, void, status and glory

        source = obj['step_0']
        dest   = self.pc.step_0

        dest.void    = source['void']
        dest.glory   = source['glory']
        dest.status  = source['status']
        dest.attribs = deepcopy( source['attribs'] )

    def load_step_1(self, obj):
        if 'step_1' not in obj:
            return

        # load attributes, void, and tags

        source = obj['step_1']
        dest   = self.pc.step_1

        dest.void    = source['void']
        dest.attribs = deepcopy( source['attribs'] )
        dest.tags    = deepcopy( source['tags'] )

    def load_step_2(self, obj):
        if 'step_2' not in obj:
            return

        # load attributes, void, honor and other stuffs

        source = obj['step_2']
        dest   = self.pc.step_2

        dest.void    = source['void']
        dest.honor   = source['honor']
        dest.attribs = deepcopy( source['attribs'] )

        # pending wildcard object in step2
        dest.pending_wc = []
        if 'pending_wc' in source:
            for m in source['pending_wc']:
                item = dal.school.SchoolSkillWildcardSet()
                self._load_obj(deepcopy(m), item)
                for i in range(0, len(item.wildcards)):
                    s_item = dal.school.SchoolSkillWildcard()
                    self._load_obj(deepcopy(item.wildcards[i]), s_item)
                    item.wildcards[i] = s_item
                self.pc.add_pending_wc_skill(item)

        dest.pending_wc_emph  = deepcopy( source['pending_wc_emph' ] )
        dest.pending_wc_spell = deepcopy( source['pending_wc_spell'] )

    def load_character_info(self, obj):
        source = obj
        dest   = self.pc

        self.version = source['version']
        print('Savefile version {}'.format(self.version))

        if self.version != self.SAVE_FILE_VERSION:
            self.old_save = True

        dest.name    = source['name'   ]
        dest.clan    = source['clan'   ]
        dest.family  = source['family' ]

        dest.status  = round(source['status' ], 1)
        dest.glory   = round(source['glory'  ], 1)
        dest.taint   = round(source['taint'  ], 1)
        dest.infamy  = round(source['infamy' ], 1)
        dest.honor   = round(source['honor'  ], 1)

        dest.attribs = deepcopy( source['attribs'] )

        dest.extra_notes = source['extra_notes']
        dest._properties = deepcopy( source['properties'] )

    def load_game_info(self, obj):
        source = obj
        dest   = self.pc

        dest._attrib_costs = deepcopy( source['attrib_costs'] )
        dest._void_cost    = source['void_cost']

        dest.health_multiplier    = source['health_multiplier'   ]
        dest.spells_per_rank      = source['spells_per_rank'     ]
        dest.pending_spells_count = source['pending_spells_count']
        dest.exp_limit            = source['exp_limit']
        dest.wounds               = source['wounds']
        dest.void_points          = source['void_points']
        dest.unlock_schools       = source['unlock_schools']
        dest.free_kiho_count      = source['free_kiho_count']

    def load_schools(self, obj):
        dest = self.pc
        if 'current_school_id' in obj:
            dest.current_school_id = obj['current_school_id']
        if 'schools' not in obj: return
        source = obj['schools']
        for s in source:
            item = CharacterSchool()
            self._load_obj(deepcopy(s), item)
            dest.schools.append(item)

    def load_advancements(self, obj):
        dest = self.pc
        if 'advans' not in obj: return
        source = obj['advans']

        for ad in source:
            a = adv.Advancement(None, None)
            self._load_obj(deepcopy(ad), a)
            dest.advans.append(a)

    def load_outfit(self, obj):
        dest = self.pc
        if 'weapons' in obj:
            for w in obj['weapons']:
                item = outfit.WeaponOutfit()
                self._load_obj(deepcopy(w), item)
                dest.add_weapon(item)
        if 'armor' in obj:
            dest._armor = outfit.ArmorOutfit()
            self._load_obj(deepcopy(obj['armor']), dest._armor)

    def load_modifiers(self,obj):
        dest = self.pc
        if 'modifiers' not in obj: return
        source = obj['modifiers']

        for m in source:
            item = modifiers.ModifierModel()
            self._load_obj(deepcopy(m), item)
            dest.add_modifier(item)


    def save_to_file(self, pc, file_):

        self.pc = pc
        obj     = {}
        obj['version'] = self.SAVE_FILE_VERSION

        self.save_step_0( obj )
        self.save_step_1( obj )
        self.save_step_2( obj )

        self.save_character_info( obj )
        self.save_game_info     ( obj )
        self.save_schools       ( obj )
        self.save_advancements  ( obj )
        self.save_outfit        ( obj )
        self.save_modifiers     ( obj )

        print('saving to',file_)

        with open(file_, 'wt') as fp:
            json.dump(obj, fp, indent=4 )

        self.pc.clean_dirty()
        return True

    def save_step_0(self, obj):
        source = self.pc.step_0
        obj['step_0'] = source.__dict__

    def save_step_1(self, obj):
        source = self.pc.step_1
        obj['step_1'] = source.__dict__

    def save_step_2(self, obj):
        source = self.pc.step_2
        obj['step_2'] = source.__dict__

    def save_character_info(self, obj):
        source = self.pc

        obj['name'   ] = source.name
        obj['clan'   ] = source.clan
        obj['family' ] = source.family

        obj['status' ] = source.status
        obj['glory'  ] = source.glory
        obj['taint'  ] = source.taint
        obj['infamy' ] = source.infamy
        obj['honor'  ] = source.honor
        obj['attribs'] = source.attribs

        obj['extra_notes'] = source.extra_notes
        obj['properties' ] = source._properties

    def save_game_info(self, obj):
        source = self.pc

        obj['attrib_costs'        ] = source._attrib_costs
        obj['void_cost'           ] = source._void_cost
        obj['health_multiplier'   ] = source.health_multiplier
        obj['spells_per_rank'     ] = source.spells_per_rank
        obj['pending_spells_count'] = source.pending_spells_count
        obj['exp_limit'           ] = source.exp_limit
        obj['wounds'              ] = source.wounds
        obj['void_points'         ] = source.void_points
        obj['unlock_schools'      ] = source.unlock_schools
        obj['free_kiho_count'     ] = source.free_kiho_count

    def save_schools(self, obj):
        source = self.pc
        obj['current_school_id'] = source.current_school_id
        obj['schools']           = []
        for s in source._schools:
            obj['schools'].append( s.__dict__ )

    def save_advancements(self, obj):
        source = self.pc
        obj['advans'] = []
        for s in source._advans:
            obj['advans'].append( s.__dict__ )

    def save_outfit(self, obj):
        source = self.pc
        obj['weapons'] = []
        for s in source._weapons:
            obj['weapons'].append( s.__dict__ )

        if source.armor is not None:
            obj['armor'] = source.armor.__dict__

    def save_modifiers(self, obj):
        source = self.pc
        obj['modifiers'] = []
        for s in source._modifiers:
            obj['modifiers'].append( s.__dict__ )
