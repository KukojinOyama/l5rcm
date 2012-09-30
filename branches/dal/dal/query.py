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

def get_clan(storage, id):
    try:
        return filter( lambda x: x.id == id, storage.clans )[0]
    except:
        return None
        
def get_family(storage, id):
    try:
        return filter( lambda x: x.id == id, storage.families )[0]
    except:
        return None
        
def get_school(storage, id):
    try:
        return filter( lambda x: x.id == id, storage.schools )[0]
    except:
        return None
        
def get_school_tech(school_obj, rank):
    try:
        return filter( lambda x: x.rank == rank, school_obj.techs )[0]
    except:
        return None, None
        
def get_tech(storage, id):
    for sc in storage.schools:
        tech   = filter( lambda x: x.id == id, sc.techs )
        if len(tech): return sc, tech[0]
    return None        

def get_skill(storage, id):
    try:
        return filter( lambda x: x.id == id, storage.skills )[0]
    except:
        return None

def get_skills(storage, categ):
    return filter( lambda x: x.type == categ, storage.skills )
        
def get_spells(storage, ring, mastery):
    return filter( lambda x: x.element == ring and x.mastery == mastery, storage.spells )

def get_maho_spells(storage, ring, mastery):
    return filter( lambda x: x.element == ring and x.mastery == mastery and 'maho' in x.tags, storage.spells )
    
def get_mastery_ability_rule(storage, id, value):
    try:
        skill = get_skill(storage, id)
        return filter( lambda x: x.rank == value, skill.mastery_abilities )[0].rule        
    except:
        return None    
        
def get_kata(storage, id):
    try:
        return filter( lambda x: x.id == id, storage.katas )[0]
    except:
        return None
        
def get_spell(storage, id):
    try:
        return filter( lambda x: x.id == id, storage.spells )[0]
    except:
        return None                