#import bpy
#from bpy.props import StringProperty, BoolProperty
from hashlib import sha1
#from . import save_new_version, save_new_asset, save_alt_version

try:
    from . import blender_helper
except:
    print ("module blender_helper was not foud")
import os

class SaveToSpamHelper():
        
    def get_asset_path(self, file_path=''):
        """
        retunr a dictionary with the path of asset
        path is intended as path in the project tree
        """
        if file_path == '':
            file_path = self.file_path
        tmp = file_path.replace(self.logindata.repository+'/', '')
        tmp_list = tmp.split('/')
        asset_path = {}
        if self.scene_or_library():
            asset_path['project'] = tmp_list[0]
            asset_path['scene'] = tmp_list[2]
            asset_path['shot'] = tmp_list[3]
            asset_path['category'] = tmp_list[4]
            asset_path['name'] = tmp_list[5]
            asset_path['ext'] = asset_path['name'][asset_path['name'].rfind('.')+1:]
        else:
            lenght = len(tmp_list)
            lib_groups = []
            for i in range(lenght):
                if i == 0:
                    asset_path['name'] = tmp_list[lenght-1-i]
                    asset_path['ext'] = asset_path['name'][asset_path['name'].rfind('.')+1:]
                elif i == 1:
                    asset_path['category'] = tmp_list[lenght-1-i]
                elif lenght-1-i == 1:
                    # is library
                    pass
                elif lenght-1-i == 0:
                    asset_path['project'] = tmp_list[0]
                else:
                    # all lybrary groups
                    lib_groups.append(tmp_list[i])
            asset_path['lib_groups'] = lib_groups
            #print (asset_path['lib_groups'])        
        return asset_path
        
    def scene_or_library(self):
        if not self.actions == '2':
            tmp = self.file_path.replace(self.logindata.repository+'/', '')
            if tmp.split('/')[1] == 'scenes':
                # for scene
                return True
            else:
                # for library
                return False
        else:
            if self.scenes_or_library == '0':
                return True
            else:
                return False
            
    def recreate_asset_id(self, asset_path=''):## alt=0, asset_path=''):
        if asset_path == '':
            asset_path = self.get_asset_path()
        if self.scene_or_library():
            hashable = '%s-%s' % (asset_path['project'], asset_path['scene'])
            scene_id = sha1(hashable.encode('utf-8')).hexdigest()

            hashable = '%s-%s' % (scene_id, asset_path['shot'])
            shot_id = sha1(hashable.encode('utf-8')).hexdigest()

#            if alt: # publish alternative
#                hashable = '%s-%s-%s' % (shot_id, asset_path['category'],
#                                self.alternative_name)
#            else:
            hashable = '%s-%s-%s' % (shot_id, asset_path['category'],
                            asset_path['name'])
                                
            asset_id = sha1(hashable.encode('utf-8')).hexdigest()
            return (asset_id, shot_id)
        else:
            parent_id = ''
            for i, lib in enumerate(asset_path['lib_groups']):
                if i == 0:
                    voto = None
                    hashable = '%s-%s' % (voto, lib)
                    parent_id = sha1(hashable.encode('utf-8')).hexdigest()
                else:
                    hashable = '%s-%s' % (parent_id, lib)
                    parent_id = sha1(hashable.encode('utf-8')).hexdigest()
            
            hashable = '%s-%s-%s' % (parent_id, asset_path['category'], asset_path['name'])
            asset_id = sha1(hashable.encode('utf-8')).hexdigest()
            return (asset_id, parent_id)
        
    def get_file_path(self):
        tmp = self.file_path.replace(self.logindata.repository+'/', '')
        return (tmp)
        
        
    def save_dependency_assets(self, asset_path=None):
        
        main_file_path = self.file_path
        if asset_path:
            new_main_file_path = main_file_path[:main_file_path.rfind('/')+1]+asset_path['name']
            asset_path = self.get_asset_path(file_path=new_main_file_path)
            asset_id, shot_id = self.recreate_asset_id(asset_path=asset_path)
        else:
            asset_path = self.get_asset_path()
            asset_id, shot_id = self.recreate_asset_id()
            
        sc_or_lib = self.scene_or_library()

        if sc_or_lib:
            container_type = 'shot'
        else:
            container_type = 'library'
                

        # if SCENE
        if True:#sc_or_lib:
            images = blender_helper.get_all_images()
            collection = blender_helper.image_collection(images, main_file_path)
            
            for img in collection:
                img_name =img.original_path[img.original_path.rfind('/')+1:img.original_path.rfind('.')]
                img_ext = img.original_path[img.original_path.rfind('.')+1:]
                if img_name[img_name.rfind('_'):] in ['_TEX', '_PLT', '_DRW', '_MDL', '_RIG',
                            '_STB', '_PNT', '_AUD', '_LAY', '_ANI', '_FX', '_RND', '_CMP', '_PLN']:
                    continue
                
                # verifica se gia esiste il asset con questo nome
                new_asset_path = dict(asset_path)
                new_asset_path['category'] = 'texture'
                new_asset_path['name'] = img_name+'_TEX.'+img_ext
                new_asset_id, new_shot_id = self.recreate_asset_id(asset_path=new_asset_path)
                
                asset_exist = True
                try:
                    result = self.logindata.conn.asset.get(new_asset_path['project'],
                                new_asset_id)
                except:
                    asset_exist = False
                if not asset_exist:
                    result = self.logindata.adminconn.asset.new(
                                new_asset_path['project'], container_type, new_shot_id,
                                'texture', new_asset_path['name'] )
                result = self.logindata.conn.asset.checkout(
                            new_asset_path['project'], new_asset_id)
                result = self.logindata.conn.upload(open(img.absolute_path, 'rb'))
                result = self.logindata.conn.asset.publish(
                            new_asset_path['project'], new_asset_id, img_name+'.'+img_ext)
                            
                # subbmit for revision
                result = self.logindata.conn.asset.submit(proj=new_asset_path['project'],
                            asset_id=new_asset_id, sender=self.logindata.name, uploaded='',
                            receiver=None, comment='auto submitted from blender')
                # release
                result = self.logindata.conn.asset.release(new_asset_path['project'],
                                new_asset_id)
                                
                # set new path for images
                if sc_or_lib:
                    final_path = os.path.join(
                                self.logindata.repository,
                                new_asset_path['project'], 'scenes', new_asset_path['scene'],
                                new_asset_path['shot'], new_asset_path['category'],
                                new_asset_path['name'])
                else:
                    final_path = os.path.join(
                                self.logindata.repository,
                                new_asset_path['project'], 'library',
                                *new_asset_path['lib_groups'])
                                
                    final_path = os.path.join(final_path,
                                new_asset_path['category'],
                                new_asset_path['name'])
                            
                collection.set_new_path(img, final_path, main_file_path)
                
def get_all_categories():
#    result = self.logindata.adminconn.category.get_all()
#    categories = []
#    for c in result:
#        categories.append((c['naming_convention'][c['naming_convention'].find('+_')+1:c['naming_convention'].find('\\.')],c['name'], ''))
#    print (tuple(categories))
#        categories = [['design', '_DRW'], ['model', '_MDL'], ['texture', '_TEX'],
#                        ['rig', '_RIG'], ['storyboard', '_STB'], ['plate', '_PLT'],
#                        ['paint', '_PNT'], ['audio', '_AUD'],
#                        ['animatic', '_A2D'], ['animatic', '_A3D'],
#                        ['layout', '_LAY'], ['animation', '_ANI'], ['effects', '_FX'],
#                        ['render', '_RND'], ['compositing', '_CMP']]

    return ((('_MDL', 'model', ''),
                ('_RIG', 'rig', ''),
                ('_A2D', 'animatic', ''), ('_A3D', 'animatic', ''),
                ('_LAY', 'layout', ''),
                ('_ANI', 'animation', ''), ('_FX', 'effects', ''),
                ))
        
