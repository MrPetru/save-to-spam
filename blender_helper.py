
import bpy
import os

#def get_all_images():
#    all_images_relative_path = []
#    for i in bpy.data.images:
#        if i.filepath[2:] not in all_images_relative_path:
#            all_images_relative_path.append (i.filepath[2:])

#    all_images_absolut_path = []
#    main_file_path = bpy.data.filepath
#    
#    work_dir = main_file_path[:main_file_path.rfind('/')]
#    
#    for fpath in all_images_relative_path:
#        #if not os.path.isabs(fpath):
#        fpath2 = os.path.normpath(os.path.join(work_dir, fpath))
#        if os.path.exists(fpath2):
#            if os.path.isfile(fpath2):
#                if fpath2 not in all_images_absolut_path:
#                    all_images_absolut_path.append(fpath2)
#    return (all_images_absolut_path)
    
def get_all_images():
    return bpy.data.images
    
    
class image_collection(list):
    """
    
    EXAMPLE OF USE
    
    images = bpy.data.images
    base_file = bpy.data.filepath
    
    new_location = '/home/petru/Desktop/logoblender.jpg'
    
    collection = image_collection(images, base_file)
    for i in collection:
        collection.set_new_path(i, new_location, base_file)
        #print (i.extension)
        
    """
    
    class new_file_type(list):
        
        def check_if_path_is_relative(self):
            if self.original_path[:2] == '//': return True
            else: return False
        
        def __init__(self, file_obj, base_file, new_path=''):
            self.file_obj = file_obj
            if new_path=='':
                self.original_path = self.file_obj.filepath
                self.extension = self.original_path[self.original_path.rfind('.')+1:]
                self.base_dir = base_file[:base_file.rfind('/')]
                self.append([self.original_path, self.absolute_path,
                            self.relative_path])
            else:
                self.original_path = new_path
                self.extension = self.original_path[self.original_path.rfind('.')+1:]
                self.base_dir = base_file[:base_file.rfind('/')]
                self.append([self.original_path, self.absolute_path,
                            self.relative_path])
                self.file_obj.filepath = self.relative_path 
        
        @property
        def absolute_path(self):
            import os
            if self.check_if_path_is_relative():
                # make it absolute
                absolute = self.original_path[2:]
                absolute = os.path.join(self.base_dir, absolute)
                absolute = os.path.normpath(absolute)                
                return absolute
            else: return self.original_path
            
        @property
        def relative_path(self):
            import os
            if not self.check_if_path_is_relative():
                # make it relative
                relative = os.path.relpath(self.original_path, start=self.base_dir)
                relative = '//'+relative
                return relative
            else: return self.original_path
            
    
    def __init__(self, images, main_file_path):
        for f in images:
            if f.type == 'IMAGE' and not f.library and f.source != 'SEQUENCE':
                import os
                tmp = self.new_file_type(f, main_file_path)
                if os.path.exists(tmp.absolute_path):
                    self.append(tmp)
            
    def set_new_path(self, nft_img, new_location, base_file):
        # nft_img = new file type image
        if nft_img.absolute_path != new_location and nft_img.relative_path != new_location:
            tmp_nft_img = self.new_file_type(nft_img.file_obj, base_file, new_path=new_location)
            nft_img  = tmp_nft_img
            

