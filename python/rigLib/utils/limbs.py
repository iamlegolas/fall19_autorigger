"""
limb utils @utils
has different service functions required while working with limbs
"""

import maya.cmds as cmds
from rigLib.utils import transform
from imathmodule import ceil
from rigLib.base import control

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
                 defaultValue=1.0, minValue=0.0, maxValue=1.0)
    
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


def create_deformer_blend(prefix, limb_ribbon_sfc, geo_skin_cluster, 
                          ctrl=None, foll_jnts_list=None, num_jnts=0):
    sine_bs_sfc = cmds.duplicate(limb_ribbon_sfc, name=prefix+'_ribbon_sfc_sine_bs')[0]
    twist_bs_sfc = cmds.duplicate(limb_ribbon_sfc, name=prefix+'_ribbon_sfc_twist_bs')[0]
    jnt_bs_sfc = cmds.duplicate(limb_ribbon_sfc, name=prefix+'_ribbon_sfc_joint_bs')[0]
    
    limb_bs = cmds.blendShape(sine_bs_sfc, twist_bs_sfc, jnt_bs_sfc, limb_ribbon_sfc, n=prefix+'_ribbon_blendShape')[0]
    cmds.setAttr(limb_bs+'.'+sine_bs_sfc, 1)
    cmds.setAttr(limb_bs+'.'+twist_bs_sfc, 1)
    cmds.setAttr(limb_bs+'.'+jnt_bs_sfc, 1)
    
    cmds.select(limb_ribbon_sfc)
    cmds.reorderDeformers(geo_skin_cluster, limb_bs)
    
    #setup sine
    sine_deformer = cmds.nonLinear(sine_bs_sfc, type='sine')
    cmds.setAttr(sine_deformer[0]+'.dropoff', 1)
    
    cmds.addAttr(ctrl, shortName='amplitude', keyable=True, 
                 defaultValue=0.0, minValue=-5.0, maxValue=5.0)
    cmds.addAttr(ctrl, shortName='wavelength', keyable=True, 
                 defaultValue=2.0, minValue=0.5, maxValue=10)
    cmds.addAttr(ctrl, shortName='offset', keyable=True, 
                 defaultValue=0.0, minValue=-10.0, maxValue=10.0)
    
    cmds.connectAttr(ctrl+'.amplitude', sine_deformer[0]+'.amplitude')
    cmds.connectAttr(ctrl+'.wavelength', sine_deformer[0]+'.wavelength')
    cmds.connectAttr(ctrl+'.offset', sine_deformer[0]+'.offset')
    
    #setup twist
    twist_deformer = cmds.nonLinear(twist_bs_sfc, type='twist')
    
    cmds.addAttr(ctrl, shortName='twist', keyable=True, 
                 defaultValue=0.0, minValue=-800.0, maxValue=800.0)
    cmds.connectAttr(ctrl+'.twist', twist_deformer[0]+'.startAngle')
    
    #setup joint-based blendshape
    num_jnts += 2
    joint_bs_jnt_list = []
    joint_bs_jnt_ofst_list = []
    joint_bs_ctrl_list = []
    foll_jnts_index_list = []
    for i in range(num_jnts):
#        index_list.append(i/(num_jnts-1.00))
        index = ceil((i/(num_jnts-1.00))*len(foll_jnts_list))
        if index-1 >= 0:
            index -= 1
        joint_bs_jnt_list.append(
            cmds.duplicate(foll_jnts_list[index],
                           name=prefix+'_ribbon_bs_jnt_'+str(i).zfill(2))[0])
        foll_jnts_index_list.append(index)
        
        if index != 0 and index != len(foll_jnts_list)-1:
            joint_bs_ctrl_list.append(
                 control.Control(shape='spine_ctrl_template', prefix=prefix+'_joint_bs_'+str(i).zfill(2), 
                                 translate_to=foll_jnts_list[index], scale=0.5, lock_channels=['s']))

    for jnt in joint_bs_jnt_list:
        cur_grp = cmds.group(em=True, n=jnt+'_ofst_grp', w=True)
        transform.snap_pivot(jnt, cur_grp)
        cmds.parent(jnt, cur_grp)

        joint_bs_jnt_ofst_list.append(cur_grp)

    cmds.group(joint_bs_jnt_ofst_list, n=prefix+'_ribbon_bs_jnts_grp', w=True)
    cmds.select(joint_bs_jnt_list, jnt_bs_sfc)
    jnt_bs_clstr = cmds.skinCluster(tsb=True, dr=4.5)

    for i in range(len(joint_bs_ctrl_list)):
        cmds.parentConstraint(foll_jnts_list[foll_jnts_index_list[i+1]], 
                              joint_bs_ctrl_list[i].ofst, mo=True)
        #cmds.parentConstraint(joint_bs_ctrl_list[i].ctrl, joint_bs_jnt_ofst_list[i+1])
        cmds.connectAttr(joint_bs_ctrl_list[i].ctrl+'.translate', joint_bs_jnt_ofst_list[i+1]+'.translate')
        cmds.connectAttr(joint_bs_ctrl_list[i].ctrl+'.rotate', joint_bs_jnt_ofst_list[i+1]+'.rotate')

    
    
    
    
    
    
    
    
    

        