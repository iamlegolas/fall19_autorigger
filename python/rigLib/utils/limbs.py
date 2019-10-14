"""
limb utils @utils
has different service functions required while working with limbs
"""

import maya.cmds as cmds
from rigLib.utils import transform

def create_pole_vector_locator(prefix, mid_jnt, t_vec):
    """
    create locator where control for IK pole vector needs to be
    
    @param prefix: str, name of the limb
    @param mid_jnt: str, the limb's mid joint i.e. the elbow or knee
    @param t_vec: vector with local translate values for the locator
    @return str: name of the locator
    """
    
    loc = prefix+'_temp_loc'
    cmds.spaceLocator(n=loc)
    cmds.delete(cmds.parentConstraint(mid_jnt, loc, mo=False))
    cmds.parent(loc, mid_jnt)

    cmds.xform(loc, os=True, t=t_vec)

    cmds.parent(loc, w=True)
    cmds.makeIdentity(loc, t=1, r=1, s=1, apply=True)

    return loc

def setup_ikfk_switch(ikfk_switch_ctrl, side, prefix, 
                      ik_jnts, fk_jnts, bnd_jnts, ik_anim_grp, fk_anim_grp):
    """
    set up ikfk switching feature
    
    @param ikfk_switch_ctrl: ctrl obj, the ikfk_switch_ctrl on the baserig
    @param side: str, side of the body this limb is attached to (l or r)
    @param prefix: str, name of the limb
    @param ik_jnts: list(str), list of ik_drv jnts for the limb
    @param fk_jnts: list(str), list of fk_drv jnts for the limb
    @param bnd_jnts: list(str), list of bnd jnts for the limb
    @param ik_anim_grp: obj, maya group containing all ik ctrls (parented under baseRig.ctrl_grp)
    @param fk_anim_grp: obj, maya group containing all fk ctrls (parented under baseRig.ctrl_grp)
    @return None
    """

    blend_attr_name = side+'_'+prefix
    cmds.addAttr(ikfk_switch_ctrl.ctrl, k=True , ln=blend_attr_name,
                 defaultValue=0.0, minValue=0.0, maxValue=1.0)
    
    for i in range(len(bnd_jnts)):
        rotate_blend_node_name = side+'_'+prefix+'_ikfk_rotate_blend_node_'+str(i)
        cmds.shadingNode('blendColors', asUtility=True, name=rotate_blend_node_name)
        
        cmds.connectAttr(ikfk_switch_ctrl.ctrl+'.'+blend_attr_name, 
                         rotate_blend_node_name+'.blender')
        cmds.connectAttr(fk_jnts[i]+'.rotate', rotate_blend_node_name+'.color2')
        cmds.connectAttr(ik_jnts[i]+'.rotate', rotate_blend_node_name+'.color1')
        cmds.connectAttr(rotate_blend_node_name+'.output', bnd_jnts[i]+'.rotate')
        
        cmds.setDrivenKeyframe(fk_anim_grp, at='visibility', 
                               currentDriver=ikfk_switch_ctrl.ctrl+'.'+blend_attr_name, 
                               driverValue=0, value=1)
        cmds.setDrivenKeyframe(fk_anim_grp, at='visibility', 
                               cd=ikfk_switch_ctrl.ctrl+'.'+blend_attr_name, 
                               dv=1, v=0)
        cmds.setDrivenKeyframe(ik_anim_grp, at='visibility', 
                               cd=ikfk_switch_ctrl.ctrl+'.'+blend_attr_name, 
                               dv=1, v=1)
        cmds.setDrivenKeyframe(ik_anim_grp, at='visibility', 
                               cd=ikfk_switch_ctrl.ctrl+'.'+blend_attr_name, 
                               dv=0, v=0)
        
        '''
        translate_blend_node_name = side+'_'+prefix+'_ikfk_translate_blend_node_'+str(i)
        cmds.shadingNode('blendColors', asUtility=True, name=translate_blend_node_name)
        
        cmds.connectAttr(base_rig.ikfk_ctrl.ctrl+'.'+blend_attr_name, 
                         translate_blend_node_name+'.blender')
        cmds.connectAttr(fk_jnts[i]+'.translate', translate_blend_node_name+'.color2')
        cmds.connectAttr(ik_jnts[i]+'.translate', translate_blend_node_name+'.color1')
        cmds.connectAttr(translate_blend_node_name+'.output', bnd_jnts[i]+'.translate')
        '''

def create_twist_jnts(prefix, bnd_jnts):
    upper_twist_jnt = prefix+'_upper_twist'
    cmds.duplicate(bnd_jnts[0], n=upper_twist_jnt, parentOnly=True)
    cmds.parent(upper_twist_jnt, bnd_jnts[0])
    cmds.xform(upper_twist_jnt, r=True, t=[1, 0, 0])
    
    lower_twist_jnt = prefix+'_lower_twist'
    cmds.duplicate(bnd_jnts[1], n=lower_twist_jnt, parentOnly=True)
    cmds.parent(lower_twist_jnt, bnd_jnts[1])
    temp_dst = cmds.getAttr(bnd_jnts[2]+'.translateX')/2.0
    cmds.xform(lower_twist_jnt, r=True, t=[temp_dst, 0, 0])

def connect_twist_jnts(prefix, bnd_jnts, twist_jnts):
    upper_twist_mult = prefix+'_upper_mult'
    cmds.shadingNode('multiplyDivide', asUtility=True, n=upper_twist_mult)
    cmds.setAttr(upper_twist_mult+'.input2X', -1)
    cmds.connectAttr(bnd_jnts[0]+'.rotateX', upper_twist_mult+'.input1X')
    cmds.connectAttr(upper_twist_mult+'.outputX', twist_jnts[0]+'.rotateX')
    
    lower_twist_mult = prefix+'_lower_mult'
    cmds.shadingNode('multiplyDivide', asUtility=True, n=lower_twist_mult)
    cmds.setAttr(lower_twist_mult+'.input2X', 0.5)
    cmds.connectAttr(bnd_jnts[2]+'.rotateX', lower_twist_mult+'.input1X')
    cmds.connectAttr(lower_twist_mult+'.outputX', twist_jnts[1]+'.rotateX')
    
def setup_fk_space_switching(prefix, fk_anim_grp, fk_jnts, master_ctrl, fk_ctrl_01):
    #create orient group
    orient_grp = prefix+'_fk_orient_grp'
    orient_body_grp = prefix+'_fk_orient_body_grp'
    orient_world_grp = prefix+'_fk_orient_world_grp'
    
    cmds.group(name=orient_grp, em=True, p=fk_anim_grp)
    transform.snap(fk_jnts[0], orient_grp)

    cmds.duplicate(orient_grp, name=orient_body_grp)
    cmds.duplicate(orient_grp, name=orient_world_grp)
    cmds.parent(orient_world_grp, master_ctrl)
    
    cmds.parent(fk_ctrl_01, orient_grp)
    cmds.orientConstraint([orient_body_grp, orient_world_grp], orient_grp, mo=True)

    #set driven keys
    
def setup_limb_stretch(prefix, rig_module, ik_jnts, ik_ctrl_list):
    dis_dim_node = transform.setup_distance_dimension_node(prefix, ik_jnts[0], ik_ctrl_list[0].ctrl)
    cmds.parent(dis_dim_node[0], rig_module.dnt_grp)
    
def add_ikpop_counter(prefix, drv_jnts, bnd_jnts, ctrl):
    attr_name = 'limbStretch'
    cmds.addAttr(ctrl, shortName=attr_name, keyable=True, 
                 defaultValue=1.0, minValue=1.0, maxValue=1.4)
    
    multdiv_node_01 = prefix+'_stretch_multDiv_node_01'
    cmds.createNode('multiplyDivide', n=multdiv_node_01)
    multdiv_node_02 = prefix+'_stretch_multDiv_node_02'
    cmds.createNode('multiplyDivide', n=multdiv_node_02)

    cmds.connectAttr(ctrl+'.'+attr_name, drv_jnts[0]+'.scaleX')
    cmds.connectAttr(drv_jnts[0]+'.scaleX', multdiv_node_01+'.input1X')
    cmds.connectAttr(drv_jnts[1]+'.translateX', multdiv_node_01+'.input2X')
    cmds.connectAttr(multdiv_node_01+'.outputX', bnd_jnts[1]+'.translateX')
    
    cmds.connectAttr(ctrl+'.'+attr_name, drv_jnts[1]+'.scaleX')
    cmds.connectAttr(drv_jnts[1]+'.scaleX', multdiv_node_02+'.input1X')
    cmds.connectAttr(drv_jnts[2]+'.translateX', multdiv_node_02+'.input2X')
    cmds.connectAttr(multdiv_node_02+'.outputX', bnd_jnts[2]+'.translateX')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

        