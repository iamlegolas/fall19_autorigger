"""
spine @ rig
"""

import maya.cmds as cmds

from ..base import module
from ..base import control
from rigLib.utils import joint, ribbon

def build(
        pelvis_jnt,
        spine_jnts,
        #spine_crv,
        prefix='spine',
        rig_scale=1.0,
        base_rig=None
        ):
    
    """
    @param spine_jnts: list(str), list of 6 spine jnts
    @param root_jnt: str, root_jnt
    #@param spine_crv: str, name of spine cubic curve with 5 CVs
    @param body_loc: str, reference transform for position of body ctrl
    @param chest_loc: str, reference transform for position of chest ctrl
    @param pelvis_loc: str, reference transform for position of pelvis ctrl
    @param prefix: str, prefix to name new object
    @param rig_scale: float, scale factor for size of controls
    @param base_rig: instance of base.module.Base class
    @return: dictionary with rig module objects 
    """
    
    #make rig module
    rig_module = module.Module(prefix='spine', base_obj=base_rig)
    
    
    #make spine controls
    body_ctrl = control.Control(shape='body_ctrl_template', prefix='body',
                                translate_to=pelvis_jnt, scale=rig_scale,
                                parent=rig_module.ctrl_grp, lock_channels=['s'])
    
    hip_ctrl = control.Control(shape='hip_ctrl_template', prefix='hip',
                                translate_to=pelvis_jnt, scale=rig_scale,
                                parent=body_ctrl.ctrl, lock_channels=['s'])
    ctrl_shape = cmds.listRelatives(hip_ctrl.ctrl, shapes=True)[0]
    cmds.setAttr(ctrl_shape + '.ove', 1)
    cmds.setAttr(ctrl_shape + '.ovc', 18)
    
    chest_ctrl = control.Control(shape='chest_ctrl_template', prefix='chest',
                                translate_to=spine_jnts[len(spine_jnts)-1], scale=rig_scale,
                                parent=body_ctrl.ctrl, lock_channels=['s'])
    
    spine_ctrl = control.Control(shape='spine_ctrl_template', prefix='spine',
                                translate_to=[hip_ctrl.ctrl, chest_ctrl.ctrl], scale=rig_scale,
                                parent=body_ctrl.ctrl, lock_channels=['s'])
    ctrl_shape = cmds.listRelatives(spine_ctrl.ctrl, shapes=True)[0]
    cmds.setAttr(ctrl_shape + '.ove', 1)
    cmds.setAttr(ctrl_shape + '.ovc', 18)
    
    
    #set up the ribbon
    
    ribbon.create_curve_using('temp_spine_ribbon_crv_01', spine_jnts)
    
    '''
    #make spineIK
    spine_ik_name = prefix+'_ikh'
    spine_crv_name = 'spine_crv'
    spine_ik = cmds.ikHandle(n=spine_ik_name, sol='ikSplineSolver', sj=spine_jnts[0], ee=spine_jnts[len(spine_jnts)-1])
    spine_crv = cmds.listRelatives(cmds.listRelatives(spine_ik)[0], p=True, type='transform')[0]
    cmds.rename(spine_crv, spine_crv_name)
    
    cmds.hide(spine_ik_name)
    cmds.parent(spine_ik_name, rig_module.parts_grp)
    
    #make spine curve clusters
    spine_crv_cvs = cmds.ls(spine_crv_name + '.cv[*]', fl=True) #fl=flatten so we have one CV for each item
    num_spine_cvs = len(spine_crv_cvs)
    spine_crv_cls = []
    
    for i in range(num_spine_cvs):
        
        cls = cmds.cluster(spine_crv_cvs[i], n=prefix+'_cls_%d' % (i+1))[1]
        spine_crv_cls.append(cls)
        
    cmds.hide(spine_crv_cls)
    
    #make controls
    body_ctrl = control.Control(prefix=prefix+'_body', translate_to=body_loc, scale=rig_scale*10, 
                                parent=rig_module.ctrl_grp)
    
    chest_ctrl = control.Control(prefix=prefix+'_chest', translate_to=chest_loc, scale=rig_scale*10, 
                                parent=body_ctrl.ctrl_name)
    
    pelvis_ctrl = control.Control(prefix=prefix+'_pelvis', translate_to=pelvis_loc, scale=rig_scale*10, 
                                parent=body_ctrl.ctrl_name)
    
    mid_ctrl = control.Control(prefix=prefix+'_mid', translate_to=spine_crv_cls[2], scale=rig_scale*10, 
                                parent=body_ctrl.ctrl_name)
    
    #attach controls
    cmds.parentConstraint(chest_ctrl.ctrl_name, pelvis_ctrl.ctrl_name, mid_ctrl.ofst_name, sr=['x','y','z'], mo=True)

    #attach clusters
    cmds.parent(spine_crv_cls[3:], chest_ctrl.ctrl_name)
    cmds.parent(spine_crv_cls[2], mid_ctrl.ctrl_name)
    cmds.parent(spine_crv_cls[:2], pelvis_ctrl.ctrl_name)

    #setup IK twist
    cmds.setAttr(spine_ik_name+'.dTwistControlEnable', True)
    cmds.setAttr(spine_ik_name+'.dWorldUpType', 1)
    """
    cmds.connectAttr(chest_ctrl.ctrl_name + '.worldMatrix[0]', spine_ik_name + '.dWorldUpMatrixEnd')
    cmds.connectAttr(pelvis_ctrl.ctrl_name + '.worldMatrix[0]', spine_ik_name + '.dWorldUpMatrix')
    
    ##he added a parent constraint here for root_jnt being driven by the pelvis_ctrl
    
    return {'module':rig_module}
    """
    '''