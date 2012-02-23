#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os

from gimpfu import *
import os.path

import sys

sys.path.append(os.path.join(gimp.plug_in_directory,'plug-ins'))

import helpfiles
from helpfiles import spamclient, save_new_version, logintospam, save_alt_version, spamhelper


gettext.install("gimp20-python", gimp.locale_directory, unicode=True)

class mytestclass(save_alt_version.save_alt_version,
                save_new_version.save_new_version):
                
    logindata = logintospam.logindata()
    def pyslice(self, image, drawable, action, altname, new_type, release, revision):

        # an object that handle all connections to spam server
        
        
        filename = image.filename
        
        print (filename)
        print (image.ID)
        
        if filename:
            
            self.file_path = filename
            main_file_path = self.file_path
                
            if action == 'new':
                # publish a new version
                self.actions = '0'
                img_name =main_file_path[main_file_path.rfind('/')+1:main_file_path.rfind('.')]
                img_ext = main_file_path[main_file_path.rfind('.')+1:]
                if img_ext != 'xcf':
                    image.merge_visible_layers(2)
                    #pdb.gimp_file_save(image, drawable, main_file_path, main_file_path)
                #else:
                pdb.gimp_file_save(image, image.active_drawable, filename, filename)
                
                sc_or_lib = self.scene_or_library()
                asset_path = self.get_asset_path()
                asset_id, shot_id = self.recreate_asset_id()
                
                result = self.logindata.conn.asset.get(asset_path['project'],
                                asset_id)
                owner = None
                if result['owner']:
                    if result['owner']['user_name']:
                        owner = result['owner']['user_name']
                if not owner or owner != self.logindata.name:
                    print ('you don\'t own this asset')
                    return 1
                
                print (asset_id, shot_id)
                
                result = self.logindata.conn.upload(open(main_file_path, 'rb'))
                result = self.logindata.conn.asset.publish(asset_path['project'],
                                asset_id, main_file_path)
                                
                if revision:
                    result = self.logindata.conn.asset.submit(asset_path['project'],
                                asset_id)
                if release:
                    result = self.logindata.conn.asset.release(asset_path['project'],
                                asset_id)          
                
            elif action == 'alt':
                
                
                # publish an alternative asset
                self.actions = '1'
                img_name =main_file_path[main_file_path.rfind('/')+1:main_file_path.rfind('.')]
                img_ext = main_file_path[main_file_path.rfind('.')+1:]
                self.alternative_name = img_name.replace('_TEX', '') + '_' +altname #+ new_type
                
                new_main_file_path = main_file_path[:main_file_path.rfind('/')+1] + self.alternative_name + '_TEX.' + new_type
                
                image2 = image.duplicate()
                image2.merge_visible_layers(2)
                #new_file_name = filename[:filename.rfind('.')+1]+new_type
                #pdb.file_png_save(image2, image2.active_drawable, filename+'.png', filename+'.png', False, 9, True, False, False, False, True)
                #pdb.gimp_file_save(image2, image2.active_drawable, new_main_file_path, new_main_file_path)
                pdb.file_png_save(image2, image2.active_drawable, new_main_file_path, new_main_file_path, False, 9, True, False, False, False, True)
                
                sc_or_lib = self.scene_or_library()
                asset_path = self.get_asset_path()
                asset_id, shot_id = self.recreate_asset_id()
                
                result = self.logindata.conn.asset.get(asset_path['project'],
                                asset_id)
                owner = None
                if result['owner']:
                    if result['owner']['user_name']:
                        owner = result['owner']['user_name']
                if not owner or owner != self.logindata.name:
                    print ('you don\'t own this asset')
                    return 1
                if sc_or_lib:
                    container_type = 'shot'
                else:
                    container_type = 'library'
                
                
                # verifica se gia esiste il asset con questo nome
                new_asset_path = dict(asset_path)
                #new_asset_path['category'] = 'texture'
                new_asset_path['name'] = self.alternative_name + '_TEX.'+ new_type
                new_asset_id, new_shot_id = self.recreate_asset_id(asset_path=new_asset_path)
                
                asset_exist = True
                try:
                    result = self.logindata.conn.asset.get(new_asset_path['project'],
                                new_asset_id)
                except:
                    asset_exist = False
                    
                if not asset_exist:
                    result = self.logindata.adminconn.asset.new(
                                new_asset_path['project'], container_type, shot_id,
                                new_asset_path['category'], new_asset_path['name'])
                else:
                    print ('asset with this name exist')
                    return 1

                result = self.logindata.conn.asset.checkout(
                                    new_asset_path['project'], new_asset_id)
                                    
                result = self.logindata.conn.upload(open(new_main_file_path, 'rb'))
                
                result = self.logindata.conn.asset.publish(
                                    new_asset_path['project'], new_asset_id, new_main_file_path[new_main_file_path.rfind('/')+1:])
                
                if revision:
                    result = self.logindata.conn.asset.submit(new_asset_path['project'],
                                        new_asset_id)
                if release:
                    result = self.logindata.conn.asset.release(new_asset_path['project'],
                                        new_asset_id)
            

obj = mytestclass()
pyslice = obj.pyslice            


register(
    "python-fu-savetospam", # name
    "Publish current Image to SPAM", # blurb
    "Publish current Image to SPAM", # help
    "Mr. Petru", # autor
    "Mr. Petru", # copyright
    "2012", # date
    _("_Savetospam..."), # menupath
    "*", # image type
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
        (PF_RADIO, "action", _("Publish:"), "new", (("new version", "new"), ("new asset", "alt"))),
        (PF_STRING, "altname", _("Name for alternative version"), ""),
        (PF_RADIO, "new_type", _("Select new type:"), "jpg", (("JPEG", "jpg"), ("PNG", "png"), ("TIFF", "tif"), ("XCF", "xcf"))),
        (PF_TOGGLE, "release",  _("Release current asset"), False),
        (PF_TOGGLE, "revision",  _("Submit current asset for revision"), False),
    ],
    [],
    pyslice,
    #menu="<Image>/Filters/Web",
    menu="<Image>/File",
    domain=("gimp20-python", gimp.locale_directory)
    )

main()
