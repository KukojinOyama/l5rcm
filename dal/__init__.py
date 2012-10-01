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

from clan        import *
from family      import *
from school      import *
from skill       import *
from spell       import *
from perk        import *
from powers      import *
from weapon      import *

import os
import xml.etree.cElementTree as ET

class Data(object):
    def __init__(self, data_dir, cust_data_dir = None):
        self.data_dir      = data_dir
        self.cust_data_dir = cust_data_dir
        
        self.clans     = []
        self.families  = []
        self.schools   = []
        
        self.spells    = []
        self.skills    = []
        self.merits    = []
        self.flaws     = []
        self.katas     = []
        self.kihos     = []
        self.tattoos   = []
        
        self.weapons   = []
        self.armors    = []
        
        self.skcategs       = []        
        self.perktypes      = []
        self.weapon_effects = []
        
        if data_dir and os.path.exists(data_dir):
            self.load_data(data_dir)
            
        print(cust_data_dir)
        if cust_data_dir and os.path.exists(cust_data_dir):
            self.load_data(cust_data_dir)
    
    def append_to(self, collection, item):
        if item in collection:
            i = collection.index(item)
            collection[i] = item
        else:
            collection.append(item)
    
    def load_data(self, data_path):
        # iter through all the data tree and import all xml files
        for path, dirs, files in os.walk(data_path):
            dirn = os.path.basename(path)
            if dirn.startswith('.'):
                continue
            for file_ in files:
                if file_.startswith('.') or file_.endswith('~'):
                    continue
                if not file_.endswith('.xml'):
                    continue
                try:
                    self.__load_xml(os.path.join(path, file_))
                except Exception as e:
                    print("cannot parse file {0}".format(file_))
                    import traceback
                    traceback.print_exc()
        
    def __load_xml(self, xml_file):
        print('load data from {0}'.format(xml_file))
        tree = ET.parse(xml_file)
        root = tree.getroot()
        if root is None or root.tag != 'L5RCM':
            raise Exception("Not an L5RCM data file")
        for elem in list(root):
            if elem.tag == 'Clan':
                self.append_to(self.clans, Clan.build_from_xml(elem))
            elif elem.tag == 'Family':
                self.append_to(self.families, Family.build_from_xml(elem))
            elif elem.tag == 'School':
                self.append_to(self.schools, School.build_from_xml(elem))
            elif elem.tag == 'SkillDef':
                self.append_to(self.skills, Skill.build_from_xml(elem))
            elif elem.tag == 'SpellDef':
                self.append_to(self.spells, Spell.build_from_xml(elem))
            elif elem.tag == 'Merit':
                self.append_to(self.merits, Perk.build_from_xml(elem))
            elif elem.tag == 'Flaw':
                self.append_to(self.flaws, Perk.build_from_xml(elem))
            elif elem.tag == 'SkillCateg':
                self.append_to(self.skcategs, SkillCateg.build_from_xml(elem))
            elif elem.tag == 'KataDef':
                self.append_to(self.katas, Kata.build_from_xml(elem))
            elif elem.tag == 'PerkCateg':
                self.append_to(self.perktypes, PerkCateg.build_from_xml(elem))
            elif elem.tag == 'EffectDef':
                self.append_to(self.weapon_effects, WeaponEffect.build_from_xml(elem))
            elif elem.tag == 'Weapon':
                self.append_to(self.weapons, Weapon.build_from_xml(elem))
            elif elem.tag == 'Armor':
                self.append_to(self.armors, Armor.build_from_xml(elem))
                   
                
                
                
