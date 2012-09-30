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
import dal
import dal.query

from PySide import QtCore, QtGui

APP_NAME    = 'l5rcm'
APP_DESC    = 'Legend of the Five Rings: Character Manager'
APP_VERSION = '2.8'
DB_VERSION  = '2.6'
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

def get_tab_icon(name):        
    if os.name == 'nt':
        return os.path.join( MY_CWD, 'share/icons/l5rcm/tabs/', name + '.png' )
    else:
        sys_path = '/usr/share/icons/l5rcm/tabs/'
        if os.path.exists( sys_path ):
            return os.path.join( sys_path, name + '.png' )
        return os.path.join( MY_CWD, 'share/icons/l5rcm/tabs/', name + '.png' )
        
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

class L5RCMCore(QtGui.QMainWindow):
    def __init__(self, locale, parent = None): 
        super(L5RCMCore, self).__init__(parent)
        #print(repr(self))
        self.pc = None
        
        # character stored insight rank
        # used to knew if the character
        # get new insight rank
        self.last_rank = 1
        
        # Flag to lock advancment refunds in order        
        self.lock_advancements = True
        
        # Connect to database
        self.db_conn = None

        # Data storage
        self.dstore = dal.Data( get_app_file('data') )
        
        # current locale
        self.locale = locale

        db_name = 'l5rdb_{0}.sqlite'.format(locale)
        if not os.path.exists( get_app_file(db_name) ):
            db_name = 'l5rdb.sqlite'
        
        print("using database file: {0}".format(get_app_file(db_name)))
        
        try:            
            self.db_conn = sqlite3.connect(  get_app_file(db_name) )
        except Exception as e:
            sys.stderr.write('unable to open database file %s\n' % get_app_file('l5rdb.sqlite'))
            sys.stderr.write("current working dir : %s\n" % os.getcwd())           
        
    def update_from_model(self):
        pass
        
    def export_as_text(self, export_file):
        exporter = exporters.TextExporter()
        exporter.set_form (self)
        exporter.set_model(self.pc     )        

        f = open(export_file, 'wt')
        if f is not None:
            exporter.export(f)
        f.close()
        
    def export_as_pdf(self, export_file):
        from tempfile import mkstemp
        import subprocess
        
        def _create_fdf(exporter):            
            #exporter = exporters.FDFExporterAll()
            exporter.set_form (self)
            exporter.set_model(self.pc     )           
            #fpath = os.path.join(gettempdir(), 'l5rcm.fdf')
            fd, fpath = mkstemp(suffix='.fdf', text=True)
            with os.fdopen(fd, 'wt') as fobj:
                exporter.export(fobj)            
            
            return fpath
            
        def _flatten_pdf(fdf_file, source_pdf, target_pdf, target_suffix = None):
            basen = os.path.splitext(os.path.basename(target_pdf))[0]
            based = os.path.dirname (target_pdf)
            
            if target_suffix:
                target_pdf = os.path.join(based, basen) + '_%s.pdf' % target_suffix
            else:
                target_pdf = os.path.join(based, basen) + '.pdf'
                
            # call pdftk            
            args_ = [_get_pdftk(), source_pdf, 'fill_form', fdf_file, 'output', target_pdf, 'flatten']
            subprocess.call(args_)
            _try_remove(fdf_file)
            print('created pdf {0}'.format(target_pdf))
            
        def _merge_pdf(input_files, output_file):
            # call pdftk            
            args_ = [_get_pdftk()] + input_files + ['output', output_file]
            subprocess.call(args_)
            for f in input_files:
                _try_remove(f)            
            
        def _get_pdftk():
            if os.name == 'nt':
                return os.path.join(MY_CWD, 'tools', 'pdftk.exe')
            elif os.name == 'posix':
                return '/usr/bin/pdftk'
            return None
            
        def _try_remove(fpath):
            try: 
                os.remove(fpath) 
            except:
                pass
            print('removed {0}'.format(fpath))
        
        temp_files = []        
        # GENERIC SHEET
        source_pdf = get_app_file('sheet_all.pdf')
        source_fdf = _create_fdf(exporters.FDFExporterAll())  
        fd, fpath = mkstemp(suffix='.pdf');
        os.fdopen(fd, 'wt').close()
        _flatten_pdf(source_fdf, source_pdf, fpath)        
        
        temp_files.append(fpath)
        # SHUGENJA SHEET
        if self.pc.has_tag('shugenja'):
            source_pdf = get_app_file('sheet_shugenja.pdf')
            source_fdf = _create_fdf(exporters.FDFExporterShugenja())
            fd, fpath = mkstemp(suffix='.pdf');
            os.fdopen(fd, 'wt').close()
            _flatten_pdf(source_fdf, source_pdf, fpath)
            temp_files.append(fpath)
        
        if os.path.exists(export_file):
            os.remove(export_file)
        
        if len(temp_files) > 1:
            _merge_pdf(temp_files, export_file)
        elif len(temp_files) == 1:
            os.rename(temp_files[0], export_file)
        
    def remove_advancement_item(self, adv_itm):
        if adv_itm in self.pc.advans:
            self.pc.advans.remove(adv_itm)
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
        adv.desc = (self.tr('{0}, Rank {1} to {2}. Cost: {3} xp')
                   .format( text, cur_value, new_value, adv.cost ))
                   
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
        adv.desc = (self.tr('Void Ring, Rank {0} to {1}. Cost: {2} xp')
                   .format( cur_value, new_value, adv.cost ))
        if (adv.cost + self.pc.get_px()) > self.pc.exp_limit:
            return CMErrors.NOT_ENOUGH_XP

        self.pc.add_advancement( adv )
        self.update_from_model()
        
        return CMErrors.NO_ERROR

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
        print('buy skill rank {0}'.format(skill_id))
        cur_value = self.pc.get_skill_rank(skill_id)
        new_value = cur_value + 1

        cost    = new_value
        skill   = dal.query.get_skill(self.dstore, skill_id)
        sk_type = skill.type
        text    = skill.name
               
        if (self.pc.has_rule('obtuse') and
            sk_type == 'high' and 
            skill_id != 'investigation'   and # investigation
            skill_id != 'medicine'):     # medicine
            
            # double the cost for high skill
            # other than medicine and investigation
            cost *= 2            

        adv = models.SkillAdv(skill_id, cost)
        adv.rule = dal.query.get_mastery_ability_rule(self.dstore, skill_id, new_value)
        adv.desc = (self.tr('{0}, Rank {1} to {2}. Cost: {3} xp')
                   .format( text, cur_value, new_value, adv.cost ))
                   

        if adv.cost + self.pc.get_px() > self.pc.exp_limit:
            return CMErrors.NOT_ENOUGH_XP

        self.pc.add_advancement(adv)
        self.update_from_model()
        
        return CMErrors.NO_ERROR
        
    def memo_spell(self, spell_id):
        print('memorize spell {0}'.format(spell_id))
        info_ = dal.query.get_spell(self.dstore, spell_id)
        cost  = info_.mastery
        text  = info_.name
        
        adv = models.MemoSpellAdv(spell_id, cost)
        adv.desc = (self.tr('{0}, Mastery {1}. Cost: {2} xp')
                   .format( text, cost, adv.cost ))

        if adv.cost + self.pc.get_px() > self.pc.exp_limit:
            return CMErrors.NOT_ENOUGH_XP

        self.pc.add_advancement(adv)
        self.update_from_model()
        
        return CMErrors.NO_ERROR
        
    def remove_spell(self, spell_id):
        self.pc.remove_spell(spell_id)
        self.update_from_model()

    def buy_school_requirements(self):
        for skill_uuid in self.get_missing_school_requirements():
            print('buy requirement skill {0}'.format(skill_uuid))
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
        print('check requirement for school {0}'.format(school_id))
        for uuid, rank in c.fetchall():
            if not uuid: continue
            print('needed {0}, got rank {1}'.format(uuid, self.pc.get_skill_rank(uuid)))
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
        
    
    def get_school_name(self, school_id):
        c = self.db_conn.cursor()
        c.execute('''select name from schools
                     where uuid=?''', [school_id])
        tmp = c.fetchone()
        c.close()
        return tmp[0] if tmp else ""
        
    def get_school_aff_def(self, school_id):
        c = self.db_conn.cursor()
        c.execute('''select affinity, deficiency from schools
                     where uuid=?''', [school_id])
        tmp = c.fetchone()
        c.close()
        if tmp:
            return tmp[0], tmp[1]
        return None, None
        
    def get_school_tech_name(self, school_id, rank = 1):
        c = self.db_conn.cursor()
        c.execute('''select name from school_techs
                     where school_uuid=? and rank=?''', [school_id, rank])
        tmp = c.fetchone()
        c.close()
        return tmp[0] if tmp else ""
       
