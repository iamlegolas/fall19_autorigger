"""
sirena rig setup
deformation setup
"""

import os
import maya.cmds as cmds

from . import project
from rigTools import bSkinSaver
from rigLib.utils import name

skin_weights_dir = 'weights/skinCluster'
skin_weights_ext = '.swt'

def build(base_rig, character_name):
    
    model_grp = '%s_geo' % character_name
    
    #make twist joints
    ref_twist_jnts=['calf_l_bnd', 'calf_r_bnd']
    make_twist_jnts(base_rig, ref_twist_jnts)
    
    #load skin weights
    geo_list = get_model_geo_objs(model_grp)
    load_skin_weights(character_name, geo_list)
    
    #apply mush deformer
    
    #wrap hires body mesh
    
    
def get_model_geo_objs(model_grp):
    #get all geometry transforms
    geoList = [cmds.listRelatives(o, p=True)[0] for o in cmds.listRelatives(model_grp, ad=True, type='mesh')]
    return geoList
    
def make_twist_jnts(base_rig, parent_jnts):
    twist_jnts_main_grp = cmds.group(n='twist_joints_bnd_grp', p=base_rig.jnt_grp, em=True)
    for parent_jnt in parent_jnts:
        prefix = name.remove_suffix(parent_jnt)
        parent_jnt_child = cmds.listRelatives(parent_jnt, c=True, type='joint')[0]
        
        #make twist joints
        twist_jnt_grp = cmds.group(n=prefix+'_twist_jnt', p=twist_jnts_main_grp, em=1)
        
        twist_parent_jnt = cmds.duplicate(parent_jnt, n=prefix+'twistjnt_01', parentOnly=True)[0]
        twist_child_jnt = cmds.duplicate(parent_jnt_child, n=prefix+'twistjnt_02', parentOnly=True)[0]
        
        #adjust twist joints
        orig_jnt_radius = cmds.getAttr(parent_jnt+'.radius')
        for j in [twist_parent_jnt, twist_child_jnt]:
            cmds.setAttr(j+'.radius', orig_jnt_radius*2)
            cmds.color(j, ud=1)
            
        cmds.parent(twist_child_jnt, twist_parent_jnt)
        cmds.parent(twist_parent_jnt, twist_jnt_grp)
        
        #attach twist joints
        cmds.pointConstraint(parent_jnt, twist_parent_jnt)
        
        #make IK handle
        twist_ik = cmds.ikHandle(n=prefix+'twist_jnt_ikhandle', sol='ikSCsolver', sj=twist_parent_jnt, ee=twist_child_jnt)[0]
        cmds.hide(twist_ik)
        cmds.parent(twist_ik, twist_jnt_grp)
        cmds.parentConstraint(parent_jnt_child, twist_ik)

def save_skin_weights(character_name, geo_list=[]):
    """
    save weights for character geometry objects
    """
    
    for obj in geo_list:
        #get the weights file
        wt_file = os.path.join(project.main_project_path, character_name, skin_weights_dir, obj+skin_weights_ext)
        
        #save the weights file
        cmds.select(obj)
        bSkinSaver.bSaveSkinValues(wt_file)
        
def load_skin_weights(character_name, geo_list=[]):
    """
    load weights for character geometry objects
    """
    
    wt_dir = os.path.join(project.main_project_path, character_name, skin_weights_dir)
    wt_files = os.listdir(wt_dir)
    
    #load skin weights
    for wt_file in wt_files:
        ext_res = os.path.splitext(wt_file) #splits file name and its extension
        
        #check extension format
        if not ext_res>1:
            continue
        
        #check skin weight file
        if not ext_res[1] == skin_weights_ext:
            continue
        
        #check geometry list
        if geo_list and not ext_res[0] in geo_list:
            continue
        
        #check if object exists
        if not cmds.objExists(ext_res[0]):
            continue 
        
        #if all checks passed
        full_path_wt_file = os.path.join(wt_dir, wt_file)
        bSkinSaver.bLoadSkinValues(False, full_path_wt_file)








