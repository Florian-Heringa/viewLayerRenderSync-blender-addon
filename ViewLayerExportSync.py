bl_info = {
    "name" : "View Layer Export Sync",
    "blender": (3, 2, 2),
    "version": (1, 0, 0),
    "category": "System",
    "warning": "Only tested with a single scene",
    "internal_name": "vles"
}

import bpy
from bpy.props import StringProperty, BoolProperty

# Requirements:
#   AddonPreferences =>
#       Reset All
#       Default render path

#   Additional menu between [ ] Stereoscopy and Output
#       A row for each view layer, and an additional row for editing the associated path

class viewLayerExportSyncPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    defaultRenderPath: StringProperty(
        name="Default Render Path",
        default="//renders",
        description="Select the defulat filepath whenever a new view layer is added",
        subtype="DIR_PATH",
        )
    
    dataIsInitialised: BoolProperty(
        name="Data is initialised",
        default=False,
    )
        
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "defaultRenderPath")
        row = layout.row()
        row.operator(bl_info["internal_name"] + ".initialise")
        row.operator(bl_info["internal_name"] + ".reset")
        # Not implemented yet
        ## row.operator(bl_info["internal_name"] + ".sync")
    
class VLES_OT_initialise(bpy.types.Operator):
    
    bl_idname = bl_info["internal_name"] + ".initialise"
    bl_label = "Initialise"
    bl_option = {"REGISTER"}
    
    def execute(self, context):
        
        settings = context.preferences.addons[__name__].preferences
        
        if not settings.dataIsInitialised:
            settings.dataIsInitialised = True
        else:
            return {"FINISHED"}
        
        print(" ".join([l.name for l in context.scene.view_layers]))
        
        scene = context.scene
        
        for viewLayer in scene.view_layers:
            n = scene.viewLayerFilePaths.add()
            n.viewLayerName = viewLayer.name
            n.path = settings.defaultRenderPath
            
        print(" ".join([str(item) for item in context.scene.viewLayerFilePaths]))
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return self.execute(context)
        
    
class VLES_OT_reset(bpy.types.Operator):
    
    bl_idname = bl_info["internal_name"] + ".reset"
    bl_label = "Reset"
    bl_option = {"REGISTER"}
    
    def execute(self, context):
        context.scene.viewLayerFilePaths.clear()
        context.preferences.addons[__name__].preferences.dataIsInitialised = False
        # TODO : Change this to something non-ridiculous
        eval(f"bpy.ops.{bl_info['internal_name']}.initialise")()
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return self.execute(context)
    
class VLES_OT_sync(bpy.types.Operator):
    
    bl_idname = bl_info["internal_name"] + ".sync"
    bl_label = "Sync"
    bl_option = {"REGISTER"}
    
    def execute(self, context):
        # TODO : this operator should be able to keep the view layers synched 
        # with the data mapping to a path. For now, recommendation is to
        # define all view layers you will need and then reset the mappings manually.
        # This does require to re-enter the paths (for now)
        print("NOT IMPLEMENTED YET")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return self.execute(context)

# This function was supposed to be registered as
#       bpy.app.handlers.render_init.append(setRenderPath)
# but this does not work since the callback is not sufficiently
# context aware to be able to resolve the selected view layer
def setRenderPath(scene):
    newPath = findPathForViewLayer(bpy.context.view_layer.name)
    if newPath:
        scene.render.filepath = newPath

# Therefore this needs to be checked in another timed callback function
# that is run every 2 seconds
# This function will also set all view layers to not be used for rendering
# apart from the one that is currently selected     
def updatePaths():
    newPath = findPathForViewLayer(bpy.context.view_layer.name)
    if newPath:
        bpy.context.scene.render.filepath = newPath
    for view_layer in bpy.context.scene.view_layers:
        view_layer.use = True if view_layer.name == bpy.context.view_layer.name else False
    return 2.0

# Helper function to find the correct view layer to path mapping    
def findPathForViewLayer(view_layer_name):
    mapping = bpy.context.scene.viewLayerFilePaths   
    for item in mapping:
        if item.viewLayerName == view_layer_name:
            return item.path
   
class VLES_PT_path_menu(bpy.types.Panel):
    bl_label = "ViewLayerSync"
    bl_idname = "VIEW3D_PT_ViewLayer"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "View Layer Sync"
        
    def draw(self, ctx):
        
        layout = self.layout
        
        for viewLayerMapping in ctx.scene.viewLayerFilePaths:
            row = layout.row()
            row.label(text=f"{viewLayerMapping.viewLayerName}")
            row = layout.row()
            row.prop(viewLayerMapping, "path")
    
class viewLayerFilePath(bpy.types.PropertyGroup):
    viewLayerName: StringProperty(name="viewLayer")
    path: StringProperty(name="Path", description="File Path", subtype="DIR_PATH")
    # TODO => Add name of the view layer to this struct as a general interface, also add methods to
    # overarching property to search through
    
    def __repr__(self):
        return f"{self.viewLayerName}=>{self.path}"
    
    def __str__(self):
        return self.__repr__()
    
classes = [
    viewLayerFilePath,
    viewLayerExportSyncPreferences,
    VLES_PT_path_menu,
    VLES_OT_initialise,
    VLES_OT_reset,
    VLES_OT_sync,
]

#########################################################################
##
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.viewLayerFilePaths = bpy.props.CollectionProperty(
        type=viewLayerFilePath,
        name="View Layer File Paths",
        description="A collection of combinations of viewlayers with paths",
    )
    
    bpy.app.timers.register(updatePaths)
    
def unregister():
    
    del bpy.types.Scene.viewLayerFilePaths
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.app.timers.unregister(updatePaths)

    
if __name__ == "__main__":
    register()