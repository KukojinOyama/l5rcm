#!/usr/bin/python

class ArmorOutfit(object):
    def __init__(self):
        self.tn   = 0
        self.rd   = 0
        self.name = ''
        self.desc = ''
        self.rule = ''
        self.cost = ''      

class WeaponOutfit(object):        
    def __init__(self):
        self.dr       = ''
        self.dr_alt   = ''
        self.name     = ''
        self.desc     = ''
        self.rule     = ''
        self.cost     = '' 
        self.range    = ''
        self.strength = 0
        self.min_str  = 0
        
def weapon_outfit_from_db(dbconn, weap_uuid):
    itm = WeaponOutfit()
    
    c = dbconn.cursor()
    c.execute('''select name, dr, dr_alt, range, strength,
                 min_strength, effect_id, cost
                 from weapons
                 where uuid=?''', [weap_uuid])
    
    for name, dr, dr_alt, rng, str_, mstr_, eff, cost in c.fetchall():
        c.execute('''select desc from effects
                     where uuid=?''', [eff])
        rule_text = ''
        for desc in c.fetchall():
            rule_text = desc[0]
            break
       
        itm.name     = name
        itm.dr       = dr
        itm.dr_alt   = dr_alt
        itm.rule     = rule_text
        itm.cost     = cost
        itm.range    = rng
        itm.strength = str_
        itm.min_str  = mstr_            
        break
    c.close()
    return itm
            
def armor_outfit_from_db(dbconn, armor_uuid):
    itm = ArmorOutfit()
    
    c = dbconn.cursor()
    c.execute('''select name, tn, rd, special, cost from armors
                 where uuid=?''', [armor_uuid])
    
    for name, tn, rd, special, cost in c.fetchall():
        c.execute('''select desc from effects
                     where tag=?''', [special])
        rule_text = ''
        for desc in c.fetchall():
            rule_text = desc[0]
            break
            
        itm.name = name
        itm.tn   = tn
        itm.rd   = rd
        itm.rule = rule_text
        itm.cost = cost
        break
        
    c.close()
    return itm
