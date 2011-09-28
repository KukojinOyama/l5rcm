#!/usr/bin/python

import advances as adv
import json

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
        self.void       = 0
        self.attribs    = [0, 0, 0, 0, 0, 0, 0, 0]
        self.skills     = {}
        self.pending_wc = []
        self.honor      = 0.0
        self.glory      = 0.0
        self.status     = 0.0
        self.taint      = 0.0

    def load_default(self):
        self.void    = 2
        self.attribs = [2, 2, 2, 2, 2, 2, 2, 2]
        self.rank    = 1
        self.glory   = 2.0

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
        self.tag       = ''

        self.insight   = 0
        self.tags      = []
        self.advans    = []

        self.armor_tn  = 0
        self.armor_tag = ''
        self.armor_rd  = 0

        self.attrib_costs = [4, 4, 4, 4, 4, 4, 4, 4]
        self.void_cost    = 6
        self.health_multiplier = 2
        self.wounds = []

        self.mod_init = (0, 0)

        self.void_points = self.get_void_rank()

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
        if uuid in self.step_2.skills:
            rank = self.step_2.skills[uuid]
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
        return self.step_0.glory + self.glory

    def get_status(self):
        return self.status

    def get_taint(self):
        return self.taint

    def get_insight(self):
        n = 0
        for i in xrange(0, 5):
            n += self.get_ring_rank(i)*10
        for i in xrange(0, len(self.skills)):
            n += self.get_skill_rank(i)
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
        return self.armor_tn

    def get_armor_rd(self):
        return self.armor_rd

    def get_cur_tn(self):
        return self.get_base_tn() + self.get_armor_tn()

    def get_health_rank(self, idx):
        if idx == 0:
            return self.get_ring_rank(RINGS.EARTH) * 5
        return  self.get_ring_rank(RINGS.EARTH) * self.health_multiplier

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
        return self.step_2.skills.keys()

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

    def set_family(self, family_id = 0, perk = None, perkval = 1):
        if self.family == family_id:
            return
        self.step_1  = BasePcModel()
        self.unsaved = True
        self.family  = family_id
        if family_id == 0:
            return
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

    def add_school_skill(self, skill_uid, skill_rank):
        if skill_uid in self.step_2.skills:
            self.step_2.skills[skill_uid] += skill_rank
        else:
            self.step_2.skills[skill_uid] = skill_rank
        self.unsaved = True

    def add_pending_wc_skill(self, wc, skill_rank):
        self.step_2.pending_wc.append( (wc, skill_rank) )
        self.unsaved = True

    def clear_pending_wc_skills(self):
        self.step_2.pending_wc = []
        self.unsaved = True

    def set_school(self, school_id = 0, perk = None, perkval = 1,
                         honor = 0.0):
        if self.school == school_id:
            return
        self.step_2  = BasePcModel()
        self.unsaved = True
        self.school  = school_id
        self.clear_pending_wc_skills()
        if school_id == 0:
            return

        print 'set honor %f' % honor
        self.step_2.honor = honor

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

    def add_advancement(self, adv):
        self.advans.append(adv)
        self.unsaved = True

    def pop_advancement(self):
        self.advans.pop()
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

    def load_from(self, file):
        print "loading from %s" % file

        fp = open(file, 'rt')
        if fp:
            obj = json.load(fp)
            fp.close()

            self.__dict__ = deepcopy(obj)

            self.step_0 = BasePcModel()
            self.step_1 = BasePcModel()
            self.step_2 = BasePcModel()

            print obj
            print obj['step_0']

            self.step_0.__dict__ = deepcopy(obj['step_0'])
            self.step_1.__dict__ = deepcopy(obj['step_1'])
            self.step_2.__dict__ = deepcopy(obj['step_2'])

            self.advans = []
            for ad in obj['advans']:
                a = adv.Advancement(None, None)
                a.__dict__ = deepcopy(ad)
                self.advans.append(a)

            self.unsaved  = False
            return True
        return False
