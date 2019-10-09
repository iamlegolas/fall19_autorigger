"""
sirena rig setup
main setup
"""

#from rigLib.base import control
from rigLib.base import module
from rigLib.rig import spine
from rigLib.rig import leg

from . import project
from . import character_deform

import maya.cmds as cmds

scene_scale = project.scene_scale
main_project_path = project.main_project_path
model_file_path = '%s/%s/model/geo.mb'
builder_file_path = '%s/%s/builder/skel.mb' 

root_bnd_jnt = 'root'
head_bnd_jnt = 'head_bnd'

pelvis_jnt = 'pelvis'
spine_jnts = ['spine_01', 'spine_02', 'spine_03', 'spine_04']
l_leg_jnts = ['thigh_l', 'calf_l', 'ankle_l', 'ball_l', 'toe_l']
r_leg_jnts = ['thigh_r', 'calf_r', 'ankle_r', 'ball_r', 'toe_r']

def build(character_name):
    """
    main function to build character rig
    """
    
    #new scene
    cmds.file(new=True, force=True)
    
    #import builder scene
    builder_file = builder_file_path % (main_project_path, character_name)
    cmds.file(builder_file, i=True) #i=import
    
    #create base
    base_rig = module.Base(character_name=character_name, scale=scene_scale)
    ikfk_shapes = cmds.listRelatives(base_rig.ikfk_ctrl.ctrl, shapes=True)
    for shape in ikfk_shapes:
        cmds.setAttr(shape + '.ove', True) #enable overrides
        cmds.setAttr(shape + '.ovc', 18)
    
    #import model
    model_file = model_file_path % (main_project_path, character_name)
    cmds.file(model_file, i=True) #i=import
    
    #parent model
    model_grp = '%s_geo' % character_name
    cmds.parent(model_grp, base_rig.geo_grp)
    
    #parent skeleton
    cmds.parent(root_bnd_jnt, base_rig.top_grp)
    
    #deform setup
    character_deform.build(base_rig, character_name)
    
    #control setup
    spine.build(pelvis_jnt=pelvis_jnt, spine_jnts=spine_jnts, base_rig=base_rig)
    leg.build(leg_jnts=l_leg_jnts, side='l', prefix='leg', rig_scale=1.0, base_rig=base_rig)
#    leg.build(leg_jnts=r_leg_jnts, side= 'r', prefix='leg', rig_scale=1.0, base_rig=base_rig)
    
    
def make_control_setup(base_rig):
    """
    make control setup
    """
    pass
    '''
    #spine_jnts = ['root_bnd', 'spine_01_bnd', 'spine_02_bnd', 'spine_03_bnd', 'spine_04_bnd']
    spine_jnts = ['spine_01_bnd', 'spine_02_bnd', 'spine_03_bnd', 'spine_04_bnd']
    
    #spine
    spine_rig = spine.build(
                            spine_jnts,
                            root_bnd_jnt,
                            #spine_crv,
                            body_loc='body_lctr',
                            chest_loc='chest_lctr',
                            pelvis_loc='pelvis_lctr',
                            prefix='spine',
                            rig_scale=scene_scale,
                            base_rig=base_rig
                            )
    '''
    
    
    
    
    
    
    
    
    
    