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
import models
import rules
import md5
from datetime import datetime

class FDFExporter(object):
    def __init__(self):
        self.model  = None
        self.form   = None
        
    def set_model(self, model):
        self.model = model
               
    def set_form(self, form):
        self.form = form
        
    def export(self, io):
        self.export_header(io)
        self.export_body  (io)
        self.export_footer(io)
        
    def export_header(self, io):
        io.write("%FDF-1.2\n%????\n1 0 obj \n<< /FDF << /Fields [ ")
        
    def export_body(self, io):
        pass
        
    def export_footer(self, io):
        hash_ = md5.new()
        hash_.update(str(datetime.now()))
        io.write(str.format("] \n/F (dummy.pdf) /ID [ <{0}>\n] >>",
                 hash_.hexdigest()))
        io.write(" \n>> \nendobj\ntrailer\n")
        io.write("<<\n/Root 1 0 R \n\n>>\n%%EOF\n")
    
    def export_field(self, key, value, io):
        if type(value) == type(True):
            io.write(str.format("<< /V /{1} /T({0})>>",
                 key, 'Yes' if value else 'No'))
        else:
            io.write(str.format("<< /V({1}) /T({0})>>",
                 key, value))
                 
    # HELPERS                    
                 
    def get_clan_name(self):
        return self.form.cb_pc_clan.currentText()
        
    def get_family_name(self):
        return self.form.cb_pc_family.currentText()
        
    def get_school_name(self):
        return self.form.cb_pc_school.currentText()
                
    def get_exp(self):
        return '%s / %s' % (self.model.get_px(), self.model.exp_limit)
                        

def zigzag(l1, l2):    
    def _zigzag(l1_, l2_):
        rl = []
        i = 0
        for i in xrange(0, len(l2_)):
            rl.append(l1_[i])
            rl.append(l2_[i])
        return rl + l1_[i:]
        
    if len(l1) >= len(l2):
        return _zigzag(l1,l2)
    return _zigzag(l2, l1)
                        
class FDFExporterAll(FDFExporter):
    def __init__(self):
        super(FDFExporterAll, self).__init__()
        
    def export_body(self, io):
        m = self.model
        f = self.form
        
        fields = {}
        fields['NAME'   ] = m.name
        fields['CLAN'   ] = self.get_clan_name   ()
        fields['RANK'   ] = m.get_insight_rank   ()
        fields['FAMILY' ] = self.get_family_name ()
        fields['SCHOOL' ] = self.get_school_name ()
        fields['EXP'    ] = self.get_exp         ()
        fields['INSIGHT'] = m.get_insight        ()
        
        # TRAITS AND RINGS
        for i in xrange(0, 8):
            fields[models.attrib_name_from_id(i).upper()] = m.get_attrib_rank(i)
        for i in xrange(0, 5):
            fields[models.ring_name_from_id(i).upper()] = m.get_ring_rank(i)
        
        # HONOR, GLORY, STATUS, TAINT       
        hvalue, hdots = rules.split_decimal(m.get_honor ())
        gvalue, gdots = rules.split_decimal(m.get_glory ())
        svalue, sdots = rules.split_decimal(m.get_status())
        tvalue, tdots = rules.split_decimal(m.get_taint ())
        
        fields['HONOR' ] = hvalue
        fields['GLORY' ] = gvalue
        fields['STATUS'] = svalue
        fields['TAINT' ] = tvalue
        
        for i in xrange(1, hdots*10+1):
            fields['HONOR_DOT.%d' % i ]  = True

        for i in xrange(1, gdots*10+1):
            fields['GLORY_DOT.%d' % i ]  = True

        for i in xrange(1, sdots*10+1):
            fields['STATUS_DOT.%d' % i]  = True

        for i in xrange(1, tdots*10+1):
            fields['TAINT_DOT.%d' % i ]  = True
            
        # INITIATIVE
        fields['INITIATIVE_BASE'] = f.tx_base_init.text()
        fields['INITIATIVE_MOD' ] = f.tx_mod_init .text()
        fields['INITIATIVE_CUR' ] = f.tx_cur_init .text()
        
        # TN / RD
        fields['TN_BASE'] = m.get_base_tn ()
        fields['TN_CUR' ] = m.get_cur_tn  ()
        fields['BASE_RD'] = m.get_base_rd ()
        fields['CUR_RD' ] = m.get_full_rd ()
        
        # ARMOR
        fields['ARMOR_TYPE' ] = m.get_armor_name   ()
        fields['ARMOR_TN'   ] = m.get_armor_tn     ()
        fields['ARMOR_RD'   ] = m.get_armor_rd     ()
        fields['ARMOR_NOTES'] = m.get_armor_desc   ()
        
        # WOUNDS
        w_labels = ['HEALTHY', 'NICKED', 'GRAZED', 
                    'HURT', 'INJURED', 'CRIPPLED',
                    'DOWN', 'OUT']
        for i in xrange(0, len(w_labels)):
            fields[w_labels[i]] = str(m.get_health_rank(i))
            
        fields['WOUND_HEAL_BASE'] = (m.get_attrib_rank(models.ATTRIBS.STAMINA)*2
                                     + m.get_insight_rank())
        #fields['WOUND_HEAL_MOD' ] = ''
        fields['WOUND_HEAL_CUR' ] = fields['WOUND_HEAL_BASE']
        
        # SKILLS
        idx = 1
        count = min(23, len(f.sk_view_model.items))
        for i in xrange(1, count+1):
            sk = f.sk_view_model.items[i-1]
            fields['SKILL_IS_SCHOOL.%d' % i] = sk.is_school
            fields['SKILL_NAME.%d'    % i  ] = sk.name
            fields['SKILL_RANK.%d'    % i  ] = sk.rank
            fields['SKILL_TRAIT.%d'   % i  ] = sk.trait
            fields['SKILL_EMPH_MA.%d' % i  ] = ', '.join(sk.emph)            
        
        # MERITS AND FLAWS
        merits = f.merits_view_model.items
        flaws  = f.flaws_view_model .items
        
        count = min(17, len(merits))
        for i in xrange(1, count+1):
            merit = merits[i-1]
            fields['ADVANTAGE_NM.%d' % i] = merit.name
            fields['ADVANTAGE_PT.%d' % i] = abs(merit.cost)

        count = min(17, len(flaws))
        for i in xrange(1, count+1):
            flaw = flaws[i-1]
            fields['DISADVANTAGE_NM.%d' % i] = flaw.name
            fields['DISADVANTAGE_PT.%d' % i] = abs(flaw.cost)
            
        # WEAPONS
        melee_weapons = f.melee_view_model .items
        range_weapons = f.ranged_view_model.items
        wl = zigzag(melee_weapons, range_weapons)
        count = min(2, len(wl))
        for i in xrange(1, count+1):
            weap = wl[i-1]
            fields['WEAP_TYPE.%d'  % i] = weap.name
            if weap.base_atk != weap.max_atk:
                fields['WEAP_ATK.%d'   % i] = weap.base_atk + "/" + weap.max_atk
            else:
                fields['WEAP_ATK.%d'   % i] = weap.base_atk
            if weap.base_dmg != weap.max_dmg:
                fields['WEAP_DMG.%d'   % i] = weap.base_dmg + "/" + weap.max_dmg
            else:
                fields['WEAP_DMG.%d'   % i] = weap.base_dmg                
            fields['WEAP_NOTES.%d' % i] = weap.desc
            
        # ARROWS
        arrows        = f.arrow_view_model .items
        count = min(5, len(arrows))
        for i in xrange(1, count+1):
            ar = arrows[i-1]
            fields['ARROW_TYPE.%d'  % i] = ar.name.replace('Arrow', '')
            fields['ARROW_DMG.%d'   % i] = ar.dr
            fields['ARROW_QTY.%d'   % i] = ar.qty
                    
        # EXPORT FIELDS    
        for k in fields.iterkeys():
            self.export_field(k, fields[k], io)
            
