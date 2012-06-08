bl_info = {
    "name": "Save to Spam",
    "author": "SparkDE",
    "version": (0, 1),
    "blender": (2, 6, 1),
    "api": 41226,
    "location": "Save_to_Spam",
    "description": "Save curent file to SPAM",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "System"}


if "bpy" in locals():
    import imp
    if "spamclient" in locals():
        imp.reload(spamclient)
        imp.reload(save_new_version)
        imp.reload(logintospam)
        imp.reload(save_alt_version)
        imp.reload(save_new_asset)
        


import bpy
from bpy.props import FloatVectorProperty
#from add_utils import AddObjectHelper, add_object_data
from mathutils import Vector

#from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, FloatProperty, BoolProperty, EnumProperty
from . import spamclient
from . import save_new_version, logintospam
from . import save_alt_version, save_new_asset, spamhelper

spam_data = dict(
            selected_project = '',
            selected_scene = '',
            selected_scene_id = '',
            selected_shot = '',
            selected_shot_id = '',
            selected_category = 'model',
            selected_libgr = [['', '']],
            )

# Save to Spam Operator
class SaveToSpam(bpy.types.Operator, save_alt_version.save_alt_version,
                save_new_version.save_new_version,
                save_new_asset.save_new_asset):
    """Save To Spam Operator,
       the main operator of addon
    """
    
    # an object that handle all connections to spam server
    logindata = logintospam.logindata()
    #helper = spamhelper.SaveToSpamHelper()
    save_main_file = bpy.ops.wm.save_mainfile
    file_path = bpy.data.filepath
    save_as_main_file = bpy.ops.wm.save_as_mainfile
    open_main_file = bpy.ops.wm.open_mainfile
    
    bl_idname = "wm.save_to_spam"
    bl_label = "Save to Spam (develop)"
    
    filename_ext = ".spam"
    filter_glob = StringProperty(default="*.spam", options={'HIDDEN'})
    
    new_name = StringProperty(
            name="Name",
            description="Name for new asset",
            #default = '' ,
            )
    
    name_sufix = StringProperty(
            name="Name sufix",
            description="sufix to add to new asset name",
            #default = '' ,
            )
            
    comment = StringProperty(
            name="Comment",
            description="Comment for alternative asset",
            default = '',
            )
            
    actions = EnumProperty(
            name="Select Action",
            items=(('0', "Publish", "Publish new version of current asset"),
                   ('1', "Alternative", "Add an alternative versione of this asset (will create new asset)"),
                   ('2', "New Asset", "Create new asset from current file"),
                   ),
            )
            
    category = EnumProperty(
            name="Asset Category",
            items=spamhelper.get_all_categories(),
            )
    #print (category)
    scenes_or_library = EnumProperty(
            name="Select Scenes or library",
            items=(('0', "scenes", "create new asset in scenes"),
                   ('1', "library", "create new asset in library"),
                   ),
            )
    
    submit_for_rev = BoolProperty(
            name="For revision",
            description="Send asset for reviosion to supervisor",
            default= False,
            )
    
    release = BoolProperty(
            name="Release",
            description="release asset",
            default= False,
            )
            
    switch_to = BoolProperty(
            name="Switch to ...",
            description="Switch to new created asset",
            default= False,
            )
            
    filepath = StringProperty(
            name="File Path",
            description="Filepath used for exporting the file",
            maxlen=1024,
            subtype='FILE_PATH',
            )
    check_existing = BoolProperty(
            name="Check Existing",
            description="Check and warn on overwriting existing files",
            default=True,
            options={'HIDDEN'},
            )

    # subclasses can override with decorator
    # True == use ext, False == no ext, None == do nothing.
    check_extension = None

    def invoke(self, context, event):
        import os
        #bpy.ops.wm.save_mainfile()
        #self.get_all_categories()
        if not self.filepath:
            blend_filepath = context.blend_data.filepath
            self.file_path = bpy.data.filepath
            if not blend_filepath:
                blend_filepath = "you don't need to insert a name"
            else:
                blend_filepath = os.path.splitext(blend_filepath)[0]

            self.filepath = blend_filepath

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        #layout.prop(self, "user_name")
        layout.label(text="Loged in as: "+ self.logindata.name)
        layout.prop(self, "actions", expand=True)
        if self.actions == '0':
            layout.label(text='Publish')
            row = layout.row()
            row.prop(self, "release")
            row.prop(self, "submit_for_rev")
            layout.prop(self, 'comment')
        if self.actions == '1':
            layout.label(text='Alternative')
            row = layout.row()
            layout.prop(self, 'name_sufix')
            layout.prop(self, 'comment')
            row.prop(self, "release")
            row.prop(self, "submit_for_rev")
            layout.prop(self, 'switch_to')
            
        if self.actions == '2':
            layout.label(text='New Asset')
            layout.menu("menuprojectselect",text=spam_data['selected_project'])
            layout.prop(self, "scenes_or_library", expand=True)
            if self.scenes_or_library == '0' and spam_data['selected_project'] != '':
                layout.label(text='scenes')
                layout.menu("menusceneselect",text=spam_data['selected_scene'])
                layout.menu("menushotselect",text=spam_data['selected_shot'])
                #layout.label(text='category is MODEL')
                layout.prop(self, "category")
                layout.prop(self, 'new_name')
                row = layout.row()
                row.prop(self, "release")
                row.prop(self, "submit_for_rev")
            elif self.scenes_or_library == '1' and spam_data['selected_project'] != '':
                layout.label(text='library')
                for i in range(len(spam_data['selected_libgr'])):
                    if (i > 0) and (i < 2):
                        row = layout.row()
                        row.label(text='Lib')
                        row.menu("menulibgrselect",text=spam_data['selected_libgr'][i][0])
                    elif (i > 1):
                        row = layout.row()
                        row.label(text='SubLib')
                        row.menu("menusublibgrselect",text=spam_data['selected_libgr'][i][0])
                    elif  i == 0:
                        pass
                if len(spam_data['selected_libgr']) == 1:
                    row = layout.row()
                    row.label(text='Lib')
                    row.menu("menulibgrselect",text=spam_data['selected_libgr'][0][0])
                elif len(spam_data['selected_libgr']) > 1:
                    row = layout.row()
                    row.label(text='next SubLib')
                    row.menu("menusublibgrselect",text=spam_data['selected_libgr'][0][0])
                #layout.label(text='category is MODEL')
                layout.prop(self, "category")
                layout.prop(self, 'new_name')
                layout.prop(self, 'comment')
                row = layout.row()
                row.prop(self, "release")
                row.prop(self, "submit_for_rev")
                            
            #layout.prop(self, "proj", expand=False)
    
    def check(self, context):
        # working when 
        return (True)
    
    def execute(self, context):
        # check for user data
        
#        bpy.ops.spamerror.message('INVOKE_DEFAULT', 
#                type = "Error",
#                message = 'Found one error!')
#        return {'FINISHED'}
        
        if self.logindata.name == None:
            return {'FINISHED'}

        if self.actions == '0':
            self.publish_new_version()#asset_data)
            
        if self.actions == '1':
            if self.name_sufix != '':
                self.publish_alternative(self.name_sufix, self.comment)
            else:
                print ('please insert a name')
            
        if self.actions == '2':
            print ('was decided to create new asset')
            self.save_new_asset(spam_data)
            
        return {'FINISHED'}


class MenuProjectSelect(bpy.types.Menu):
    bl_idname = "menuprojectselect"
    bl_label = "Select a Project"
    
    logindata = logintospam.logindata()
    def draw(self, context):
        
        print ('getting list of projects')
        
        result = self.logindata.adminconn.project.get_all()
        projects_list = []
        for p in result:
            if ('local-'+self.logindata.name) in p['user_ids']:
                projects_list.append(p['id'])
        
        layout = self.layout
        for p_name in projects_list:
            text = p_name  
            layout.operator("scene.select_project", text=text).selected_prj=text
            

class SelectProject_OP(bpy.types.Operator):
    '''Tooltip'''
    bl_idname = "scene.select_project"
    bl_label = "Save project Choise"
    
    selected_prj = bpy.props.StringProperty()
    def execute(self, context):
        spam_data['selected_libgr'] = [['', '']]
        spam_data['selected_project'] = self.selected_prj
        return {'FINISHED'}

       
class MenuSceneSelect(bpy.types.Menu):
    bl_idname = "menusceneselect"
    bl_label = "Select a  Scenet"
    logindata = logintospam.logindata()
    
    def draw(self, context):
        print ('getting list of Scenes')
        
        result = self.logindata.conn.scene.get_all(spam_data['selected_project'])    
        layout = self.layout
        for sc in result['scenes']:
            name = sc['name']
            sc_id = sc['id']
            sc_data = name+'_sep_'+sc_id
            layout.operator("scene.select_scene", text=name).scene_data=sc_data

class SelectScene_OP(bpy.types.Operator):
    '''Tooltip'''
    bl_idname = "scene.select_scene"
    bl_label = "Save scene Choise"
    
    scene_data = bpy.props.StringProperty()
    def execute(self, context):
        spam_data['selected_scene'],spam_data['selected_scene_id'] = self.scene_data.split('_sep_')
        return {'FINISHED'}
        
        
class MenuShotSelect(bpy.types.Menu):
    bl_idname = "menushotselect"
    bl_label = "Select a  Shot"
    logindata = logintospam.logindata()
    
    def draw(self, context):
        print ('getting list of Shot')
        
        result = self.logindata.conn.shot.get_all(
                        spam_data['selected_project'], spam_data['selected_scene'])
        #print (result)
        layout = self.layout
        for sh in result['shots']:
            name = sh['name']
            sh_id = sh['id']
            sh_data = name+'_sep_'+sh_id
            layout.operator("scene.select_shot", text=name).shot_data=sh_data

class SelectShot_OP(bpy.types.Operator):
    '''Tooltip'''
    bl_idname = "scene.select_shot"
    bl_label = "Save shot Choise"
    
    shot_data = bpy.props.StringProperty()
    def execute(self, context):
        spam_data['selected_shot'],spam_data['selected_shot_id'] = self.shot_data.split('_sep_')
        return {'FINISHED'}
        
class MenuLibgrSelect(bpy.types.Menu):
    bl_idname = "menulibgrselect"
    bl_label = "Select a  LibraryGroup"
    logindata = logintospam.logindata()
    
    def draw(self, context):
        print ('getting list of library groups')
        
        result = self.logindata.conn.libgroup.get_all(
                        spam_data['selected_project'])
        #print (result)
        layout = self.layout
        for l in result['libgroups']:
            name = l['name']
            l_id = l['id']
            l_data = name+'_sep_'+l_id
            layout.operator("scene.select_libgr", text=name).lib_data=l_data

class SelectLibgr_OP(bpy.types.Operator):
    '''Tooltip'''
    bl_idname = "scene.select_libgr"
    bl_label = "Save libgroup Choise"
    
    lib_data = bpy.props.StringProperty()
    def execute(self, context):
        spam_data['selected_libgr'] = [['', '']]
        spam_data['selected_libgr'].append(self.lib_data.split('_sep_'))
        return {'FINISHED'}
        
class MenuSubLibgrSelect(bpy.types.Menu):
    bl_idname = "menusublibgrselect"
    bl_label = "Select a  SubLibraryGroup"
    logindata = logintospam.logindata()
    
    def draw(self, context):
        print ('getting list of sublibrary groups')
        
        result = self.logindata.conn.libgroup.get_subgroups(
                        spam_data['selected_project'], spam_data['selected_libgr'][-1][1])
        #print (result)
        layout = self.layout
        for subl in result['libgroups']:
            name = subl['name']
            subl_id = subl['id']
            subl_data = name+'_sep_'+subl_id
            layout.operator("scene.select_sublibgr", text=name).sublib_data=subl_data

class SelectSubLibgr_OP(bpy.types.Operator):
    '''Tooltip'''
    bl_idname = "scene.select_sublibgr"
    bl_label = "Save sublibgroup Choise"
    
    sublib_data = bpy.props.StringProperty()
    def execute(self, context):
        spam_data['selected_libgr'].append(self.sublib_data.split('_sep_'))
        return {'FINISHED'}
        
class SpamMessageOperator(bpy.types.Operator):
    bl_idname = "spamerror.message"
    bl_label = "Message"
    type = StringProperty()
    message = StringProperty()
 
    def execute(self, context):
        self.report({'INFO'}, self.message)
        print(self.message)
        return {'FINISHED'}
 
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=200)
 
    def draw(self, context):
        self.layout.label("A message from SPAM")
        row = self.layout.split(0.25)
        row.label(self.type)
        row.label(self.message)
        print (self.message)
        row = self.layout.split(0.80)
        row.label("")

def menu_func(self, context):
    layout = self.layout
    layout.operator(SaveToSpam.bl_idname)
    layout.separator()

# Registration

def register():
    bpy.utils.register_class(SpamMessageOperator)
    bpy.utils.register_class(SelectProject_OP)
    bpy.utils.register_class(SelectScene_OP)
    bpy.utils.register_class(SelectShot_OP)
    bpy.utils.register_class(SelectLibgr_OP)
    bpy.utils.register_class(SelectSubLibgr_OP)
    bpy.utils.register_class(MenuProjectSelect)
    bpy.utils.register_class(MenuSceneSelect)
    bpy.utils.register_class(MenuShotSelect)
    bpy.utils.register_class(MenuLibgrSelect)
    bpy.utils.register_class(MenuSubLibgrSelect)
    bpy.utils.register_class(SaveToSpam)
    bpy.types.INFO_MT_file.prepend(menu_func)



def unregister():
    bpy.utils.unregister_class(SaveToSpam)
    bpy.types.INFO_MT_file.remove(menu_func)

if __name__ == "__main__":
    register()
    
