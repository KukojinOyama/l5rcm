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

import os
import json
import zipfile
import shutil 

class ManifestNotFound(Exception):
    def __init__(self, msg):
        super(ManifestNotFound, self).__init__(msg)
        
class InvalidDataPack(Exception):
    def __init__(self, msg):
        super(InvalidDataPack, self).__init__(msg)        

class DataPack(object):

    def __init__(self, archive_path):    
        self.authors  = []
        self.id       = None
        self.dsp_name = None
        self.language = None
        
        self.archive_path = archive_path
        
        # todo: look for "manifest" file in root directory
        # no manifest file == no valid archive
        # read manifest file and extract:
        # 1. data target language ( es. us_US )
        # no language field == culture invariant
        # read id, data will be extracted in a subdirectory named that way
        # other fields:
        # author
        # display_name
               
        with zipfile.ZipFile(archive_path, 'r') as dz:
            try:
                # search manifest
                manifest_info = dz.getinfo('manifest')
                manifest_fp   = dz.open(manifest_info)
                manifest_js   = json.load(manifest_fp)
                
                self.id       = manifest_js['id']
                if 'display_name' in manifest_js:
                    self.dsp_name = manifest_js['display_name']
                if 'language' in manifest_js:
                    self.language = manifest_js['language']
                if 'authors' in manifest_js:
                    self.authors = manifest_js['authors']                
            except:
                print('manifest not found!')
                raise ManifestNotFound('Not a valid Data pack file.')
    
    def export_to(self, data_path):        
        if not self.good():
            raise InvalidDataPack('Cannot extract. Not a valid Data pack file.')
            
        data_path = os.path.join(data_path, self.id)
        
        if not os.path.exists(data_path):
            os.makedirs(data_path)
            
        dest_dir = os.path.join(data_path, self.id)
            
        try:
            if os.path.exists(dest_dir):
                shutil.rmtree(dest_dir, ignore_errors=True)
        except:
            print("cannot delete old data pack")            
            
        try:       
            with zipfile.ZipFile(self.archive_path, 'r') as dz:
                dz.extractall(data_path)
        except:
            raise InvalidDataPack('Cannot extract. Not a valid Data pack file.')
        
    def good(self):
        return self.id is not None
                
    def __str__(self):
        return self.dsp_name or self.id
        
    def __unicode__(self):
        return self.dsp_name or self.id
        
    def __eq__(self, obj):
        return obj and hasattr(obj, 'id') and obj.id == self.id
        
def test():
    data = 'test.zip'
    importer = DataPack(data)
    print(importer.good())
    
    importer.export_to('./test_out')
    
if __name__ == '__main__':
    test()