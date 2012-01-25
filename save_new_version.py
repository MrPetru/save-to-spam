#import bpy

from . import spamhelper
import os

""" publish new version of exesting asset """

class save_new_version(spamhelper.SaveToSpamHelper):
    
    def publish_new_version(self):
        print ('was decided to publish new version')
        
        main_file_path = self.file_path
        sc_or_lib = self.scene_or_library()
        asset_path = self.get_asset_path()
        asset_id, shot_id = self.recreate_asset_id()
        
        # check if user own this asset
        result = self.logindata.conn.asset.get(asset_path['project'],
                                asset_id)
        owner = None
        if result['owner']:
            if result['owner']['user_name']:
                owner = result['owner']['user_name']
        if not owner or owner != self.logindata.name:
            print ('you don\'t own this asset')
            return {'FINISHED'}
        
        # create and submite all dependencies asset
        self.save_dependency_assets()
        
        # save main file
        if hasattr(self, 'save_main_file'):
            self.save_main_file(filepath = main_file_path)
        
        result = self.logindata.conn.asset.publish(asset_path['project'],
                                asset_id, main_file_path, comment=self.comment)
                                
        if (self.submit_for_rev):
            result = self.logindata.conn.asset.submit(asset_path['project'],
                                asset_id, comment=self.comment)
        if (self.release):
            result = self.logindata.conn.asset.release(asset_path['project'],
                                asset_id)

