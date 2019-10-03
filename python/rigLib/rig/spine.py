"""
spine @ rig
"""

import maya.cmds as cmds

from ..base import module
from ..base import control
from rigLib.utils import joint, ribbon
from rigLib.utils.ribbon import create_ep_curve

def build(
        pelvis_jnt,
        spine_jnts,
        prefix='spine',
        rig_scale=1.0,
        base_rig=None
        ):
    
    """
    @param spine_jnts: list(str), list of 6 spine jnts
    @param root_jnt: str, root_jnt
    @param prefix: str, prefix to name new object
    @param rig_scale: float, scale factor for size of controls
    @param base_rig: instance of base.module.Base class
    @return: dictionary with rig module objects 
    """
    
    #make rig module
    rig_module = module.Module(prefix=prefix, base_obj=base_rig, create_dnt_grp=True)
    
    
    #make spine controls
    body_ctrl = control.Control(shape='body_ctrl_template', prefix='body',
                                translate_to=pelvis_jnt, scale=rig_scale,
                                parent=rig_module.ctrl_grp, lock_channels=['s', 'v'])
    
    hip_ctrl = control.Control(shape='hip_ctrl_template', prefix='hip',
                                translate_to=pelvis_jnt, scale=rig_scale,
                                parent=body_ctrl.ctrl, lock_channels=['s', 'v'])
    ctrl_shape = cmds.listRelatives(hip_ctrl.ctrl, shapes=True)[0]
    cmds.setAttr(ctrl_shape + '.ove', 1)
    cmds.setAttr(ctrl_shape + '.ovc', 18)
    
    chest_ctrl = control.Control(shape='chest_ctrl_template', prefix='chest',
                                translate_to=spine_jnts[len(spine_jnts)-1], scale=rig_scale,
                                parent=body_ctrl.ctrl, lock_channels=['s', 'v'])
    
    spine_ctrl = control.Control(shape='spine_ctrl_template', prefix=prefix,
                                translate_to=[hip_ctrl.ctrl, chest_ctrl.ctrl], scale=rig_scale,
                                parent=body_ctrl.ctrl, lock_channels=['s', 'r', 'v'])
    ctrl_shape = cmds.listRelatives(spine_ctrl.ctrl, shapes=True)[0]
    cmds.setAttr(ctrl_shape + '.ove', 1)
    cmds.setAttr(ctrl_shape + '.ovc', 18)
    
    
    #SET UP RIBBON
    #create ribbon surface and add follicles
    ribbon.create_cv_curve('temp_spine_ribbon_crv_01', spine_jnts)
    ribbon_sfc = ribbon.loft_using_curve('temp_spine_ribbon_crv_01', 8, prefix)
    spine_follicles = ribbon.add_follicles(ribbon_sfc, 4)
    spine_ik_jnts = joint.duplicate(spine_jnts, prefix='ik')

    spine_follicles_grp = '_'.join([prefix,'follicles','grp'])
    cmds.group(spine_follicles, n=spine_follicles_grp)
    
    for i in range(len(spine_ik_jnts)):
        cmds.parent(spine_ik_jnts[i], spine_follicles[i])
    
    #create ribbon_wire_curve to drive the surface using wire deformer
    ribbon_wire_curve = 'ribbon_wire_crv'
    create_ep_curve(curve=ribbon_wire_curve, 
                          pos_ref_list=[spine_jnts[0], spine_jnts[len(spine_jnts)-1]],
                           degree=2)
    
    #create and add clusters
    ribbon_clstr_list = []
    for i in range(ribbon.get_curve_num_cvs(ribbon_wire_curve)):
        cmds.select(ribbon_wire_curve+'.cv[%d]' % i)
        temp_clstr_name = 'ribbon_clstr_'+str(i).zfill(2)+'_'
        ribbon_clstr_list.append(cmds.cluster(name=temp_clstr_name)[1])
        cmds.setAttr(temp_clstr_name+'Handle.visibility', 0)
        
    ribbon_clstrs_grp = cmds.group(ribbon_clstr_list, n='ribbon_clstrs_grp')
    
    #create wire deformer
    cmds.wire(ribbon_sfc, w=ribbon_wire_curve, dds=(0,50))
    ribbon_wire_grp = cmds.group([ribbon_wire_curve, ribbon_wire_curve+'BaseWire'],
                                  n='ribbon_wire_grp')
    
    #fix orientations for spine_ik_jnts
    for i in range(1,len(spine_ik_jnts))[::-1]:
        temp_jnt_driver = '_'.join(['ik', prefix, str(i+1).zfill(2)])
        temp_jnt_driven = '_'.join(['ik', prefix, str(i).zfill(2)])
        cmds.aimConstraint(temp_jnt_driver, temp_jnt_driven, 
                            aim=(1.0,0.0,0.0), wut='objectrotation', 
                            wuo=temp_jnt_driver)

    #setup ribbon twist
    ribbon_twist_sfc = 'spine_ribbon_twist_surface'
    cmds.duplicate(ribbon_sfc, n=ribbon_twist_sfc)
    twist_handle = ribbon.create_twist_deformer(sfc=ribbon_twist_sfc, prefix=prefix)

    twist_angle_plus_minus_node = connect_body_ctrl_to_ribbon(body_ctrl, twist_handle)

    connect_twist_ribbon(prefix, hip_ctrl, twist_angle_plus_minus_node, 'start')
    connect_twist_ribbon(prefix, chest_ctrl, twist_angle_plus_minus_node, 'end')
    
    twist_mult_node = 'spine_twist_master_mult_node'
    cmds.createNode('multiplyDivide', n=twist_mult_node)
    cmds.connectAttr(base_rig.master_ctrl.ctrl+'.rotateY', twist_mult_node+'.input1X')
    cmds.setAttr(twist_mult_node+'.input2X', -1)
    cmds.connectAttr(twist_mult_node+'.outputX', 'start'+twist_angle_plus_minus_node+'.input1D[2]')
    cmds.connectAttr(twist_mult_node+'.outputX', 'end'+twist_angle_plus_minus_node+'.input1D[2]')
    
    ribbon_bs = prefix+'_ribbon_blendshape'
    cmds.blendShape(ribbon_twist_sfc, ribbon_sfc, n=ribbon_bs)
    cmds.setAttr(ribbon_bs+'.'+ribbon_twist_sfc, 1)
    
    cmds.select(hip_ctrl.ctrl, chest_ctrl.ctrl)
    cmds.xform(rotateOrder='yzx')
    
    cmds.select(ribbon_sfc)
    cmds.reorderDeformers('wire1', ribbon_bs)
    
    
    #set up skel constraints
    cmds.select(d=True)
    for i in range(len(spine_jnts)-1):
        driver = spine_ik_jnts[i]
        driven = spine_jnts[i]
        cmds.pointConstraint(driver, driven, maintainOffset=False)
        cmds.orientConstraint(driver, driven, maintainOffset=False)
    
    ik_spine_04_orient_jnt = spine_ik_jnts[3]+'_orient'
    cmds.duplicate(spine_ik_jnts[3], n=ik_spine_04_orient_jnt)
    cmds.parent(ik_spine_04_orient_jnt, chest_ctrl.ctrl)
    cmds.makeIdentity(ik_spine_04_orient_jnt, t=0, r=1, s=0, apply=True)
    cmds.pointConstraint(ik_spine_04_orient_jnt, spine_jnts[3], maintainOffset=False)
    cmds.orientConstraint(ik_spine_04_orient_jnt, spine_jnts[3], maintainOffset=False)
    
    pelvis_orient_jnt = 'pelvis_orient'
    cmds.duplicate('pelvis', n=pelvis_orient_jnt, rc=True)
    cmds.delete(cmds.listRelatives(pelvis_orient_jnt))
    
    cmds.parent(pelvis_orient_jnt, hip_ctrl.ctrl)
    cmds.makeIdentity(pelvis_orient_jnt, t=0, r=1, s=0, apply=True)
    cmds.pointConstraint(pelvis_orient_jnt, 'pelvis', maintainOffset=False)
    cmds.orientConstraint(pelvis_orient_jnt, 'pelvis', maintainOffset=False)
    
    #AUTO MOVEMENT FOR spine_ctrl
    spine_ctrl_drv = 'spine_ctrl_drv'
    cmds.select(d=True)
    cmds.group(n=spine_ctrl_drv, em=True)
    
    cmds.delete(cmds.parentConstraint(spine_ctrl.ofst, spine_ctrl_drv))
    cmds.parent(spine_ctrl_drv, spine_ctrl.ofst)
    cmds.parent(spine_ctrl.ctrl, spine_ctrl_drv)
    
    #create joint for spine_ctrl
    create_spine_ctrl_auto_jnts(hip_ctrl, 'bottom', spine_ctrl, spine_ctrl_drv)
    create_spine_ctrl_auto_jnts(chest_ctrl, 'top', spine_ctrl, spine_ctrl_drv)
        
    #spine_ctrl auto switch
    cmds.addAttr(chest_ctrl.ctrl, shortName='midInfluence', keyable=True, 
                 defaultValue=0.0, minValue=0.0, maxValue=1.0)

    create_spine_ctrl_auto_switch(chest_ctrl, spine_ctrl_drv)
     
    
    #set up ctrl constraints
    cmds.parentConstraint(hip_ctrl.ctrl, ribbon_clstr_list[0], mo=True)
    cmds.parentConstraint(spine_ctrl.ctrl, ribbon_clstr_list[1], mo=True)
    cmds.parentConstraint(chest_ctrl.ctrl, ribbon_clstr_list[2], mo=True)


    #cleanup
    spine_sfc_grp = 'spine_sfc_grp'
    spine_deformers_grp = 'spine_deformers_grp'
    cmds.group([ribbon_sfc, ribbon_twist_sfc], name=spine_sfc_grp)
    cmds.group(twist_handle, name=spine_deformers_grp)
    cmds.parent([spine_follicles_grp, ribbon_wire_grp, 
                    ribbon_clstrs_grp, spine_sfc_grp, spine_deformers_grp],
                 rig_module.dnt_grp)
    

def connect_body_ctrl_to_ribbon(body_ctrl, twist_handle):    
    twist_mult_node = 'spine_twist_body_mult_node'
    cmds.createNode('multiplyDivide', n=twist_mult_node)
    cmds.connectAttr(body_ctrl.ctrl+'.rotateY', twist_mult_node+'.input1X')
    cmds.setAttr(twist_mult_node+'.input2X', -1)

    cmds.shadingNode('plusMinusAverage', asUtility=True, name='end_body_twist_add')
    cmds.connectAttr(twist_mult_node+'.outputX', 'end_body_twist_add.input1D[0]')
    cmds.connectAttr('end_body_twist_add.output1D', twist_handle[0]+'.endAngle')
    
    cmds.shadingNode('plusMinusAverage', asUtility=True, name='start_body_twist_add')
    cmds.connectAttr(twist_mult_node+'.outputX', 'start_body_twist_add.input1D[0]')
    cmds.connectAttr('start_body_twist_add.output1D', twist_handle[0]+'.startAngle')
    
    return '_body_twist_add'
    
def connect_twist_ribbon(prefix, ctrl, plus_minus_node, angle='start'):
    """
    connects sfc with twist deformer to spine_ribbon_sfc
    
    @param prefix: str, prefix required for any new nodes being created
    @param twist_handle: list(str), twist deformer's objs
    @param ctrl: Control obj, control to be connected to twist deformer's angle attr
    @param angle: str, either 'start' or 'end' based on which angle of the 
                        deformer we want to connect to
    @return None
    """
    twist_mult_node = prefix+'_twist_'+angle+'_mult_node'
    
    cmds.createNode('multiplyDivide', n=twist_mult_node)
    cmds.connectAttr(ctrl.ctrl+'.rotateY', twist_mult_node+'.input1X')
    cmds.setAttr(twist_mult_node+'.input2X', -1)
    cmds.connectAttr(twist_mult_node+'.outputX', angle+plus_minus_node+'.input1D[1]')


def create_spine_ctrl_auto_jnts(ctrl, position, spine_ctrl, drv_grp):
    """
    creates extra joints and locators required to calculate translation on 
    spine_ctrl. also makes necessary node connections.

    @param ctrl: Control obj, the ctrl to which the new joints are to be parented    
    @param position: str, either 'bottom' or 'top' based on the two possible ctrls
    @param spine_ctrl: Control obj, spine_ctrl for positioning the created '_end' joints
    @param drv_grp: str, the driver group that's going to move spine_ctrl
    @return None
    """
    cmds.select(d=True)
    drv_base_jnt = 'spine_drv_'+position+'_base'
    cmds.joint(n=drv_base_jnt)
    cmds.delete(cmds.parentConstraint(ctrl.ctrl, drv_base_jnt))
    
    drv_end_jnt = 'spine_drv_'+position+'_end'
    cmds.joint(n=drv_end_jnt)
    cmds.delete(cmds.parentConstraint(spine_ctrl.ctrl, drv_end_jnt))

    cmds.parent(drv_base_jnt, ctrl.ctrl)
    
    drv_end_loc = 'spine_driver_'+position+'_follow'
    cmds.spaceLocator(n=drv_end_loc)
    cmds.delete(cmds.parentConstraint(drv_end_jnt, drv_end_loc))
    cmds.parent(drv_end_loc, ctrl.ofst)
    cmds.pointConstraint(drv_end_jnt, drv_end_loc)

    cmds.shadingNode('plusMinusAverage', asUtility=True, name='spine_bend_side_pma')
    cmds.shadingNode('plusMinusAverage', asUtility=True, name='spine_bend_front_pma')
    if position == 'bottom':
        cmds.connectAttr(drv_end_loc+'.translate.translateX', 'spine_bend_side_pma.input1D[0]')
        cmds.connectAttr(drv_end_loc+'.translate.translateZ', 'spine_bend_front_pma.input1D[0]')
    elif position == 'top':
        cmds.connectAttr(drv_end_loc+'.translate.translateX', 'spine_bend_side_pma.input1D[1]')
        cmds.connectAttr(drv_end_loc+'.translate.translateZ', 'spine_bend_front_pma.input1D[1]')
#    cmds.connectAttr('spine_bend_side_pma.output1D', spine_anim_drv+'.translate.translateX')
#    cmds.connectAttr('spine_bend_front_pma.output1D', spine_anim_drv+'.translate.translateZ')

def create_spine_ctrl_auto_switch(chest_ctrl, spine_ctrl_drv):
    tz_blendcolors_node = 'mid_control_tz_influence'
    cmds.shadingNode('blendColors', asUtility=True, name=tz_blendcolors_node)
    cmds.connectAttr('spine_bend_front_pma.output1D', tz_blendcolors_node+'.color1R')
    cmds.connectAttr(chest_ctrl.ctrl+'.midInfluence', tz_blendcolors_node+'.blender')
    cmds.connectAttr(tz_blendcolors_node+'.outputR', spine_ctrl_drv+'.translateZ')
    
    tx_blendcolors_node = 'mid_control_tx_influence'
    cmds.shadingNode('blendColors', asUtility=True, name=tx_blendcolors_node)
    cmds.connectAttr('spine_bend_side_pma.output1D', tx_blendcolors_node+'.color1R')
    cmds.connectAttr(chest_ctrl.ctrl+'.midInfluence', tx_blendcolors_node+'.blender')
    cmds.connectAttr(tx_blendcolors_node+'.outputR', spine_ctrl_drv+'.translateX')
    
    
    
    
    
        