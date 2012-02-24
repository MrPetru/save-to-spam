import bpy
from . import spamhelper
from . import blender_helper

"""" create new asset """

class save_new_asset(spamhelper.SaveToSpamHelper):
    
    def save_new_asset(self, spam_data):
        import os
        main_file_path = self.file_path
        #sc_or_lib = self.scene_or_library()
        #asset_path = self.get_asset_path()
        #asset_id, shot_id = self.recreate_asset_id()
        
        if self.scenes_or_library == '0':
            sc_or_lib = True
            container_type = 'shot'
        else:
            sc_or_lib = False
            container_type = 'library'
        
        def get_cat_name():
            category_tuple = spamhelper.get_all_categories()
            for i in category_tuple:
                if i[0] == self.category:
                    return i[1]
        category_name = get_cat_name()
        asset_path = dict()
        if sc_or_lib:
            asset_path['project'] = spam_data['selected_project']
            asset_path['scene'] = spam_data['selected_scene']
            asset_path['shot'] = spam_data['selected_shot']
            asset_path['category'] = category_name
            asset_path['name'] = self.new_name + self.category + '.blend'
        else:
            asset_path['project'] = spam_data['selected_project']
            asset_path['category'] = category_name
            asset_path['name'] = self.new_name + self.category +'.blend'
            tmp_list = []
            for element in spam_data['selected_libgr']:
                if element[0] != '':
                    tmp_list.append(element[0])
            asset_path['lib_groups'] = tmp_list
        
        asset_id, shot_id = self.recreate_asset_id(asset_path=asset_path)
        
        asset_exist = True
        try:
            result = self.logindata.adminconn.asset.get(asset_path['project'],
                        asset_id)
        except:
            asset_exist = False
            
        if not asset_exist:
            result = self.logindata.adminconn.asset.new(
                        asset_path['project'], container_type, shot_id,
                        asset_path['category'], asset_path['name'], comment=self.comment )
        else:
            bpy.ops.spamerror.message('INVOKE_DEFAULT', 
                type = "Error",
                message = 'asset with this name exist')
            return {'FINISHED'}
        
        result = self.logindata.conn.asset.checkout(
                            asset_path['project'], asset_id)
                            
        # save file to new location
        new_main_file_path = ''
        if sc_or_lib:
            new_main_file_path=os.path.join(self.logindata.repository+'/',
                    asset_path['project'], 'scenes', asset_path['scene'],
                    asset_path['shot'], asset_path['category'], asset_path['name'])
        else:
            new_main_file_path = os.path.join(self.logindata.repository+'/', asset_path['project'], container_type)
            new_main_file_path = os.path.join(new_main_file_path, *asset_path['lib_groups'])
            new_main_file_path = os.path.join(new_main_file_path, asset_path['category'], asset_path['name'])
            
        for i in range(10):
            if not hasattr(self, 'save_as_main_file'): break
            if not os.path.exists(new_main_file_path[:new_main_file_path.rfind('/')]):
               os.mkdir(new_main_file_path[:new_main_file_path.rfind('/')]) 
            self.save_as_main_file(filepath=new_main_file_path)
            break
        
        result = self.logindata.conn.upload(open(new_main_file_path, 'rb'))
        
        result = self.logindata.conn.asset.publish(
                            asset_path['project'], asset_id, new_main_file_path[new_main_file_path.rfind('/')+1:])
        
        if (self.submit_for_rev):
            result = self.logindata.conn.asset.submit(asset_path['project'],
                                asset_id, comment=self.comment)
        if (self.release):
            result = self.logindata.conn.asset.release(asset_path['project'],
                                asset_id)


