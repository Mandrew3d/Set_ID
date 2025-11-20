bl_info = {
    "name": "Set_ID",
    "author": "Mandrew3D",
    "version": (1, 5),
    "blender": (5, 0, 0),
    "location": "View3D > UI > Set-ID",
    "description": "Addon for setting ID names",
    "warning": "",
    "doc_url": "https://github.com/Mandrew3d/Set_ID",
    "category": "Mods",
}

import bpy, math, random, colorsys, os
import addon_utils
import requests
import re

from bpy.utils import register_class, unregister_class
from bpy.types import (
    Header,
    Menu,
    Panel,
    Operator,
)

    
#Slider
class Slider(bpy.types.PropertyGroup):
    col_id : bpy.props.IntProperty(name = "Collection ID", soft_min=0, soft_max=100, default=1)
    active_col_id : bpy.props.IntProperty(name = "Collection ID", soft_min=0, soft_max=100, default=1)


#Collections
class Collections_Props(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty(name = "", default="A")
    
    
#Set name index str
class Set_name_str(bpy.types.PropertyGroup):
    my_str : bpy.props.StringProperty(name = "", default="A")
    
    
#Set name index auto gal
class Set_name_aib(bpy.types.PropertyGroup):
    my_autg : bpy.props.BoolProperty(name = " Auto index", default=True )
    my_hide : bpy.props.BoolProperty(name = " Auto hide", default=True )

#FBX Settings

class SetID_Show_Settings(bpy.types.PropertyGroup):
    show_fbx_settings: bpy.props.BoolProperty(default=False)
    
class FbxExportSettings(bpy.types.PropertyGroup):

    # ОБЪЕКТЫ
    #use_selection: bpy.props.BoolProperty(default=False)
    #use_visible: bpy.props.BoolProperty(default=False)
    #use_active_collection: bpy.props.BoolProperty(default=False)
    #collection: bpy.props.StringProperty(default="")

    # МАСШТАБ
    global_scale: bpy.props.FloatProperty(default=1.0, min=0.001, max=1000.0)
    apply_unit_scale: bpy.props.BoolProperty(default=True)
    apply_scale_options: bpy.props.EnumProperty(
        items=[
            ("FBX_SCALE_NONE", "None", ""),
            ("FBX_SCALE_UNITS", "Units", ""),
            ("FBX_SCALE_CUSTOM", "Custom", ""),
            ("FBX_SCALE_ALL", "All", ""),
        ],
        default="FBX_SCALE_NONE"
    )

    # ПРОСТРАНСТВО
    use_space_transform: bpy.props.BoolProperty(default=True)
    bake_space_transform: bpy.props.BoolProperty(default=False)

    # ТИПЫ ОБЪЕКТОВ
    object_types: bpy.props.EnumProperty(
        items=[
            ("ARMATURE", "Armature", ""),
            ("CAMERA", "Camera", ""),
            ("EMPTY", "Empty", ""),
            ("LIGHT", "Light", ""),
            ("MESH", "Mesh", ""),
            ("OTHER", "Other", ""),
        ],
        options={'ENUM_FLAG'},
        default={'ARMATURE', 'CAMERA', 'EMPTY', 'LIGHT', 'MESH', 'OTHER'}
    )

    # МЕШ-ОПЦИИ
    use_mesh_modifiers: bpy.props.BoolProperty(default=True)
    use_mesh_modifiers_render: bpy.props.BoolProperty(default=True)

    mesh_smooth_type: bpy.props.EnumProperty(
        items=[
            ("OFF", "Normals Only", ""),
            ("FACE", "Face", ""),
            ("EDGE", "Edge", ""),
            ("SMOOTH_GROUP", "Smooth Group", ""),
        ],
        default="OFF"
    )

    colors_type: bpy.props.EnumProperty(
        items=[
            ("NONE", "None", ""),
            ("SRGB", "sRGB", ""),
            ("LINEAR", "Linear", ""),
        ],
        default="SRGB"
    )
    prioritize_active_color: bpy.props.BoolProperty(default=False)

    use_subsurf: bpy.props.BoolProperty(default=False)
    use_mesh_edges: bpy.props.BoolProperty(default=False)
    use_tspace: bpy.props.BoolProperty(default=False)
    #use_triangles: bpy.props.BoolProperty(default=False)
    use_custom_props: bpy.props.BoolProperty(default=False)

    # МЕТАДАННЫЕ (общие)
    use_metadata: bpy.props.BoolProperty(default=True)

    # ОСИ
    axis_forward: bpy.props.EnumProperty(
        items=[
            ("X", "X", ""), ("Y", "Y", ""), ("Z", "Z", ""),
            ("-X", "-X", ""), ("-Y", "-Y", ""), ("-Z", "-Z", "")
        ],
        default="-Z"
    )
    axis_up: bpy.props.EnumProperty(
        items=[
            ("X", "X", ""), ("Y", "Y", ""), ("Z", "Z", ""),
            ("-X", "-X", ""), ("-Y", "-Y", ""), ("-Z", "-Z", "")
        ],
        default="Y"
    )




    
#Low poly str
class Low_polystr(bpy.types.PropertyGroup):
    my_lpstr : bpy.props.StringProperty(name = "", default="low" )
#high poly str
class High_polystr(bpy.types.PropertyGroup):
    my_hpstr : bpy.props.StringProperty(name = "", default="high" )    
    
#Galochki LP and HP
class HpLP_gal(bpy.types.PropertyGroup):
    lp_gal : bpy.props.BoolProperty(name = " Low poly", default=True )
    lp_tris : bpy.props.BoolProperty(name = " Triangulate", default=False )
    hp_tris : bpy.props.BoolProperty(name = " Triangulate", default=False )
    
    hp_gal : bpy.props.BoolProperty(name = " High poly", default=True )     
    lp_gal_viz : bpy.props.BoolProperty(name = " Low poly Viz", default=True )
    hp_gal_viz : bpy.props.BoolProperty(name = " High poly Viz", default=True )           

class Path_m(bpy.types.PropertyGroup):
    exp_path : bpy.props.StringProperty(subtype="FILE_PATH", name = "", default="//")
    exp_pathmat : bpy.props.StringProperty(subtype="FILE_PATH", name = "", default="//")


def get_active_collection_name(): 
    name_c= ' '
    if bpy.context.scene.setid_collections:
        name_c = bpy.context.scene.setid_collections[bpy.context.scene.id_slider.active_col_id].name 
    return name_c

#fbx export func
def export_fbx(path: str, objects, use_triangulate):
    """
    Экспорт в FBX.
    path    — полный путь к файлу .fbx (строка)
    objects — итерируемая коллекция объектов для экспорта
    Параметры экспорта берутся из bpy.context.scene.fbx_settings
    """
    ctx = bpy.context
    scene = ctx.scene
    s = scene.fbx_settings  # напрямую

    prev_active = ctx.view_layer.objects.active
    prev_selected = list(ctx.selected_objects)
    path = path + '.fbx'
    try:
        # снять текущее выделение
        for o in prev_selected:
            o.select_set(False)

        # выделить объекты для экспорта
        objs = list(objects)
        for o in objs:
            o.select_set(True)

        # установить активный объект
        if objs:
            ctx.view_layer.objects.active = objs[0]

        # экспорт
        bpy.ops.export_scene.fbx(
            filepath=path,
            use_selection=True,
            use_visible=False,
            #collection=s.collection,

            global_scale=s.global_scale,
            apply_unit_scale=s.apply_unit_scale,
            apply_scale_options=s.apply_scale_options,

            use_space_transform=s.use_space_transform,
            bake_space_transform=s.bake_space_transform,

            object_types=s.object_types,

            use_mesh_modifiers=s.use_mesh_modifiers,
            use_mesh_modifiers_render=s.use_mesh_modifiers_render,

            mesh_smooth_type=s.mesh_smooth_type,
            colors_type=s.colors_type,
            prioritize_active_color=s.prioritize_active_color,

            use_subsurf=s.use_subsurf,
            use_mesh_edges=s.use_mesh_edges,
            use_tspace=s.use_tspace,
            use_triangles=use_triangulate,
            use_custom_props=s.use_custom_props,

            axis_forward=s.axis_forward,
            axis_up=s.axis_up,
        )

    finally:
        # снять выделение после экспорта
        for o in list(ctx.selected_objects):
            o.select_set(False)

        # восстановить прежнее выделение
        for o in prev_selected:
            if o.name in ctx.view_layer.objects:
                ctx.view_layer.objects[o.name].select_set(True)

        # восстановить активный объект
        if prev_active and prev_active.name in ctx.view_layer.objects:
            ctx.view_layer.objects.active = ctx.view_layer.objects[prev_active.name]
        else:
            ctx.view_layer.objects.active = None


        

#Open folder
def open_folder(self, context):
    path = os.path.abspath(self.path)
    
    os.startfile(path)

class Open_Folder(Operator):
    bl_idname = "setid.open_folder"
    bl_label = "Open Folder"
    
    path: bpy.props.StringProperty(name = 'Path', default = '' )
    
    def execute(self, context):
            
        open_folder(self, context)
        return {'FINISHED'}    

def increment_string(s: str) -> str:
    match = re.search(r"(\d+)$", s)
    
    # нет числа в конце → добавить "_1"
    if not match:
        return f"{s}_1"
    
    number_str = match.group(1)
    number = int(number_str) + 1
    new_number = str(number).zfill(len(number_str))  # сохраняем ведущие нули
    
    return s[:match.start()] + new_number



def create_collection(self,context):
    cols = context.scene.setid_collections
    if len(cols) > 0:
        new_name = increment_string(context.scene.setid_collections[len(cols)-1].name)
        new_col = context.scene.setid_collections.add()
        new_col.name = new_name
    else:
        new_col = context.scene.setid_collections.add()
        new_col.name = 'Object_1'

    
    
    
class Create_New_Collection(Operator):
    bl_idname = "setid.new_collection"
    bl_label = "Create New Collection"

    
    def execute(self, context):
        create_collection(self, context)
        return {'FINISHED'}

    
#Move Collection

def move_collection(self, context):
    scene = context.scene
    idx = self.col_id
    col = scene.setid_collections

    if not col or idx < 0 or idx >= len(col):
        return

    # вычисляем индекс для перемещения
    new_idx = idx - 1 if self.up else idx + 1
    if new_idx < 0 or new_idx >= len(col):
        return

    # копируем **только пользовательские свойства** PropertyGroup
    user_props = [k for k in col[idx].keys() if not k.startswith("_")]
    for prop_name in user_props:
        col[idx][prop_name], col[new_idx][prop_name] = col[new_idx][prop_name], col[idx][prop_name]


class Move_Id_Collection(Operator):
    bl_idname = "setid.move_id_collection"
    bl_label = "Move Collection"
     
    col_id : bpy.props.IntProperty(default = 0)
    up : bpy.props.BoolProperty(default = False)
    
    def execute(self, context):
        move_collection(self, context)
        return {'FINISHED'}

def delete_collection(self,context):
    col = self.col_id
    bpy.context.scene.id_slider.active_col_id = max(0,col -1)
    bpy.context.scene.setid_collections.remove(col)
    
        
class Delete_Collection(Operator):
    bl_idname = "setid.delete_collection"
    bl_label = "Remove Collection"
    
    col_id : bpy.props.IntProperty(default = 0)
    
    def execute(self, context):
        delete_collection(self, context)
        return {'FINISHED'}

def set_active_collection(self,context):
    col_id = self.col_id
    bpy.context.scene.id_slider.active_col_id = col_id
    
    
    
class Set_Active_Collection(Operator):
    bl_idname = "setid.set_collection"
    bl_label = "Set Active"

    col_id : bpy.props.IntProperty(default = 0)
    
    def execute(self, context):
        set_active_collection(self, context)
        return {'FINISHED'}    


#rename col
def rename_collection(self,context):
    col_id = self.col_id
    
    bpy.context.scene.setid_collections[col_id].name = self.new_name
    
    

class Rename_Collection(Operator):
    bl_idname = "setid.rename_collection"
    bl_label = "Rename Collection"

    col_id : bpy.props.IntProperty(default = 0)
    
    new_name: bpy.props.StringProperty(name="Name")
    
    
    def invoke(self, context, event):
        self.new_name = bpy.context.scene.setid_collections[self.col_id].name
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "new_name")    
    
    
    def execute(self, context):
        rename_collection(self, context)
        return {'FINISHED'} 
        
def move_to_collection(obj, collection_name: str):
    # Найти или создать коллекцию
    if collection_name in bpy.data.collections:
        col = bpy.data.collections[collection_name]
    else:
        col = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(col)

    # Удалить объект из всех текущих коллекций
    for c in obj.users_collection:
        c.objects.unlink(obj)

    # Добавить в нужную коллекцию
    col.objects.link(obj)
    
# low poly collection
def low_poly(self, context):


#Collection creation
    indexcol=bpy.context.scene.id_slider.active_col_id
    name_to_move = bpy.context.scene.setid_collections[indexcol].name
    namecollp="Low Poly_" + name_to_move
    
    for obj in bpy.context.selected_objects:
        move_to_collection(obj, namecollp)

    
class Low_poly(Operator):
    bl_idname = "lp.poly"
    bl_label = "Low Poly"

    def execute(self, context):
            
        low_poly(self, context)
        return {'FINISHED'}

# High poly collection
def high_poly(self, context):



#Collection creation
    indexcol=bpy.context.scene.id_slider.active_col_id
    name_to_move = bpy.context.scene.setid_collections[indexcol].name
    namecollp="High Poly_" + name_to_move
    
    for obj in bpy.context.selected_objects:
        move_to_collection(obj, namecollp)


    
class High_poly(Operator):
    bl_idname = "hp.poly"
    bl_label = "High Poly"

    def execute(self, context):
            
        high_poly(self, context)
        return {'FINISHED'}    
#LP Viz
def lpviz(self, context):
    indexcol=bpy.context.scene.id_slider.active_col_id
    name_to_vis = bpy.context.scene.setid_collections[indexcol].name
    colname="Low Poly_" + name_to_vis

    contcol = bpy.context.view_layer.layer_collection.children[colname].hide_viewport
    #hg = bpy.context.view_layer.layer_collection.children[colname].hide_get

    if contcol == True:
        bpy.context.scene.lp_g.lp_gal_viz = True
        bpy.context.view_layer.layer_collection.children[colname].hide_viewport = False
    else:
        bpy.context.scene.lp_g.lp_gal_viz = False
        bpy.context.view_layer.layer_collection.children[colname].hide_viewport = True
        
class LPCol_viz(Operator):
    bl_idname = "setid.lpviz"
    bl_label = "Show LP"
    


        
    def execute(self, context):
        lpviz(self, context)
        return {'FINISHED'}        
#HP Viz
def hpviz(self, context):
    indexcol=bpy.context.scene.id_slider.active_col_id
    name_to_vis = bpy.context.scene.setid_collections[indexcol].name
    colname="High Poly_" + name_to_vis
    

    contcol = bpy.context.view_layer.layer_collection.children[colname].hide_viewport

    if contcol == True:
        bpy.context.scene.lp_g.hp_gal_viz = True
        bpy.context.view_layer.layer_collection.children[colname].hide_viewport = False
    else:
        bpy.context.scene.lp_g.hp_gal_viz = False
        bpy.context.view_layer.layer_collection.children[colname].hide_viewport = True
        
class HPCol_viz(Operator):
    bl_idname = "setid.hpviz"
    bl_label = "Show HP"
    
        
    def execute(self, context):
        hpviz(self, context)
        return {'FINISHED'}   
    
#Set Name func

numb = 1


def set_name(self, context):
    namesn = str(bpy.context.scene.st_name.my_str)
    nl = str(bpy.context.scene.mesh_l.my_lpstr)
    nh = str(bpy.context.scene.mesh_h.my_hpstr)
    
    indexcol=bpy.context.scene.id_slider.col_id
    namecollp='Low Poly_' + str(bpy.context.scene.setid_collections[bpy.context.scene.id_slider.active_col_id].name)
    
    indexcol=bpy.context.scene.id_slider.col_id
    namecolhp='High Poly_' + str(bpy.context.scene.setid_collections[bpy.context.scene.id_slider.active_col_id].name)

    lpcoll = namecollp
    hpcoll = namecolhp
    
    bpy.context.scene.st_name.my_str
    
    #
    strok = bpy.context.scene.st_name.my_str
    leng = len(strok)

    i = 1
    printerlp = "Renamed: "
    printerhp = " "
    if bpy.context.scene.ai_b.my_autg == True:
        if leng != 0 :    
            if strok[leng-1].isdigit() == True:
             
                while strok[leng-i].isdigit() == True:
                    
                    i += 1

                    if (leng-i) < 0:
                        break
                i -=1
                ks = strok[-i:]
                nn = int(ks) + 1
                strok = strok[0:(leng)-i]
                strok += str(nn)
                bpy.context.scene.st_name.my_str = strok
            else:
                bpy.context.scene.st_name.my_str += "1"
        else:
            bpy.context.scene.st_name.my_str = "A1"  
    
    for obj in bpy.data.collections[str(lpcoll)].all_objects:
        if obj in bpy.context.selected_objects:
            obj.name = namesn + "_" + nl + "_1"
            printerlp += " " + obj.name
    for obj in bpy.data.collections[str(hpcoll)].all_objects:
        if obj in bpy.context.selected_objects:
            obj.name = namesn + "_" + nh + "_1"
            printerhp += " " + obj.name    
    if bpy.context.scene.ai_b.my_hide == True:
        bpy.ops.object.hide_view_set(unselected=False)
    
    self.report({'INFO'}, printerlp + printerhp)    #print(printerlp + printerhp)
 


class Set_name(Operator):
    bl_idname = "set.name"
    bl_label = "Set Names"

    def execute(self, context):
        set_name(self, context)
        return {'FINISHED'}



#Attach
def copy_name(self, context):
    actob = context.object
    selob = context.selected_objects
    aname = actob.name
    colname = actob.users_collection[0]
    
    for obj in selob:
        obj.name = aname
        curcols = obj.users_collection
        
        if colname not in curcols:
                
            colname.objects.link(obj)
            for col in curcols:
                col.objects.unlink(obj)
    #actob.name = aname
    print(colname.name)
        
 


class Copy_name(Operator):
    bl_idname = "set.copy_name"
    bl_label = "Attach"

    def execute(self, context):
        copy_name(self, context)
        return {'FINISHED'}


#Hide Named
def hide_named(self, context):
    #col_id = bpy.context.scene.id_slider.col_id
    name = get_active_collection_name()
    
    hp_col_name = 'High Poly_' + name
    lp_col_name = 'Low Poly_' + name
    
    hp_col = bpy.data.collections[hp_col_name]
    lp_col = bpy.data.collections[lp_col_name]
    
    for ob in hp_col.objects:
        if  bpy.context.scene.mesh_l.my_lpstr in ob.name:
            ob.hide_set(True)
            #print(ob.name)
    for ob in lp_col.objects:
        if bpy.context.scene.mesh_h.my_hpstr in ob.name:
            ob.hide_set(True)
    
    
class Hide_named(Operator):
    bl_idname = "setid.hide_named"
    bl_label = "Hide Named"

    def execute(self, context):
        hide_named(self, context)
        return {'FINISHED'}
    

def list_objects_in_collection(collection_name):
    collection = bpy.data.collections.get(collection_name)
    if collection is None:
        #print(f"Коллекция '{collection_name}' не найдена.")
        return []
    
    objects = [obj for obj in collection.objects]
    #print(f"Объекты в коллекции '{collection_name}': {objects}")
    return objects
        
def exp_fbx(context):
#export Lowpoly

    trislp = bpy.context.scene.lp_g.lp_tris
    trishp = bpy.context.scene.lp_g.hp_tris
    
    if bpy.context.scene.lp_g.lp_gal == True:
        indexcol = bpy.context.scene.id_slider.col_id 
        name = get_active_collection_name()
        namecollp = "Low Poly_" + name
        objects_to_exp = list_objects_in_collection(namecollp)

        path =  bpy.path.abspath(bpy.context.scene.path_s.exp_path)
        #collection = bpy.data.collections[namecollp]
        path = os.path.join(path, namecollp)
        export_fbx(path, objects_to_exp, trislp)
        
    if bpy.context.scene.lp_g.hp_gal == True:
        indexcol = bpy.context.scene.id_slider.col_id 
        
        name = get_active_collection_name()
        namecollp = "High Poly_" + name
        objects_to_exp = list_objects_in_collection(namecollp)
        
        path =  bpy.path.abspath(bpy.context.scene.path_s.exp_path)
        #collection = bpy.data.collections[namecollp]
        path = os.path.join(path, namecollp)
        
        export_fbx(path, objects_to_exp, trishp)

class Export_fbx(Operator):
    bl_idname = "ex.fbx"
    bl_label = "Export FBX"

    def execute(self, context):
            
        exp_fbx(context)
        return {'FINISHED'}

#Triangulate

def trian_obj(context):
    selob = bpy.context.selected_objects
    lensel = len(selob)

    chek = False
    ismod = 0
    if lensel != 0:
        for ob in bpy.context.selected_objects:
            if len(bpy.data.objects[ob.name].modifiers) !=0:
                for mod in bpy.data.objects[ob.name].modifiers:
                    
                    if mod.type == 'TRIANGULATE':
                        
                        ismod += 1

            else:
                
                ismod += 0
                        

    if ismod != lensel:
        if lensel != 0:
            for ob in bpy.context.selected_objects:
                chek = False
                for mod in bpy.data.objects[ob.name].modifiers:
                    if mod.type == 'TRIANGULATE':
                        chek = True


                if chek != True:
                    newmod = ob.modifiers.new(name="Triangulate", type='TRIANGULATE')
                    newmod.quad_method = 'BEAUTY'
                    
    
    else:
        if lensel != 0:
            for ob in bpy.context.selected_objects:
                for mod in  bpy.data.objects[ob.name].modifiers:
                    if mod.type == 'TRIANGULATE':
                        
                        bpy.data.objects[ob.name].modifiers.remove(ob.modifiers.get(mod.name))       


 

class Triang_obj(Operator):
    bl_idname = "ex.triang"
    bl_label = "Triangulate"

    def execute(self, context):
            
        trian_obj(context)
        return {'FINISHED'}

#Maps connector
def in_list(str_, words):
    for word in words:
        if word.lower() in str_.lower():
            return True
    return False


def maps_con(self, context):
    selob = bpy.context.selected_objects
    path = bpy.path.abspath(bpy.context.scene.path_s.exp_pathmat)
    exp = self.exp
#    fcol = []
#    for (root,dirs,files) in os.walk(path):

#        for names in files:
#            fcol.append(names)

    
    mats = []   
    for ob in selob:
        for mat in ob.material_slots:
            if mat.name not in mats:
                mats.append(mat.name)
    
    for ma in mats:
        #folder check
        #for 
        offsetx = 256
        offsety = 256 + 32
        material = bpy.data.materials[ma]
        mnt = material.node_tree
        mntn = material.node_tree.nodes
        
        #get principled BSDF
        princ = mntn["Principled BSDF"]
        startloc = princ.location
        #add nodes
        #Base color
        if "Base Color" not in mntn:
            bc= mntn.new('ShaderNodeTexImage')
            bc.label = "Base Color"
            bc.name = "Base Color"
            bc.location[0] = startloc[0]-offsetx*2
            bc.location[1] = startloc[1]-0
        else:
            bc = mntn["Base Color"]
        
        #ORM
        if "ORM" not in mntn:
            orm= mntn.new('ShaderNodeTexImage')
            orm.label = "Oclussion Roughness Metallic"
            orm.name = "ORM"
            orm.location[0] = startloc[0]-offsetx*2
            orm.location[1] = startloc[1]-offsety

        else:
            orm = mntn["ORM"]
        
        #AO
        if "AO" not in mntn:
            ao= mntn.new('ShaderNodeMixRGB')
            ao.label = "Ambient Oclussion"
            ao.name = "AO"
            ao.blend_type = 'MULTIPLY'
            ao.inputs[0].default_value = 1
            ao.location[0] = startloc[0]-offsetx*0.8
            ao.location[1] = startloc[1]
            ao.hide = True

        else:
            ao = mntn["AO"] 
                       
            #seperator ORM
        if "Seperate ORM" not in mntn:
            sorm= mntn.new('ShaderNodeSeparateRGB')
            sorm.label = "Seperate ORM"
            sorm.name = "Seperate ORM"
            sorm.location[0] = startloc[0]-offsetx*0.8
            sorm.location[1] = startloc[1]-offsety
            sorm.hide = True
            
        else:
            sorm = mntn["Seperate ORM"] 
             
         #Normal
        if "Normal" not in mntn:
            norm= mntn.new('ShaderNodeTexImage')
            norm.label = "Normal"
            norm.name = "Normal"
            norm.location[0] = startloc[0]-offsetx*2
            norm.location[1] = startloc[1]-offsety*2

        else:
            norm = mntn["Normal"]                 
            
            #FlipGreen
        if "FlipY" not in mntn:
            fy= mntn.new('ShaderNodeMixRGB')
            fy.label = "Flyp Y"
            fy.name = "FlipY"
            fy.blend_type = 'DIFFERENCE'
            fy.inputs[0].default_value = 1
            fy.inputs[2].default_value = [0, 1 , 0, 1]
            fy.location[0] = startloc[0]-offsetx*0.8
            fy.location[1] = startloc[1]-offsety*2.6
            fy.hide = True

        else:
            fy = mntn["FlipY"] 
            
            #add normal map node
        
        if "Normal Map" not in mntn:
            normm= mntn.new('ShaderNodeNormalMap')
            normm.label = "Normal Map"
            normm.name = "Normal Map"
            normm.location[0] = startloc[0]-offsetx*0.8
            normm.location[1] = startloc[1]-offsety*2

        else:
            normm = mntn["Normal Map"]          
        #add maps 

#NEW
        path = bpy.path.abspath(bpy.context.scene.path_s.exp_pathmat)

        dir = os.listdir(path)


        files = [file for file in dir if '.' in file]
        print(files)

                
        l_names = []

        color = ['base','color','diffuse','basecolor','albedo']
        mix = ['mix','combine','occlusionroughnessmetallic','pack']
        norm_map = ['normal','norm','directx','opengl','narmalmap']

        mat_name = ma

        for name in files:
            l_name = name.lower()
            l_mat = mat_name.lower()
            
            
            namebc = None
            nameorm = None
            namenorm = None
            if l_mat in l_name:
                l_name = l_name.replace(l_mat,'')    
                if in_list(l_name, color):
                    print(name)
                    namebc = name
                    if namebc not in bpy.data.images:
                        bc.image = bpy.data.images.load(path+namebc)
                    else:
                        bc.image = bpy.data.images[namebc]
                        bpy.data.images[namebc].reload()   
                                         
                if in_list(l_name, mix) or 'ORM' in name:
                    print(name)
                    nameorm = name
                    if nameorm not in bpy.data.images:
                        orm.image = bpy.data.images.load(path+nameorm)
                        bpy.data.images[nameorm].colorspace_settings.name = 'Non-Color'
                    else:
                        orm.image = bpy.data.images[nameorm]
                        bpy.data.images[nameorm].reload()
                                    
                if in_list(l_name, norm_map):
                    print(name)
                    namenorm = name
                    if namenorm not in bpy.data.images:
                        norm.image = bpy.data.images.load(path+namenorm)
                        bpy.data.images[namenorm].colorspace_settings.name = 'Non-Color'
                    else:
                        norm.image = bpy.data.images[namenorm]
                        bpy.data.images[namenorm].reload()

                    
        if exp == False:        
            #links
                #BC
            mnt.links.new(ao.inputs[1], bc.outputs[0])
                #AO
            mnt.links.new(princ.inputs[0], ao.outputs[0])
            mnt.links.new(ao.inputs[2], sorm.outputs[0])      
                #Sorm
            mnt.links.new(sorm.inputs[0], orm.outputs[0])
                #Rough
            mnt.links.new(princ.inputs[9], sorm.outputs[1])
                #Metall
            mnt.links.new(princ.inputs[6], sorm.outputs[2])
                #Normal
            mnt.links.new(princ.inputs[22], normm.outputs[0])
            mnt.links.new(normm.inputs[1], fy.outputs[0])  
                #Flip Y
            mnt.links.new(fy.inputs[1], norm.outputs[0])            
            #old links
        else:    
            mnt.links.new(princ.inputs[0], bc.outputs[0])
            mnt.links.new(princ.inputs[9], orm.outputs[0])   
            mnt.links.new(princ.inputs[22], normm.outputs[0])
            mnt.links.new(normm.inputs[1], norm.outputs[0])  
            mntn.remove(ao)
            mntn.remove(sorm)
            mntn.remove(fy)
            
class Maps_Con(Operator):
    bl_idname = "ex.mapscon"
    bl_label = "Connect"
    exp = False
    def execute(self, context):
        #exp = False    
        maps_con(self, context)
        return {'FINISHED'}

class Maps_Exp(Operator):
    bl_idname = "ex.mapsexp"
    bl_label = "For Export"
    exp = True 
    def execute(self, context):
        #exp = True    
        maps_con(self, context)
        return {'FINISHED'}
#Random colors


def random_col(self,context):
    selmats = []
    for sel in bpy.context.selected_objects:
            addmat = bpy.data.objects[sel.name].material_slots
            for names in addmat:
                selmats.append(names.name)
    count = len(selmats)
    print(count)
    if len(selmats) !=0:
        stepcount = 1/count
    
    s_step = 0
    
    if len(selmats) > 1:
        for ob in selmats:
            if ob != 'NoneType':
                
                bpd = bpy.data.materials[ob]
                #r = random.random()
                nhk = colorsys.rgb_to_hsv(1, 1, 1)


                nc = colorsys.hsv_to_rgb(s_step,1,1)
                for node in bpd.node_tree.nodes:
                    print(node.type)
                    if node.type == 'BSDF_PRINCIPLED':
                        node.inputs[0].default_value[0] = nc[0]
                        node.inputs[0].default_value[1] = nc[1]
                        node.inputs[0].default_value[2] = nc[2]
                    if node.type == 'BSDF_DIFFUSE':
                        node.inputs[0].default_value[0] = nc[0]
                        node.inputs[0].default_value[1] = nc[1]
                        node.inputs[0].default_value[2] = nc[2]                
  
                
                s_step += stepcount
    else:
        if len(selmats) !=0:
            for ob in selmats:
                if ob != 'NoneType':
                    
                    bpd = bpy.data.materials[ob]
                    r = random.random()
                    nhk = colorsys.rgb_to_hsv(1, 1, 1)


                    nc = colorsys.hsv_to_rgb( r,1,1)
                    
                    for node in bpd.node_tree.nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            node.inputs[0].default_value[0] = nc[0]
                            node.inputs[0].default_value[1] = nc[1]
                            node.inputs[0].default_value[2] = nc[2]
                        if node.type == 'BSDF_DIFFUSE':
                            node.inputs[0].default_value[0] = nc[0]
                            node.inputs[0].default_value[1] = nc[1]
                            node.inputs[0].default_value[2] = nc[2]
        else:
            self.report({'ERROR'}, "Select at least 1 object with material")              

 

class Random_Col(Operator):
    bl_idname = "ex.randomcol"
    bl_label = "Randomize"

    def execute(self, context):
            
        random_col(self,context)
        return {'FINISHED'}

#Select by material


def select_mat(context):
    selmat = 1
    for ob in bpy.context.active_object.material_slots:
        selmat = ob

    for ob in bpy.context.view_layer.objects:
        for nam in ob.material_slots:
            if nam.name == selmat.name:
                bpy.data.objects[ob.name].select_set(True) 



 

class Select_Mat(Operator):
    bl_idname = "ex.selmat"
    bl_label = "Material"

    def execute(self, context):
            
        select_mat(context)
        return {'FINISHED'}
    
#Select by index


def select_index(self, context):
    contob = context.object
    name = contob.name
    
    target = ""
    
    

    cur_col = contob.users_collection
    
    for col in cur_col:
        check = False
        if col.name[:8] == 'Low Poly':
            check = True
            coln = col.name
            inde = str(bpy.context.scene.mesh_l.my_lpstr)
            othercol = 'High Poly' + str(col.name[8:])
            print(othercol)
            
        if col.name[:9] == 'High Poly':
            check = True
            coln = col.name
            inde = str(bpy.context.scene.mesh_h.my_hpstr)
            othercol = 'Low Poly' + str(col.name[9:])
            
        if check == False:
            self.report({'ERROR'}, 'Object is not in LowPoly or HighPoly collection')
            return {'FINISHED'}
    
    ind = name.find(inde)
    
    target = name[:ind]
    print (target)
                        
   # coln = "Low Poly_" + str(bpy.context.scene.id_slider.col_id)
    for obj in bpy.data.collections[coln].objects:
        if obj.name[:ind] == target:
            bpy.data.objects[obj.name].select_set(True) 
    for obj in bpy.data.collections[othercol].objects:
        if obj.name[:ind] == target:
            bpy.data.objects[obj.name].select_set(True) 

class Select_By_index(Operator):
    bl_idname = "setid.selbyid"
    bl_label = "Name"

    def execute(self, context):
            
        select_index(self, context)
        return {'FINISHED'}
    
# Select n-gones
def sel_ngon(context):
    if bpy.context.object.mode == 'EDIT':
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')

        bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER', extend=False)
    else:
        for obj in bpy.data.collections["Low Poly_" + str(bpy.context.scene.id_slider.col_id)].objects:
            obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
        bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER', extend=False)
class Sel_ngones(Operator):
    bl_idname = "setid.selng"
    bl_label = "Select N-Gones"
    
    def execute(self, context):
            
        sel_ngon(context)
        return {'FINISHED'}    
#select collection
        
def sel_col(context):
    selob = bpy.context.active_object
    col = selob.users_collection
    colname = None
    for ob in col:
        colname = ob.name
        break
    accol = bpy.data.collections[colname].objects
    for objs in accol:
        objs.select_set(True)

class Sel_col(Operator):   
    bl_idname = "ex.selcol"
    bl_label = "SelCol"
    
    def execute(self, context):
        sel_col(context)
        return {'FINISHED'}



#Addon Updater

#Get Folder 
def get_addon_folder():
    addon_name = bl_info['name']
    s_path =''

    for mod in addon_utils.modules():
        #print(mod)
        #print(mod.bl_info['name'])
        
        if mod.bl_info['name'] == 'Set_ID':
            filepath = mod.__file__
            s_path = filepath[:-len(bpy.path.basename(filepath))]
        else:
            pass
            
    return s_path


def update_addon(self):
    #get raw from git
    url = 'https://raw.githubusercontent.com/Mandrew3d/Set_ID/main/__init__.py'
    
    response = requests.get(url, stream=True)

    addon_path = get_addon_folder()
    path = os.path.join(addon_path, '__init__.py')
    
    if response.status_code == 200:

        #read instaled addon init        
        f_path = path

        file = open(f_path, "r")
        
        inst_addon = file.read()
        file.close()   
        
        #read git addon init   
        git_addon = response.text

        
        t1 = inst_addon
        t2 = git_addon
        
        if t1 == t2:
            self.report({'INFO'}, 'Is the latest version')   
            #print('Git = Inst')
        else:
            
            
            filePath = addon_path

            
            newFile = open(os.path.join(filePath, "__init__UPD.py"), "w")
            newFile.write(git_addon)
            newFile.close()

 
            
            os.replace(os.path.join(filePath, "__init__UPD.py"), os.path.join(filePath, "__init__.py"))
            bpy.ops.script.reload()
            #sys.modules['Master_Instance-main'].update_addon() 
    else:
        print('Error downloading file')
         
class SETID_Addon_Updater(Operator):
    bl_idname = "setid.addon_upd"
    bl_label = "Update Addon"
    bl_description = "Update Addon from Github" 
    
        
    def execute(self, context):
        update_addon(self)
        return {'FINISHED'}   
 

#Menu Settings
class VIEW3D_MT_SETID_Settings(bpy.types.Menu):
    bl_label = "Set-ID Settings"
    
    def draw(self, context):
        
        layout = self.layout

        scene = context.scene

        layout.label(text="Settings:")
        
        
        layout.separator()
        col = layout.column()
         
        col.operator("setid.addon_upd", icon = "URL") 
         
        op = col.operator(
            'wm.url_open',
            text='Contact Me',
            icon='CURRENT_FILE'
            )
        op.url = 'https://t.me/Mandrew3d'

#Menu fbx export
class VIEW3D_MT_fbx_settings_menu(bpy.types.Menu):
    bl_label = "SetID FBX Settings"
    bl_idname = "VIEW3D_MT_fbx_settings_menu"

    def draw(self, context):
        layout = self.layout
        s = context.scene.fbx_settings

        # --- PATH ---
        layout.label(text="Filepath:")
        layout.prop(s, "filepath", text="")

        # --- SCALE ---
        col = layout.column(align=True)
        col.label(text="Scale:")
        col.prop(s, "global_scale")
        col.prop(s, "apply_unit_scale")
        col.prop(s, "apply_scale_options")

        # --- TRANSFORM ---
        col = layout.column(align=True)
        col.label(text="Transform:")
        col.prop(s, "use_space_transform")
        col.prop(s, "bake_space_transform")

        # --- OBJECTS ---
        col = layout.column(align=True)
        col.label(text="Objects:")
        col.prop(s, "object_types")

        # --- MESH OPTIONS ---
        col = layout.column(align=True)
        col.label(text="Mesh Options:")
        col.prop(s, "use_mesh_modifiers")
        col.prop(s, "use_mesh_modifiers_render")
        col.prop(s, "mesh_smooth_type")
        col.prop(s, "use_subsurf")
        col.prop(s, "use_mesh_edges")
        col.prop(s, "use_tspace")
        col.prop(s, "use_triangles")

        # --- COLORS ---
        col = layout.column(align=True)
        col.label(text="Colors:")
        col.prop(s, "colors_type")
        col.prop(s, "prioritize_active_color")

        # --- MISC ---
        col = layout.column(align=True)
        col.label(text="Other:")
        col.prop(s, "use_custom_props")
        col.prop(s, "use_metadata")

        # --- AXIS ---
        col = layout.column(align=True)
        col.label(text="Axis Conversion:")
        row = col.row(align=True)
        row.prop(s, "axis_forward")
        row.prop(s, "axis_up")

        layout.separator()
        layout.operator("export_scene.fbx_custom", text="Export FBX")

#Menu Settings
class VIEW3D_MT_SETID_Settings(bpy.types.Menu):
    bl_label = "Set-ID Settings"
    
    def draw(self, context):
        
        layout = self.layout

        scene = context.scene

        layout.label(text="Settings:")
        
        
        layout.separator()
        col = layout.column()
         
        col.operator("setid.addon_upd", icon = "URL") 
         
        op = col.operator(
            'wm.url_open',
            text='Contact Me',
            icon='CURRENT_FILE'
            )
        op.url = 'https://t.me/Mandrew3d'

#Menu Set Names
class VIEW3D_MT_SETID_SetName_Settings(bpy.types.Menu):
    bl_label = "Set Name Settings"
    
    def draw(self, context):
        
        layout = self.layout

        scene = context.scene

        layout.label(text="Settings:")
        
        
        layout.separator()
        col = layout.column()
         
                # Mesh suffix
        layout.label(text="Mesh suffix:")
        split = layout.split()
        col = split.column(align=True)
        col.label(text="Low poly")
        col.label(text="High poly")
        
        col = split.column(align=True)
        col.prop(scene.mesh_l, "my_lpstr")
        col.prop(scene.mesh_h, "my_hpstr")       
                
#Header 
def SELECT_HT_collection(self, context):
    selob = bpy.context.active_object
    if selob != None:
        col = selob.users_collection
        colname = None
        for ob in col:
            colname = ob.name
            break
        ic = 'RESTRICT_SELECT_OFF'
        slname = colname[:3]

        if slname == "Low":
    
            ic = 'MESH_CIRCLE'
        if slname == "Hig":
    
            ic = 'MESH_UVSPHERE'
        
        self.layout.operator(
            operator='ex.selcol',
            icon= ic,
            text=colname
        )

#Layouts
class SETIDC_PT_Operators(bpy.types.Panel):

    bl_label = "Set ID"
    bl_category = "Set-ID"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    #bl_context = 'objectmode'

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        
        
        
        
        
        mytool = scene.id_slider
       
        # New_Collection  
        
        collections = bpy.context.scene.setid_collections
        
        box = layout.box()
        box.label(text="Set collection:")
        
        #Cols Array
        act_col = bpy.context.scene.id_slider.active_col_id
        ind_col = 0
        
        #col = box.column(align = True)
#        row = layout.row(align = True) 
#        
#        row = col.row(align = True)
#        
        col = box.column(align = True)
        
        for colect in collections:
            row = layout.row(align = True) 
            row = col.row(align = True)
            
            is_active = False
            if ind_col == act_col:
                is_active = True
            arrow_down = row.operator("setid.move_id_collection", text = '', icon = 'TRIA_DOWN')
            arrow_down.col_id = ind_col
            arrow_down.up = False
            
            arrow_up = row.operator("setid.move_id_collection", text = '', icon = 'TRIA_UP')
            arrow_up.col_id = ind_col
            arrow_up.up = True
                        
            
            
            but = row.operator("setid.set_collection", text = colect.name,  depress = is_active)
            but.col_id = ind_col
            
            
            
            rename_b = row.operator("setid.rename_collection", text = '', icon = 'GREASEPENCIL')
            rename_b.col_id = ind_col
            
            delete_b = row.operator("setid.delete_collection", text = '', icon = 'TRASH')
            delete_b.col_id = ind_col
            
            ind_col += 1
        
        row = layout.row(align = True) 
        row = col.row(align = True)    
        row.operator("setid.new_collection", icon='PLUS', text = 'Add Object')
        
        
        col = box.column(align = True)
        row = layout.row(align = True) 
        
        row = col.row(align = True)
        #row_new = layout.row()
        
        row.operator("lp.poly", icon='MESH_CIRCLE')
        presslp = bpy.context.scene.lp_g.lp_gal_viz
        name = get_active_collection_name()
        colchek = "Low Poly_" + name
        if colchek in bpy.data.collections:
            dislp = True
        else:
            dislp = False
            
        row.operator("setid.lpviz", icon = 'HIDE_OFF', text = "",depress = presslp, emboss = dislp)
        
        
        row.operator("hp.poly", icon='MESH_UVSPHERE')
        
        presshp = bpy.context.scene.lp_g.hp_gal_viz
        #name = 
        colchek = "High Poly_" + name
        if colchek in bpy.data.collections:
            dishp = True
        else:
            dishp = False
             
        row.operator("setid.hpviz", icon = 'HIDE_OFF', text = "",depress = presshp, emboss = dishp)
        
        #col.prop(mytool,"col_id")
        
        # Set name
        box = layout.box()
        row = box.row(align = True)
        row.label(text="Set names:")
        row.menu("VIEW3D_MT_SETID_SetName_Settings", icon = "PREFERENCES", text = '' )
        
        
                
        scene = context.scene
        mystr = scene.st_name
        
        
        row = box.row(align = True)
        row.operator("set.name")
        row.prop(mystr,"my_str")       
        
        # Auto index
        #split = layout.split()
        #col = split.column()
        col = box.column(align = True)
        row = col.row(align = True)
        row.prop(scene.ai_b,"my_hide")
        #col.label(text="")
        #col = split.column()
        #row = col.row(align = True)
        row.prop(scene.ai_b,"my_autg")
            #Attach
        #row = layout.row(align = True)
        row = box.row(align = True)
        row.operator("set.copy_name") 
        #hide named
        row = box.row(align = True)
        row.operator("setid.hide_named", icon = 'HIDE_ON')
        
        
#        # Mesh suffix
#        layout.label(text="Mesh suffix:")
#        split = layout.split()
#        col = split.column(align=True)
#        col.label(text="Low poly")
#        col.label(text="High poly")
#        
#        col = split.column(align=True)
#        col.prop(scene.mesh_l, "my_lpstr")
#        col.prop(scene.mesh_h, "my_hpstr")
        
        # Export
        box = layout.box()
        row = box.row(align = True)
        row.label(text="Export collections:")
        
        row.prop(context.scene.show_fbx_settings_flag , "show_fbx_settings", text="", icon="PREFERENCES")
        
        s = context.scene
        if s.show_fbx_settings_flag.show_fbx_settings:
            layout = self.layout
            fbx = context.scene.fbx_settings


            # ----------------------------------------------------
            # TRANSFORM
            # ----------------------------------------------------
            box1 = box.box()
            box2= box1.box()
            box2.label(text="Transform", icon='OBJECT_DATA')

            # Scale
            col = box2.column(align=True)
            col.label(text="Scale:")
            col.prop(fbx, "global_scale", text="Scale")
            col.prop(fbx, "apply_unit_scale", text="Apply Unit")
            col.prop(fbx, "apply_scale_options", text="Apply Scalings")

            # Forward / Up
            row = box2.row(align=True)
            row.prop(fbx, "axis_forward", text="Forward")
            row.prop(fbx, "axis_up", text="Up")

            # Space / Apply transform
            box2.prop(fbx, "use_space_transform", text="Use Space Transform")
            box2.prop(fbx, "bake_space_transform", text="Apply Transform")


            # ----------------------------------------------------
            # GEOMETRY
            # ----------------------------------------------------
            #box = box.box()
            box2= box1.box()
            box2.label(text="Geometry", icon='MESH_DATA')

            # Smoothing
            col = box2.column(align=True)
            col.prop(fbx, "mesh_smooth_type", text="Smoothing")

            # Subdivision
            box2.prop(fbx, "use_subsurf", text="Export Subdivision Surface")

            # Modifiers
            box2.prop(fbx, "use_mesh_modifiers", text="Apply Modifiers")
         

            # Loose edges / triangulation / tangent space
            box2.prop(fbx, "use_mesh_edges", text="Loose Edges")
            #box2.prop(fbx, "use_triangles", text="Triangulate Faces")
            box2.prop(fbx, "use_tspace", text="Tangent Space")

            # Vertex colors
            box2.prop(fbx, "colors_type", text="Vertex Colors")
            box2.prop(fbx, "prioritize_active_color", text="Prioritize Active Color")
                                    
            
        #layout.label(text="Export path:")
        #box = layout.box()
        row = box.row(align = True)
        row.prop(scene.path_s, "exp_path") # EXPORT
        open_ep = row.operator("setid.open_folder", text = '', icon = 'WORKSPACE')
       
        open_ep.path = bpy.context.scene.path_s.exp_path
        
        row = box.row(align = True)
        row.operator("ex.fbx") # EXPORT
        
        row = box.row(align = True)
        #split = layout.split()
        #row = row.column()
        row.prop(scene.lp_g,"lp_gal")
        #col = split.column()
        row.prop(scene.lp_g,"hp_gal")
        
        #triangulate
        row = box.row(align = True)
        row.prop(scene.lp_g,"lp_tris")
        row.prop(scene.lp_g,"hp_tris")


        layout.label(text="Textures path:")
        row = layout.row(align = True)
        row.prop(scene.path_s, "exp_pathmat") # Materials attaching

        open_cp = row.operator("setid.open_folder", text = '', icon = 'WORKSPACE')
        open_cp.path = bpy.context.scene.path_s.exp_pathmat
                
        # Connect
        row = layout.row(align = True)
        row.operator("ex.mapscon")           
        row.operator("ex.mapsexp")
        
        # Random colors
        layout.label(text="Randomize colors:")
        row = layout.row(align = True)
        row.operator("ex.randomcol")        
        
        # Select by
        layout.label(text="Select by:")
        col = layout.column(align = True)
        col.operator("ex.selmat") 
        #row = layout.row(align = True) 
        col.operator("setid.selbyid")          
        # Triangulate 
        layout.label(text="Triangulate:")
        #row = layout.row(align = True)
        #row.operator("ex.triang", depress = True) 
        
        selob = bpy.context.selected_objects
        lensel = len(selob)

        chek = False
        ismod = 0
        selcount = 0
        if lensel != 0:
            for ob in bpy.context.selected_objects:
                selcount +=1
                if len(bpy.data.objects[ob.name].modifiers) !=0:
                    for mod in bpy.data.objects[ob.name].modifiers:
                        
                        if mod.type == 'TRIANGULATE':
                            
                            ismod += 1
                           
                else:
                    
                    ismod += 0
        if ismod != selcount:
            row = layout.row(align = True)
            row.operator("ex.triang", depress = False)
            
        else:
            row = layout.row(align = True)
            row.operator("ex.triang", depress = True, text = "Untriangulate")                                 
        
        ismod = ismod
        layout.label(text="Triangulated: "+ str(ismod) + "/"+ str(selcount))
        
        #Poly count
        colname = "Low Poly_" + str(bpy.context.scene.id_slider.col_id)
        layout.label(text="Polycount of "+ str(colname) + ":" )
        tris, polys, ngones = 0,0,0
        
        #colname = "Low Poly_" + str(bpy.context.scene.id_slider.col_id)
        if colname in bpy.data.collections:
            dg = bpy.context.evaluated_depsgraph_get()
            #objects = 
            for obj in bpy.data.collections[colname].objects:
                obj = obj.evaluated_get(dg)
                mesh = obj.to_mesh()
                polys += len(mesh.polygons)
                for poly in mesh.polygons:
                    if len(poly.vertices) > 4:
                        ngones += 1
                tris += sum([(len(p.vertices) - 2) for p in obj.data.polygons])
                
        layout.label(text ="Poly: " + str(polys) +"  Tris: "+ str(tris) + "  N-gones: "+ str(ngones))
        if ngones > 0:
            row = layout.row(align = True)
            row.operator("setid.selng")
        
        #settings
        row = layout.row()
        row.menu("VIEW3D_MT_SETID_Settings", icon = "PREFERENCES", text = '' )
        
        ver = bl_info.get('version')
        ver = str(ver[0])+('.')+str(ver[1])
        row.label(text = 'Version: ' + ver)    
        
class SETID_Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

 
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("setid.addon_upd", icon = "URL")
                
classes = [
    VIEW3D_MT_SETID_SetName_Settings,
    VIEW3D_MT_fbx_settings_menu,
    Collections_Props,
    Create_New_Collection,
    Move_Id_Collection,
    Delete_Collection,
    Set_Active_Collection,
    Rename_Collection,
    Open_Folder,
    Low_poly,
    High_poly,
    LPCol_viz,
    HPCol_viz,
    SETIDC_PT_Operators,
    Slider,
    Set_name,
    Set_name_str,
    Set_name_aib,
    SetID_Show_Settings,
    FbxExportSettings,
    Copy_name,
    Hide_named,
    Low_polystr,
    Export_fbx,
    High_polystr,
    HpLP_gal,
    Path_m,
    Triang_obj,
    Maps_Con,
    Maps_Exp,
    Random_Col,
    Select_Mat,
    Select_By_index,
    Sel_ngones,
    Sel_col,
    #SELECT_OT_collection
    SETID_Addon_Updater,
    VIEW3D_MT_SETID_Settings,
    SETID_Preferences,
]

def register():
    for cl in classes:
        register_class(cl)
    
        
    
    
    bpy.types.Scene.id_slider = bpy.props.PointerProperty(type = Slider)
    
    #fbx settings
    bpy.types.Scene.show_fbx_settings_flag = bpy.props.PointerProperty(type=SetID_Show_Settings)
    bpy.types.Scene.fbx_settings = bpy.props.PointerProperty(type=FbxExportSettings)
    
    bpy.types.Scene.st_name = bpy.props.PointerProperty(type = Set_name_str)
    bpy.types.Scene.ai_b = bpy.props.PointerProperty(type = Set_name_aib)
    bpy.types.Scene.mesh_l = bpy.props.PointerProperty(type = Low_polystr)
    bpy.types.Scene.mesh_h = bpy.props.PointerProperty(type = High_polystr)
    bpy.types.Scene.lp_g = bpy.props.PointerProperty(type = HpLP_gal)
    bpy.types.Scene.path_s = bpy.props.PointerProperty(type = Path_m)
    bpy.types.Scene.path_mat = bpy.props.PointerProperty(type = Path_m)
    #bpy.types.Scene.hp_g = bpy.props.PointerProperty(type = High_polystr)
    bpy.types.Scene.setid_collections = bpy.props.CollectionProperty(type = Collections_Props)
    bpy.types.VIEW3D_HT_header.prepend(SELECT_HT_collection)
    
    
def unregister():
    bpy.types.VIEW3D_HT_header.remove(SELECT_HT_collection)

    for cl in reversed(classes):
        unregister_class(cl)


if __name__ == "__main__":
    register()

#object.simple_operator
