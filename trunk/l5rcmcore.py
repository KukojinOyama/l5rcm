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

import sys
import os
import sqlite3

import rules
import models
import widgets
import dialogs
import autoupdate
import tempfile
import exporters
import dbutil

APP_NAME    = 'l5rcm'
APP_DESC    = 'Legend of the Five Rings: Character Manager'
APP_VERSION = '2.2'
DB_VERSION  = '2.2'
APP_ORG     = 'openningia'

PROJECT_PAGE_LINK = 'http://code.google.com/p/l5rcm/'
BUGTRAQ_LINK      = 'http://code.google.com/p/l5rcm/issues/list'
PROJECT_PAGE_NAME = 'Project Page'
AUTHOR_NAME       = 'Daniele Simonetti'
L5R_RPG_HOME_PAGE = 'http://www.l5r.com/rpg/'
ALDERAC_HOME_PAGE = 'http://www.alderac.com/'

MY_CWD        = os.getcwd()
if not os.path.exists( os.path.join( MY_CWD, 'share/l5rcm') ):
    MY_CWD = sys.path[0]
    if not os.path.exists( os.path.join( MY_CWD, 'share/l5rcm') ):
        MY_CWD = os.path.dirname(sys.path[0])

def get_app_file(rel_path):
    if os.name == 'nt':
        return os.path.join( MY_CWD, 'share/l5rcm', rel_path )
    else:
        sys_path = '/usr/share/l5rcm'
        if os.path.exists( sys_path ):
            return os.path.join( sys_path, rel_path )
        return os.path.join( MY_CWD, 'share/l5rcm', rel_path )

def get_app_icon_path(size = (48,48)):
    size_str = '%dx%d' % size
    if os.name == 'nt':
        return os.path.join( MY_CWD, 'share/icons/l5rcm/%s' % size_str, APP_NAME + '.png' )
    else:
        sys_path = '/usr/share/icons/l5rcm/%s' % size_str
        if os.path.exists( sys_path ):
            return os.path.join( sys_path, APP_NAME + '.png' )
        return os.path.join( MY_CWD, 'share/icons/l5rcm/%s' % size_str, APP_NAME + '.png' )

def get_icon_path(name, size = (48,48)):
    size_str = '%dx%d' % size
    if os.name == 'nt':
        return os.path.join( MY_CWD, 'share/icons/l5rcm/%s' % size_str, name + '.png' )
    else:
        sys_path = '/usr/share/icons/l5rcm/%s' % size_str
        if os.path.exists( sys_path ):
            return os.path.join( sys_path, name + '.png' )
        return os.path.join( MY_CWD, 'share/icons/l5rcm/%s' % size_str, name + '.png' )
        
class CMErrors(object):
    NO_ERROR      = 'no_error'
    NOT_ENOUGH_XP = 'not_enough_xp'

class L5RCMCore(object):
    def __init__(self):        
        self.pc = None
        
        # character stored insight rank
        # used to knew if the character
        # get new insight rank
        self.last_rank = 1
        
        # Flag to lock advancment refunds in order        
        self.lock_advancements = True
        
        # Connect to database
        self.db_conn = None
        
        try:
            self.db_conn = sqlite3.connect( get_app_file('l5rdb.sqlite') )
        except Exception as e:
            sys.stderr.write('unable to open database file %s\n' % get_app_file('l5rdb.sqlite'))
            sys.stderr.write("current working dir : %s\n" % os.getcwd())
        
    def update_from_model(self):
        pass
        
    def reset_adv(self):
        self.pc.advans = []
        self.pc.recalc_ranks()
        self.update_from_model()

    def export_as_text(self, export_file):
        exporter = exporters.TextExporter()
        exporter.set_form (self)
        exporter.set_model(self.pc     )        

        f = open(export_file, 'wt')
        if f is not None:
            exporter.export(f)
        f.close()
        
    def export_as_pdf(self, export_file):
    
        def _create_fdf(exporter):            
            #exporter = exporters.FDFExporterAll()
            exporter.set_form (self)
            exporter.set_model(self.pc     )
            from tempfile import gettempdir
            fpath = os.path.join(gettempdir(), 'l5rcm.fdf')
            fobj = open(fpath, 'wt')
            if fobj is not None:
                exporter.export(fobj)
            fobj.close()        
            return fpath
            
        def _flatten_pdf(fdf_file, source_pdf, target_pdf, target_suffix = None):
            basen = os.path.splitext(os.path.basename(target_pdf))[0]
            based = os.path.dirname (target_pdf)
            
            if target_suffix:
                target_pdf = os.path.join(based, basen) + '_%s.pdf' % target_suffix
            else:
                target_pdf = os.path.join(based, basen) + '.pdf'
                
            # call pdftk
            import subprocess
            args_ = [_get_pdftk(), source_pdf, 'fill_form', fdf_file, 'output', target_pdf, 'flatten']
            subprocess.call(args_)                       
            
        def _get_pdftk():
            if os.name == 'nt':
                return os.path.join(MY_CWD, 'tools', 'pdftk.exe')
            elif os.name == 'posix':
                return '/usr/bin/pdftk'
            return None
        
        # GENERIC SHEET
        source_pdf = get_app_file('sheet_all.pdf')
        source_fdf = _create_fdf(exporters.FDFExporterAll())
        _flatten_pdf(source_fdf, source_pdf, export_file)
        
    def refund_last_adv(self):
        '''pops last advancement and recalculate ranks'''
        if len(self.pc.advans) > 0:
            adv = self.pc.advans.pop()            
            self.pc.recalc_ranks()
            self.update_from_model()

    def refund_advancement(self, adv_idx = -1):
        '''refund the specified advancement and recalculate ranks'''
        if self.lock_advancements:
            return self.refund_last_adv()
        if adv_idx < 0:
            adv_idx = len(self.pc.advans) - self.adv_view.selectionModel().currentIndex().row() - 1
        if adv_idx >= len(self.pc.advans) or adv_idx < 0:
            return
        del self.pc.advans[adv_idx]        
        self.pc.recalc_ranks()
        self.update_from_model()

    def generate_name(self):
        '''generate a random name for the character'''
        gender = self.sender().property('gender')
        name = ''
        if gender == 'male':
            name = rules.get_random_name( get_app_file('male.txt') )
        else:
            name = rules.get_random_name( get_app_file('female.txt') )
        self.pc.name = name
        self.update_from_model()
        
    def increase_trait(self, attrib):    
        cur_value = self.pc.get_attrib_rank( attrib )
        new_value = cur_value + 1
        ring_id = models.get_ring_id_from_attrib_id(attrib)
        ring_nm = models.ring_name_from_id(ring_id)
        cost = self.pc.get_attrib_cost( attrib ) * new_value
        if self.pc.has_rule('elem_bless_%s' % ring_nm):
            cost -= 1
        text = models.attrib_name_from_id(attrib).capitalize()
        adv = models.AttribAdv(attrib, cost)
        adv.desc = '%s, Rank %d to %d. Cost: %d xp' % ( text, cur_value, new_value, cost )
        if (adv.cost + self.pc.get_px()) > self.pc.exp_limit:
            return CMErrors.NOT_ENOUGH_XP

        self.pc.add_advancement( adv )
        self.update_from_model()
        
        return CMErrors.NO_ERROR
    
    def increase_void(self):
        cur_value = self.pc.get_ring_rank( models.RINGS.VOID )
        new_value = cur_value + 1
        cost = self.pc.void_cost * new_value
        if self.pc.has_rule('enlightened'):
            cost -= 2
        adv = models.VoidAdv(cost)
        adv.desc = 'Void Ring, Rank %d to %d. Cost: %d xp' % ( cur_value, new_value, cost )
        if (adv.cost + self.pc.get_px()) > self.pc.exp_limit:
            QtGui.QMessageBox.warning(self, "Not enough XP",
            "Cannot purchase.\nYou've reached the XP Limit.")
            return

        self.pc.add_advancement( adv )
        self.update_from_model()

    def set_exp_limit(self, val):
        self.pc.exp_limit = val
        self.update_from_model()
    
    def set_health_multiplier(self, val):
        self.pc.health_multiplier = val
        self.update_from_model()
    
    def damage_health(self, val):
        self.pc.wounds += val
        if self.pc.wounds < 0: self.pc.wounds = 0
        if self.pc.wounds > self.pc.get_max_wounds():
            self.pc.wounds = self.pc.get_max_wounds()

        self.update_from_model()
    
    def buy_next_skill_rank(self, skill_id):
        print 'buy skill rank %d' % skill_id
        cur_value = self.pc.get_skill_rank(skill_id)
        new_value = cur_value + 1

        cost    = new_value
        sk_type = dbutil.get_skill_type(self.db_conn, skill_id)
        text    = dbutil.get_skill_name(self.db_conn, skill_id)
        
        if (self.pc.has_rule('obtuse') and
            sk_type == 'high' and 
            text != 'Investigation' and
            text != 'Medicine'):
            # double the cost for high skill
            # other than medicine and investigation
            cost *= 2            

        adv = models.SkillAdv(skill_id, cost)
        adv.rule = dbutil.get_mastery_ability_rule(self.db_conn, skill_id, new_value)
        adv.desc = '%s, Rank %d to %d. Cost: %d xp' % ( text, cur_value, new_value, cost )

        if adv.cost + self.pc.get_px() > self.pc.exp_limit:
            return CMErrors.NOT_ENOUGH_XP

        self.pc.add_advancement(adv)
        self.update_from_model()
        
        return CMErrors.NO_ERROR

    def buy_school_requirements(self):
        for skill_uuid in self.get_missing_school_requirements():
            print 'buy requirement skill %d' % skill_uuid
            if self.buy_next_skill_rank(skill_uuid) != CMErrors.NO_ERROR:
                return
        
    def check_if_tech_available(self):
        c = self.db_conn.cursor()
        c.execute('''select COUNT(uuid) from school_techs
                     where school_uuid=?''', [self.pc.get_school_id()])
        count_ = c.fetchone()[0]
        c.close()
        return count_ > self.pc.get_school_rank()

    def check_tech_school_requirements(self):
        # one should have at least one rank in all school skills
        # in order to gain a school techniques
        return len(self.get_missing_school_requirements()) == 0
        
    def get_missing_school_requirements(self):
        list_     = []
        school_id = self.pc.get_school_id()        
        c = self.db_conn.cursor()
        c.execute("""SELECT skill_uuid, skill_rank FROM school_skills
                     WHERE school_uuid=?""", [school_id])
        print 'check requirement for school %d' % school_id
        for uuid, rank in c.fetchall():
            if not uuid: continue
            print 'needed %d, got rank %d' % (uuid, self.pc.get_skill_rank(uuid))            
            if self.pc.get_skill_rank(uuid) < 1:
                list_.append(uuid)
        c.close()
        return list_
        
    def set_pc_affinity(self, affinity):
        if self.pc.has_tag('chuda shugenja school'):
            self.pc.set_affinity('maho ' + affinity.lower())
            self.pc.set_deficiency(affinity.lower())
        else:
            self.pc.set_affinity(affinity.lower())            
        self.update_from_model()
    
    def set_pc_deficiency(self, deficiency):
        self.pc.set_deficiency(deficiency.lower())      
        self.update_from_model()
    