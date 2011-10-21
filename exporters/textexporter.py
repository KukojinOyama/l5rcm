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

import string
import textwrap
import models

class TextExporter(object):
    def __init__(self):
        self.model  = None
        self.form   = None
        
    def set_model(self, model):
        self.model = model
               
    def set_form(self, form):
        self.form = form
        
    def export(self, io):
        header ="""\
                * Created by L5R: Character Manager
                * Author: Daniele Simonetti
                * All right on L5R RPG belongs to AEG"""
        io.write(textwrap.dedent(header))
        io.write('\n\n')
                 
        # begin CHARACTER SECTION
        self.write_character       (io)
        #self.write_initiative_armor(io)
        #self.write_health          (io)
        
    def write_character(self, io):
        m = self.model
        f = self.form
        
        io.write('# CHARACTER\n')
        io.write(str.format('{0:30}RANK   : {1:>12}\n', 
                self.get_fullname(m), m.get_insight_rank()))
        io.write(str.format('CLAN  : {0:>18}    FAMILY : {1:>12}\n', 
                 self.get_clan_name(m), self.get_family_name(m)))
        io.write(str.format('SCHOOL: {0:>18}    INSIGHT: {1:>12}\n',
                 self.get_school_name(m), m.get_insight()))
        io.write(str.format('EXP   : {0:>18}\n', self.get_exp(m)))
        io.write('\n')
        
        # Rings
        io.write(str.format('EARTH: {0:>2}    Stamina : {1:>2}    Willpower   : {2:>2}\n',
                 m.get_ring_rank(models.RINGS.EARTH), 
                 m.get_attrib_rank(models.ATTRIBS.STAMINA),
                 m.get_attrib_rank(models.ATTRIBS.WILLPOWER)))
        io.write(str.format('AIR  : {0:>2}    Reflexes: {1:>2}    Awareness   : {2:>2}\n',
                 m.get_ring_rank(models.RINGS.AIR), 
                 m.get_attrib_rank(models.ATTRIBS.REFLEXES),
                 m.get_attrib_rank(models.ATTRIBS.AWARENESS)))
        io.write(str.format('WATER: {0:>2}    Strength: {1:>2}    Perception  : {2:>2}\n',
                 m.get_ring_rank(models.RINGS.WATER), 
                 m.get_attrib_rank(models.ATTRIBS.STRENGTH),
                 m.get_attrib_rank(models.ATTRIBS.PERCEPTION)))
        io.write(str.format('FIRE : {0:>2}    Agility : {1:>2}    Intelligence: {2:>2}\n',
                 m.get_ring_rank(models.RINGS.FIRE), 
                 m.get_attrib_rank(models.ATTRIBS.AGILITY),
                 m.get_attrib_rank(models.ATTRIBS.INTELLIGENCE)))
        io.write(str.format('VOID : {0:>2}    Void Points:    oooooooooo\n',
                 m.get_ring_rank(models.RINGS.VOID)))
                 
        # Flags
        io.write('\n')
        io.write(str.format('HONOR : {0}\nGLORY : {1}\nSTATUS: {2}\nTAINT : {3}\n',
                            m.get_honor(), m.get_glory(), m.get_status(),
                            m.get_taint()))
        io.write('\n')
        io.write('# INITIATIVE          # ARMOR TN\n')
        io.write(str.format('BASE    : {0:<12}NAME     : {1}\n',
                 f.tx_base_init.text(),
                 f.tx_armor_nm.text()))                 
        io.write(str.format('MODIFIER: {0:<12}BASE     : {1}\n',
                 f.tx_mod_init.text(),
                 f.tx_base_tn.text()))        
        io.write(str.format('CURRENT : {0:<12}ARMOR    : {1}\n',
                 f.tx_cur_init.text(),
                 f.tx_armor_tn.text()))
        io.write(str.format('                      REDUCTION: {0}\n',
                 f.tx_armor_rd.text()))
        io.write(str.format('                      CURRENT  : {0}\n',
                 f.tx_cur_tn.text()))
                 
                 
    def get_clan_name(self, model):
        return self.form.cb_pc_clan.currentText()
        
    def get_family_name(self, model):
        return self.form.cb_pc_family.currentText()
        
    def get_school_name(self, model):
        return self.form.cb_pc_school.currentText()
        
    def get_fullname(self, model):
        return '%s %s' % (self.get_family_name(model), model.name)
        
    def get_exp(self, model):
        return '%s / %s' % (model.get_px(), model.exp_limit)
        