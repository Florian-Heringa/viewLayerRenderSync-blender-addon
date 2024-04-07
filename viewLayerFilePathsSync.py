bl_info = {
    "name" : "View Layer Filepaths Sync",
    "blender": (3, 2, 2),
    "category": "System",
}

import bpy
from bpy.types import Operator, Panel, Menu
from bpy.props import StringProperty

import pip

import sys
import subprocess
from pathlib import Path

from collections import defaultdict

# def log_to_console(message: str):
#     bpy.ops.console.scrollback_append(text=message, type="INFO")
    
# def testHandler(*args):
#     print("Pre Render!")
#     print(args[0].view_layers)
#     print(bpy.context.scene.view_layers)
#     print(bpy.context.view_layer)

def renderPathSetter(scene):
    print(ViewLayerMenu.view_layer_mapping.items())
    print("SETTING TO")
    #print(bpy.context.scene.viewLayerFilePaths[ViewLayerMenu.view_layer_mapping[bpy.context.view_layer.name]].path)
    scene.render.filepath = "//temp"#bpy.context.scene.viewLayerFilePaths[ViewLayerMenu.view_layer_mapping[bpy.context.view_layer.name]].path
    
class ViewLayerMenu(bpy.types.Panel):
    bl_label = "ViewLayerSync"
    bl_idname = "VIEW3D_PT_ViewLayer"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    # Dictionary mapping the name of a view layer to an index in the collection property
    view_layer_mapping = {}
    # Dictionary mapping the name of a view layer to a file path
    view_layer_paths = defaultdict(lambda:"")
    
    def __init__(self):
        super().__init__()
        ## Set up initial 
        self.view_layer_mapping = {v: i for i, v in enumerate(bpy.context.scene.view_layers.keys())}
        for layer_name in bpy.context.scene.view_layers.keys():
            self.view_layer_paths[layer_name] = self.view_layer_paths[layer_name]
            
        
    def draw(self, ctx):
        
        #self.updatePaths(ctx)
        
        layout = self.layout
        scene = ctx.scene
        
        #for view_layer_name, view_layer_path in zip(view_layers.keys(), scene.viewLayerFilePaths):
        for view_layer_name, (i, item) in zip(ctx.scene.view_layers.keys(), enumerate(scene.viewLayerFilePaths)):
            row = layout.row()
            row.label(text=f"{view_layer_name}")#view_layer_name)
            row = layout.row()
            row.prop(item, "path")
        print(ctx.scene.view_layers.keys())
        print(scene.viewLayerFilePaths)
        print(self.view_layer_paths)
        
def updatePaths():
    
    # Check how many view layers there are
    current_num_view_layers = len(bpy.context.scene.view_layers.keys())
    stored_num_view_layers = len(bpy.context.scene.viewLayerFilePaths.keys())
    
    print(current_num_view_layers, stored_num_view_layers)
    
    # If new one has been made, add a new entry
    if current_num_view_layers > stored_num_view_layers:
        bpy.context.scene.viewLayerFilePaths.add()
        
    # If one has been deleted, figure out which one and remove
    if current_num_view_layers < stored_num_view_layers:
        print(set(bpy.context.scene.view_layers.keys()).difference(set(ViewLayerMenu.view_layer_mapping.keys())))
        i = ViewLayerMenu.view_layer_mapping[set(bpy.context.scene.view_layers.keys()).difference(set(ViewLayerMenu.view_layer_mapping.keys()))]
        bpy.context.scene.viewLayerFilePaths.remove(i)
    
    # Update paths, create new empty one if necessary
    for layer in bpy.context.scene.view_layers.keys():
        ViewLayerMenu.view_layer_paths[layer] = ViewLayerMenu.view_layer_paths[layer]
        
    return 2.0

class FilePathProperty(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty(name="Path", description="File Path", subtype="DIR_PATH")
    # TODO => Add name of the view layer to this struct as a general interface, also add methods to
    # overarching property to search through
    
def register():
    bpy.utils.register_class(FilePathProperty)
    bpy.utils.register_class(ViewLayerMenu)
    
    # Set up the storage of file paths as a scene type
    bpy.types.Scene.viewLayerFilePaths = bpy.props.CollectionProperty(
        type=FilePathProperty,
        name="View Layer File Paths",
        #description=...,
        #options=...,
        #update=...
    )
    
    bpy.app.timers.register(updatePaths, first_interval=1.0)
    
    bpy.app.handlers.render_pre.append(renderPathSetter)
    
    #bpy.app.handlers.render_pre.append(testHandler)
    
def unregister():
    bpy.utils.unregister_class(FilePathProperty)
    bpy.utils.unregister_class(ViewLayerMenu)
    #bpy.app.handlers.render_pre.remove(testHandler)
    del bpy.types.Scene.viewLayerFilePaths
    bpy.app.timers.unregister(updatePaths)
    
    bpy.app.handlers.render_pre.remove(renderPathSetter)
    
if __name__ == "__main__":
    register()