bl_info = {
    "name": "Set_ID",
    "author": "Mandrew3D",
    "version": (1, 3),
    "blender": (4, 0, 0),
    "location": "View3D > UI > Set-ID",
    "description": "Addon for setting ID names",
    "warning": "",
    "doc_url": "https://github.com/Mandrew3d/Set_ID",
    "category": "Mods",
}

import bpy, math, random, colorsys, os
import addon_utils
import requests

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
    

#Set name index str
class Set_name_str(bpy.types.PropertyGroup):
    my_str : bpy.props.StringProperty(name = "", default="A")
    
    
#Set name index auto gal
class Set_name_aib(bpy.types.PropertyGroup):
    my_autg : bpy.props.BoolProperty(name = " Auto index", default=True )
    my_hide : bpy.props.BoolProperty(name = " Auto hide", default=True )
    
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

# low poly collection
def low_poly(self, context):


#Collection creation
    indexcol=bpy.context.scene.id_slider.col_id
    namecollp="Low Poly_" + str(indexcol)
    if not bpy.data.collections.get(namecollp):
        bpy.data.scenes["Scene"].collection.children.link(bpy.data.collections.new(namecollp))
    else:
        bpy.data.collections.get(namecollp)
        

#Add in collection            
    bpy.ops.object.move_to_collection(collection_index=0, is_new=True, new_collection_name="VremCollection")
    coll_from = bpy.data.collections['VremCollection']
    coll_to = bpy.data.collections[namecollp]
    to_unlink = []
    
    
    for ob in bpy.context.selected_objects:
        try:
            coll_to.objects.link(ob)
        except RuntimeError:
            pass
        to_unlink.append(ob)
    
    for ob in bpy.context.selected_objects:
        coll_from.objects.unlink(ob)
   
    Vrem = bpy.data.collections['VremCollection']    
    bpy.data.collections.remove(Vrem)

    
class Low_poly(Operator):
    bl_idname = "lp.poly"
    bl_label = "Low Poly"

    def execute(self, context):
            
        low_poly(self, context)
        return {'FINISHED'}

# High poly collection
def high_poly(self, context):


#Collection creation
    indexcol=bpy.context.scene.id_slider.col_id
    namecolhp="High Poly_" + str(indexcol)
    if not bpy.data.collections.get(namecolhp):
        bpy.data.scenes["Scene"].collection.children.link(bpy.data.collections.new(namecolhp))
    else:
        bpy.data.collections.get(namecolhp)
        

#Add in collection            
    bpy.ops.object.move_to_collection(collection_index=0, is_new=True, new_collection_name="VremCollection")
    coll_from = bpy.data.collections['VremCollection']
    coll_to = bpy.data.collections[namecolhp]
    to_unlink = []
    
    
    for ob in bpy.context.selected_objects:
        try:
            coll_to.objects.link(ob)
        except RuntimeError:
            pass
        to_unlink.append(ob)
    
    for ob in bpy.context.selected_objects:
        coll_from.objects.unlink(ob)
   
    Vrem = bpy.data.collections['VremCollection']    
    bpy.data.collections.remove(Vrem)

    
class High_poly(Operator):
    bl_idname = "hp.poly"
    bl_label = "High Poly"

    def execute(self, context):
            
        high_poly(self, context)
        return {'FINISHED'}    
#LP Viz
def lpviz(self, context):
    indexcol=bpy.context.scene.id_slider.col_id
    colname = "Low Poly_" + str(indexcol)

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
    indexcol=bpy.context.scene.id_slider.col_id
    colname = "High Poly_" + str(indexcol)

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
    namecollp='Low Poly_' + str(indexcol)
    
    indexcol=bpy.context.scene.id_slider.col_id
    namecolhp='High Poly_' + str(indexcol)

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
    col_id = bpy.context.scene.id_slider.col_id
    
    hp_col_name = 'High Poly_' + str(col_id)
    lp_col_name = 'Low Poly_' + str(col_id)
    
    hp_col = bpy.data.collections[hp_col_name]
    lp_col = bpy.data.collections[lp_col_name]
    
    for ob in hp_col.objects:
        if '_high_' in ob.name:
            ob.hide_set(True)
            #print(ob.name)
    for ob in lp_col.objects:
        if '_low_' in ob.name:
            ob.hide_set(True)
    
    
class Hide_named(Operator):
    bl_idname = "setid.hide_named"
    bl_label = "Hide Named"

    def execute(self, context):
        hide_named(self, context)
        return {'FINISHED'}
    
        
def exp_fbx(context):
#export Lowpoly

    tris = bpy.context.scene.lp_g.lp_tris
    trishp = bpy.context.scene.lp_g.hp_tris
    
    if bpy.context.scene.lp_g.lp_gal == True:
        indexcol = bpy.context.scene.id_slider.col_id 
        namecollp = str("Low Poly_" + str(indexcol))


        path =  bpy.path.abspath(bpy.context.scene.path_s.exp_path)
        collection = bpy.data.collections[namecollp]
        

        layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
        bpy.context.view_layer.active_layer_collection = layer_collection
        bpy.ops.export_scene.fbx(check_existing=False,
            filepath= path + "Lowpoly_" + str(indexcol) + ".fbx",
            filter_glob="*.fbx",
            use_selection= False,
            use_triangles= tris,
            use_armature_deform_only=True,
            use_active_collection= True,
            add_leaf_bones=False,
            path_mode='AUTO')

    if bpy.context.scene.lp_g.hp_gal == True: 
        indexcol=bpy.context.scene.id_slider.col_id
        namecolhp="High Poly_" + str(indexcol)
        path =  bpy.path.abspath(bpy.context.scene.path_s.exp_path)
        collection = bpy.data.collections[namecolhp]
        

        layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
        bpy.context.view_layer.active_layer_collection = layer_collection
        bpy.ops.export_scene.fbx(check_existing=False,
            filepath= path + "Highpoly_" + str(indexcol) + ".fbx",
            #filepath= path,
            filter_glob="*.fbx",
            use_selection= False,
            use_triangles= trishp,
            use_armature_deform_only=True,
            use_active_collection= True,
            add_leaf_bones=False,
            path_mode='AUTO')

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
        box = layout.box()
        box.label(text="Set collection:")
        
        col = box.column(align = True)
        row = layout.row(align = True) 
        
        row = col.row(align = True)
        #row_new = layout.row()
        
        row.operator("lp.poly", icon='MESH_CIRCLE')
        presslp = bpy.context.scene.lp_g.lp_gal_viz
        colchek = "Low Poly_" + str(bpy.context.scene.id_slider.col_id)
        if colchek in bpy.data.collections:
            dislp = True
        else:
            dislp = False
            
        row.operator("setid.lpviz", icon = 'HIDE_OFF', text = "",depress = presslp, emboss = dislp)
        row.operator("hp.poly", icon='MESH_UVSPHERE')
        
        presshp = bpy.context.scene.lp_g.hp_gal_viz
        colchek = "High Poly_" + str(bpy.context.scene.id_slider.col_id)
        if colchek in bpy.data.collections:
            dishp = True
        else:
            dishp = False
             
        row.operator("setid.hpviz", icon = 'HIDE_OFF', text = "",depress = presshp, emboss = dishp)
        
        col.prop(mytool,"col_id")
        
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
        box.label(text="Export collections:")
        #layout.label(text="Export path:")
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
    bpy.types.Scene.st_name = bpy.props.PointerProperty(type = Set_name_str)
    bpy.types.Scene.ai_b = bpy.props.PointerProperty(type = Set_name_aib)
    bpy.types.Scene.mesh_l = bpy.props.PointerProperty(type = Low_polystr)
    bpy.types.Scene.mesh_h = bpy.props.PointerProperty(type = High_polystr)
    bpy.types.Scene.lp_g = bpy.props.PointerProperty(type = HpLP_gal)
    bpy.types.Scene.path_s = bpy.props.PointerProperty(type = Path_m)
    bpy.types.Scene.path_mat = bpy.props.PointerProperty(type = Path_m)
    #bpy.types.Scene.hp_g = bpy.props.PointerProperty(type = High_polystr)
    
    bpy.types.VIEW3D_HT_header.prepend(SELECT_HT_collection)

    
def unregister():
    bpy.types.VIEW3D_HT_header.remove(SELECT_HT_collection)

    for cl in reversed(classes):
        unregister_class(cl)


if __name__ == "__main__":
    register()

#object.simple_operator
