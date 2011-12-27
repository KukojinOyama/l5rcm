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
        io.write(str.format("<</T({0})/V({1})>>",
                 key, value))
                 
    # HELPERS                    
                 
    def get_clan_name(self):
        return self.form.cb_pc_clan.currentText()
        
    def get_family_name(self):
        return self.form.cb_pc_family.currentText()
        
    def get_school_name(self):
        return self.form.cb_pc_school.currentText()
        
    def get_fullname(self):
        return '%s %s' % (self.get_family_name(), self.model.name)
        
    def get_exp(self):
        return '%s / %s' % (self.model.get_px(), self.model.exp_limit)
                        
                 
class FDFExporterAll(FDFExporter):
    def __init__(self):
        super(FDFExporterAll, self).__init__()
        
    def export_body(self, io):
        m = self.model
        f = self.form
        
        fields = {}
        fields['NAME'   ] = self.get_fullname    ()
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
        
        for k in fields.iterkeys():
            self.export_field(k, fields[k], io)
            
