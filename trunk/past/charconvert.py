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

import sqlite3
import copy

def clan_name_from_id(c, uuid):
    c.execute('''select name from clans where uuid=?''', [uuid])
    return c.fetchone()[0]

def clan_id_from_name(c, nm):
    c.execute('''select uuid from clans where name=?''', [nm])
    return c.fetchone()[0]
    
def family_name_from_id(c, uuid):
    c.execute('''select name from families where uuid=?''', [uuid])
    return c.fetchone()[0]

def family_id_from_name(c, nm):
    c.execute('''select uuid from families where name=?''', [nm])
    return c.fetchone()[0]
    
def school_name_from_id(c, uuid):
    c.execute('''select name from schools where uuid=?''', [uuid])
    return c.fetchone()[0]

def school_id_from_name(c, nm):
    c.execute('''select uuid from schools where name=?''', [nm])
    return c.fetchone()[0]   

def tech_name_from_id(c, uuid):
    c.execute('''select name from school_techs where uuid=?''', [uuid])
    return c.fetchone()[0]

def tech_id_from_name(c, nm):
    c.execute('''select uuid from school_techs where name=?''', [nm])
    return c.fetchone()[0]
    
def skill_name_from_id(c, uuid):
    c.execute('''select name from skills where uuid=?''', [uuid])
    return c.fetchone()[0]

def skill_id_from_name(c, nm):
    c.execute('''select uuid from skills where name=?''', [nm])
    return c.fetchone()[0]       

def perk_name_from_id(c, uuid):
    c.execute('''select name from perks where uuid=?''', [uuid])
    return c.fetchone()[0]

def perk_id_from_name(c, nm):
    c.execute('''select uuid from perks where name=?''', [nm])
    return c.fetchone()[0]     
    
def spell_name_from_id(c, uuid):
    c.execute('''select name from spells where uuid=?''', [uuid])
    return c.fetchone()[0]

def spell_id_from_name(c, nm):
    c.execute('''select uuid from spells where name=?''', [nm])
    return c.fetchone()[0]     
    
class CharConvert(object):
    def __init__(self, model, old_db, new_db):
        self.pc  = model
        self.odb = old_db
        self.ndb = new_db
        
    def start(self):
        self.old_conn = sqlite3.connect(self.odb)
        self.new_conn = sqlite3.connect(self.ndb)
        
        self.fix_clan()
        self.fix_family()
        self.fix_school()
        self.fix_spells()
        self.fix_skills()
        self.fix_techs()
        self.fix_perks()
        self.fix_emphs()
        
    def fix_clan(self):
        try:
            oc = self.old_conn.cursor()
            nc = self.new_conn.cursor()

            nm = clan_name_from_id(oc, self.pc.clan)
            print 'character clan: %d, %s' % (self.pc.clan, nm)
            self.pc.clan = clan_id_from_name(nc, nm)
            print 'character new clan: %d, %s' % (self.pc.clan, nm)
        except:
            print 'clan not updated'
        finally:
            oc.close()
            nc.close()
        
        
    def fix_family(self):
        try:
            oc = self.old_conn.cursor()
            nc = self.new_conn.cursor()

            nm = family_name_from_id(oc, self.pc.family)
            print 'character family: %d, %s' % (self.pc.family, nm)
            self.pc.family = family_id_from_name(nc, nm)
            print 'character new family: %d, %s' % (self.pc.family, nm)
        except:
            print 'family not updated'
        finally:
            oc.close()
            nc.close()
        
    def fix_school(self):
        try:
            oc = self.old_conn.cursor()
            nc = self.new_conn.cursor()

            # SCHOOL
            nm = school_name_from_id(oc, self.pc.school)
            print 'character school: %d, %s' % (self.pc.school, nm)
            self.pc.school = school_id_from_name(nc, nm)
            print 'character new school: %d, %s' % (self.pc.school, nm)
            
            # SCHOOL BASE TECHNIQUE
            nm = tech_name_from_id(oc, self.pc.step_2.school_tech)
            print 'old school tech: %d, %s' % (self.pc.step_2.school_tech, nm)
            self.pc.step_2.school_tech = tech_id_from_name(nc, nm)
            print 'new school tech: %d, %s' % (self.pc.step_2.school_tech, nm)
        except:
            print 'school not updated'
        finally:
            oc.close()
            nc.close()
        
    def fix_spells(self):
        try:
            oc = self.old_conn.cursor()
            nc = self.new_conn.cursor()
            
            # SCHOOL SPELLS
            i = 0
            for isp in self.pc.step_2.spells:            
                nm  = spell_name_from_id(oc, isp)
                print 'old spell: %d, %s' % (isp, nm)
                isp = spell_id_from_name(nc, nm)
                self.pc.step_2.spells[i] = isp
                print 'new spell: %d, %s' % (isp, nm)            
                i += 1
            
            # LEARNED SPELLS
            i = 0
            for isp in self.pc.spells:            
                nm  = spell_name_from_id(oc, isp)
                print 'old spell: %d, %s' % (isp, nm)
                isp = spell_id_from_name(nc, nm)
                self.pc.spells[i] = isp
                print 'new spell: %d, %s' % (isp, nm)            
                i += 1
        except:
            print 'spells not updated'
        finally:
            oc.close()
            nc.close()
    
    def fix_techs(self):
        try:        
            oc = self.old_conn.cursor()
            nc = self.new_conn.cursor()
            
            # LEARNED TECHNIQUES
            i = 0
            for tech_id in self.pc.techs:
                nm = tech_name_from_id(oc, tech_id)
                print 'old tech: %d, %s' % (tech_id, nm)
                self.pc.techs[i] = tech_id_from_name(nc, nm)
                print 'new tech: %d, %s' % (self.pc.techs[i], nm)            
                i += 1
        except:
            print 'techniques not updated'
        finally:
            oc.close()
            nc.close()
    
    def fix_skills(self):
        try:
            oc = self.old_conn.cursor()
            nc = self.new_conn.cursor()
            
            # SCHOOL SKILLS
            old_skills = copy.deepcopy(self.pc.step_2.skills)
            self.pc.step_2.skills = {}        
            for sk in old_skills.iterkeys():
                isk = int(sk)
                nm  = skill_name_from_id(oc, isk)
                print 'old skill: %d, %s' % (isk, nm)
                isk = skill_id_from_name(nc, nm)
                self.pc.step_2.skills[str(isk)] = old_skills[sk]
                print 'new skill: %d, %s, value: %d' % (isk, nm, old_skills[sk])
            
            # LEARNED SKILLS
            for adv in self.pc.advans:
                if adv.type != 'skill':
                    continue
                nm  = skill_name_from_id(oc, adv.skill)
                print 'old skill: %d, %s' % (adv.skill, nm)
                adv.skill = skill_id_from_name(nc, nm)             
                print 'new skill: %d, %s' % (adv.skill, nm)
        except:
            print 'skills not updated'
        finally:
            oc.close()
            nc.close()
                
    def fix_perks(self):
        try:
            oc = self.old_conn.cursor()
            nc = self.new_conn.cursor()
                    
            # LEARNED SKILLS
            for adv in self.pc.advans:
                if adv.type != 'perk':
                    continue
                    
                nm  = perk_name_from_id(oc, adv.perk)
                print 'old perk: %d, %s' % (adv.perk, nm)
                adv.perk = perk_id_from_name(nc, nm)             
                print 'new perk: %d, %s' % (adv.perk, nm)
        except:
            print 'perks not updated'
        finally:
            oc.close()
            nc.close()        

    def fix_emphs(self):
        try:
            oc = self.old_conn.cursor()
            nc = self.new_conn.cursor()
            
            # SCHOOL EMPHASES
            old_emphs = copy.deepcopy(self.pc.step_2.emph)        
            for sk in old_emphs.iterkeys():
                isk = int(sk)
                nm  = skill_name_from_id(oc, isk)
                print 'old emph: %d, %s (%s)' % (isk, nm, old_emphs[sk])
                isk = skill_id_from_name(nc, nm)
                self.pc.step_2.emph[str(isk)] = old_emphs[sk]
                print 'new emph: %d, %s (%s)' % (isk, nm, old_emphs[sk])
            
            # LEARNED EMPHASES
            for adv in self.pc.advans:
                if adv.type != 'emph':
                    continue                
                nm  = skill_name_from_id(oc, adv.skill)
                print 'old emph: %d, %s (%s)' % (adv.skill, nm, adv.text)
                adv.skill = skill_id_from_name(nc, nm)             
                print 'new emph: %d, %s (%s)' % (adv.skill, nm, adv.text)
        except:
            print 'emphases not updated'
        finally:
            oc.close()
            nc.close()
            
def test():
    import sys
    import os
    core_path = os.path.realpath(os.path.dirname(os.path.split(__file__)[0]))
    print core_path
    sys.path.append(core_path)
    
    import models    
    model_path = sys.argv[1]    
    model = models.AdvancedPcModel()
    model.load_default()
    model.load_from(model_path)
    
    cc = CharConvert(model, 'past/l5rdb_old.sqlite', 'past/l5rdb.sqlite')
    cc.start()
    
    model.save_to(model_path + '.updated')
            
if __name__ == '__main__':
    test()
    
    
    