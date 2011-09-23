#!/usr/bin/python

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
    return 0   

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
    return 0            

class BasePcModel(object):
    def __init__(self):
        self.name      = ''
        self.clan      = 0
        self.school    = 0
        self.insight   = 0
        self.rank      = 0
        self.tag       = ''
        self.tags      = []
        self.void      = 2
        self.attribs   = [2, 2, 2, 2, 2, 2, 2, 2]
        self.skills    = []
        self.honor     = 0.0
        self.glory     = 0.0
        self.status    = 0.0
        self.taint     = 0.0
        self.attrib_costs = [4, 4, 4, 4, 4, 4, 4, 4]
        self.void_cost    = 6
        
    def load_default(self):
        self.void    = 2
        self.attribs = [2, 2, 2, 2, 2, 2, 2, 2]
        self.rank    = 1

class AdvancedPcModel(BasePcModel):
    def __init__(self):
        super(AdvancedPcModel, self).__init__()
    
        self.step_0 = BasePcModel()
        self.step_1 = BasePcModel()
        
        self.advans = []

        self.void_points = self.get_void_rank()

    def load_default(self):
        self.step_0.load_default()
        self.step_1.load_default()

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

        c = max(a,b)

        for adv in self.advans:
            if adv.type != 'attrib':
                continue
            if adv.attrib == attrib: c += 1

        return c

    def get_void_rank(self):
        v = max(self.step_0.void, self.step_1.void)

        for adv in self.advans:
            if adv.type != 'void':
                continue
            v += 1

        return v

    def get_skill_rank(self, idx):
        return 0

    def get_insight(self):
        n = 0
        for i in xrange(0, 5):
            n += self.get_ring_rank(i)*10
        for i in xrange(0, len(self.skills)):
            n += self.get_skill_rank(i)
        return n
