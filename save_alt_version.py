#import bpy

from . import spamhelper

""" save as alternative type version of an existing asset.
    create a new asset based on existing asset.
"""

class save_alt_version(spamhelper.SaveToSpamHelper):

    def publish_alternative(self, name, comment):
        print ('was decided to publish alternative version')
        import os
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
            
        if sc_or_lib:
            container_type = 'shot'
        else:
            container_type = 'library'
        
        
        # verifica se gia esiste il asset con questo nome
        new_asset_path = dict(asset_path)
        #new_asset_path['category'] = 'texture'
        def get_cat_ext():
            category_tuple = spamhelper.get_all_categories()
            for i in category_tuple:
                if i[1] == new_asset_path['category']:
                    return i[0]
        category_ext = get_cat_ext()
        new_asset_path['name'] = (
                        new_asset_path['name'][:new_asset_path['name'].rfind('.')].replace(category_ext, '') +
                        '_'+self.name_sufix + category_ext +'.' + new_asset_path['ext'])
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
                        new_asset_path['category'], new_asset_path['name'], comment=self.comment )
        else:
            print ('asset with this name exist')
            return {'FINISHED'}

        result = self.logindata.conn.asset.checkout(
                            new_asset_path['project'], new_asset_id)
        
        
        new_main_file_path = ''
        if sc_or_lib:
            new_main_file_path=os.path.join(self.logindata.repository+'/',
                    new_asset_path['project'], 'scenes', new_asset_path['scene'],
                    new_asset_path['shot'], new_asset_path['category'], new_asset_path['name'])
        else:
            new_main_file_path = os.path.join(self.logindata.repository+'/', new_asset_path['project'], container_type)
            new_main_file_path = os.path.join(new_main_file_path, *new_asset_path['lib_groups'])
            new_main_file_path = os.path.join(new_main_file_path, new_asset_path['category'], new_asset_path['name'])
            
        for i in range(10):
            if not hasattr(self, 'save_as_main_file'): break
            self.save_as_main_file(filepath=new_main_file_path)
            break
            
        # save_dependencies
        self.save_dependency_assets(asset_path=new_asset_path)
        # save main_file
        if hasattr(self, 'save_main_file'):
            self.save_main_file(filepath = new_main_file_path)#main_file_path)
                            
        result = self.logindata.conn.upload(open(new_main_file_path, 'rb'))
        
        result = self.logindata.conn.asset.publish(
                            new_asset_path['project'], new_asset_id, new_main_file_path[new_main_file_path.rfind('/')+1:])
        
        if (self.submit_for_rev):
            result = self.logindata.conn.asset.submit(new_asset_path['project'],
                                new_asset_id, comment=self.comment)
        if (self.release):
            result = self.logindata.conn.asset.release(new_asset_path['project'],
                                new_asset_id)
        elif self.switch_to:
            for i in range(10):
                if not hasattr(self, 'open_main_file'): break
                result = self.logindata.conn.asset.release(asset_path['project'],
                                asset_id)
                self.open_main_file(filepath=new_main_file_path)
                                    
                break
        else:
            for i in range(10):
                if not hasattr(self, 'open_main_file'): break
                self.open_main_file(filepath=main_file_path)
                                    
                break

