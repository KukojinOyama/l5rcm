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
import sys
import os

#import xml.etree.cElementTree as ET
import lxml.etree as ET

XML_HD = '''<?xml version="1.0" encoding="UTF-8" ?>'''

def __write_hd(fobj):
    fobj.write(XML_HD + "\n")
    fobj.write("<L5RCM>\n")

def __write_ft(fobj):
    fobj.write("</L5RCM>")
        
def exp_clans(db, out_file, out_path):
    c = db.cursor()
    c.execute("select * from clans")
    
    if not os.path.exists(out_path):
        os.makedirs(out_path)        
    fpath = os.path.join(out_path, out_file)
    
    with open(fpath, 'wt') as fobj:
        __write_hd(fobj)
        for id, name in c.fetchall():
            fobj.write('''\t<Clan name="{0}"/>\n'''.format(name))
        __write_ft(fobj)
                        
def exp_families(db, out_file, out_path):
    c = db.cursor()
    c.execute("select clans.name, families.name, perk from families inner join clans on clans.uuid=clan_id order by clans.name")
    fobj = None
    cn   = None
    
    if not os.path.exists(out_path):
        os.makedirs(out_path)        
      
    for clan, name, perk in c.fetchall():
        if cn != clan:
            if fobj: 
                __write_ft(fobj)
                fobj.close()
            fname = "{0}_{1}".format(clan, out_file)
            fpath = os.path.join(out_path, fname)
            cn    = clan
            fobj  = open(fpath, 'wt')
            __write_hd(fobj)
                    
        fobj.write('''\t<Family name="{0}">\n'''.format(name))
        fobj.write('''\t\t<Clan>{0}</Clan>\n'''.format(clan))
        fobj.write('''\t\t<Trait>{0}</Trait>\n'''.format(perk.capitalize()))
        fobj.write('''\t</Family>\n''')
    
    if fobj: 
        __write_ft(fobj)
        fobj.close()
        
def exp_schools(db, out_file, out_path):
    c = db.cursor()
    c.execute('''select schools.uuid, clans.name, schools.name, tag, perk,
                 affinity, deficiency, honor
                 from schools inner join clans on clans.uuid=clan_id order by clans.name''')
    cn   = None
    
    if not os.path.exists(out_path):
        os.makedirs(out_path)
        
    scs  = [ x for x in c.fetchall() ]
    root = None
    
    
    for uuid, clan, name, tags, perk, affi, defi, hon in scs:
        if cn != clan and root is not None:
            fname = "{0}_{1}".format(cn, out_file)
            fpath = os.path.join(out_path, fname)            
            #ET.ElementTree(root).write(fpath, 'utf-8', True)
            ET.ElementTree(root).write(fpath, pretty_print = True, encoding='UTF-8', xml_declaration=True)
            root = None
            
        if root is None:
            root = ET.Element('L5RCM')
            cn    = clan
            
        efam = ET.SubElement(root, 'School', {'name': name})
        ET.SubElement(efam, 'Clan').text = clan
        if perk: ET.SubElement(efam, 'Trait').text = perk.capitalize()
        if affi: ET.SubElement(efam, 'Affinity').text = affi.capitalize()
        if defi: ET.SubElement(efam, 'Deficiency').text = defi.capitalize()
        if hon : ET.SubElement(efam, 'Honor').text = str(hon)
        etags = ET.SubElement(efam, 'Tags')
        for tag in tags.split(';'):
            ET.SubElement(etags, 'Tag').text = tag.strip().capitalize()
            
        exp_school_skills(db, uuid, ET.SubElement(efam, 'Skills'))
        exp_school_spells(db, uuid, ET.SubElement(efam, 'Spells'))
        exp_school_techs (db, uuid, ET.SubElement(efam, 'Techs' ))
        exp_school_requirements(db, uuid, ET.SubElement(efam, 'Requirements'))
    
    if root is not None: 
        fname = "{0}_{1}".format(cn, out_file)
        fpath = os.path.join(out_path, fname)
        #ET.ElementTree(root).write(fpath, 'utf-8', True)
        ET.ElementTree(root).write(fpath, pretty_print = True, encoding='UTF-8', xml_declaration=True)
        
def exp_school_skills(db, uuid, root):
    c = db.cursor()
    c.execute('''select skills.name, emphases, skill_rank
                 from school_skills inner join skills on skills.uuid=skill_uuid
                 where school_uuid=?
                 order by skills.name''', [uuid])
                 
    for name, emphases, rank in c.fetchall():
        if emphases:
            ET.SubElement(root, "Skill", {'emphases': emphases, 'rank': str(rank) }).text = name
        else:
            ET.SubElement(root, "Skill", {'rank': str(rank) }).text = name

    c.execute('''select wildcard, skill_rank
                 from school_skills 
                 where wildcard is not null
                 and school_uuid=?''', [uuid])
                 
    for wildcard, rank in c.fetchall():
        epc = ET.SubElement(root, "PlayerChoose", {'rank': str(rank) })
        for wc in wildcard.split(';'):
            ET.SubElement(epc, "Wildcard").text = wc.strip()

def exp_school_spells(db, uuid, root):
    c = db.cursor()
    c.execute('''select school_uuid, spells.name
                 from school_spells inner join spells on spells.uuid=spell_uuid
                 where school_uuid=?
                 order by spells.name''', [uuid])
                 
    for sc, name in c.fetchall():
        ET.SubElement(root, "Spell").text = name
        
    c.execute('''select school_uuid, wildcard
                 from school_spells 
                 where wildcard is not null
                 and school_uuid=?''', [uuid])
                 
    for sc, wildcard in c.fetchall():
        elem, cnt = wildcard.split(' ')
        cnt = cnt.strip('()')
        epc = ET.SubElement(root, "PlayerChoose", {'count': cnt, 'element': elem})

def exp_school_techs (db, uuid, root):
    c = db.cursor()
    c.execute('''select school_techs.name, rank, desc
                 from school_techs inner join schools on schools.uuid=school_uuid
                 where school_uuid=?
                 order by rank''', [uuid])
                 
    for name, rank, desc in c.fetchall():
        if not desc: desc = ''
        ET.SubElement(root, "Tech", {'name': name, 'rank': str(rank)}).text = desc
        
def exp_school_requirements(db, uuid, root):        
    c = db.cursor()
    c.execute('''select req_field, req_type, min_val, max_val, target_val
                 from requirements inner join schools on schools.uuid=ref_uuid
                 where ref_uuid=?''', [uuid])
                 
    for field, type, min, max, trg in c.fetchall():
        attr = {'type': type, 'field': field }
        if min: attr['min'] = str(min)
        if max: attr['min'] = str(max)
        if trg: attr['trg'] = str(trg)
        ET.SubElement(root, "Requirement", attr)
        
def exp_skills(db, out_file, out_path):  
    c = db.cursor()
    c.execute('''select uuid, name, type, attribute
                 from skills order by type''')
    root = ET.Element('L5RCM')
    for uuid, name, type, trait in c.fetchall():
        attr = {'type': type, 'trait': trait.capitalize(), 'name': name}
        sk_def = ET.SubElement(root, "SkillDef", attr)        
        exp_tags(db, uuid, ET.SubElement(sk_def, 'Tags'))
        
    fpath = os.path.join(out_path, out_file)
    ET.ElementTree(root).write(fpath, pretty_print = True, encoding='UTF-8', xml_declaration=True)
    
def exp_weapons(db, out_file, out_path):
    c = db.cursor()
    c.execute('''select weapons.uuid, weapons.name, skills.name, dr,
                 dr_alt, range, strength, min_strength,
                 effect_id, cost
                 from weapons
                 inner join skills on skills.uuid=skill_uuid
                 order by skills.name''')
                 
    root = ET.Element('L5RCM')
    for uuid, name, skill, dr, dr_alt, range, strength, min_strength, effect_id, cost in c.fetchall():
        attr = {'name': name}
        if skill: attr['skill'] = skill
        if dr: attr['dr'] = dr
        if dr_alt: attr['dr_alt'] = dr_alt
        if range: attr['range'] = str(range)
        if strength: attr['strength'] = str(strength)
        if min_strength: attr['min_strength'] = str(min_strength)
        if cost: attr['cost'] = str(cost)
               
        wp_def = ET.SubElement(root, "Weapon", attr)        
        exp_tags(db, uuid, ET.SubElement(wp_def, 'Tags'))
        
        if effect_id:
            d = db.cursor()
            d.execute('''select tag, desc from effects where uuid=?''', [effect_id])
            tag, desc = d.fetchone()
            ET.SubElement(wp_def, 'Effect', {'tag': tag}).text = desc        
        
    fpath = os.path.join(out_path, out_file)
    ET.ElementTree(root).write(fpath, pretty_print = True, encoding='UTF-8', xml_declaration=True)    
    
    
def exp_spells(db, out_file, out_path):
    c = db.cursor()
    c.execute('''select uuid, name, ring, mastery,
                 range, area, duration, raises                 
                 from spells
                 order by mastery, ring, name asc''')
                 
    root = ET.Element('L5RCM')
    for uuid, name, ring, mastery, range, area, duration, raises in c.fetchall():
        attr = {'name': name, 'ring': ring, 'mastery': str(mastery), 'range': range, 
                'area': area, 'duration': duration}
                       
        sp_def = ET.SubElement(root, "Spell", attr)
        tags = ET.SubElement(sp_def, 'Tags')
        exp_tags(db, uuid, tags)
        if raises:
            r_elem = ET.SubElement(sp_def, 'Raises')
            for r in raises.split(';'):
                ET.SubElement(r_elem, 'Raise').text = r.strip()
                
        # add maho tag
        if '[MAHO]' in name:
            ET.SubElement(tags, 'Tag').text = 'Maho'            
        
    fpath = os.path.join(out_path, out_file)
    ET.ElementTree(root).write(fpath, pretty_print = True, encoding='UTF-8', xml_declaration=True)    
    
def exp_tags(db, uuid, root):
    c = db.cursor()
    c.execute('''select uuid, tag
                 from tags
                 where uuid=? order by tag''', [uuid])
                 
    for uuid, tag in c.fetchall():
        ET.SubElement(root, "Tag").text = tag
        
def main():
    db = sqlite3.connect(sys.argv[1])
    exp_clans   (db, "clans.xml", '../share/l5rcm/data')
    exp_families(db, "families.xml", '../share/l5rcm/data/families')
    exp_schools (db, "schools.xml", '../share/l5rcm/data/schools')
    exp_skills  (db, "skills.xml", '../share/l5rcm/data')
    exp_weapons (db, "weapons.xml", '../share/l5rcm/data')
    exp_spells  (db, "spells.xml", '../share/l5rcm/data')
        
if __name__ == '__main__':
    main()
