"""
spine @ rig
"""

import maya.cmds as cmds

from ..base import module
from ..base import control
from rigLib.utils import joint, ribbon
from rigLib.utils.ribbon import loft_using_curve, create_ep_curve

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
    rig_module = module.Module(prefix=prefix, base_obj=base_rig, create_dnt_grp=True)
    
    
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
    
    spine_ctrl = control.Control(shape='spine_ctrl_template', prefix=prefix,
                                translate_to=[hip_ctrl.ctrl, chest_ctrl.ctrl], scale=rig_scale,
                                parent=body_ctrl.ctrl, lock_channels=['s'])
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
    
    #fix orientations for ik_spine_jnts
    for i in range(1,len(spine_ik_jnts))[::-1]:
        temp_jnt_driver = '_'.join(['ik', prefix, str(i+1).zfill(2)])
        temp_jnt_driven = '_'.join(['ik', prefix, str(i).zfill(2)])
        cmds.aimConstraint(temp_jnt_driver, temp_jnt_driven, 
                            aim=(1.0,0.0,0.0), wut='objectrotation', 
                            wuo=temp_jnt_driver)

    #set up ctrl constraints
    '''
    cmds.parentConstraint(hip_anim, ribbon_clstr_list[0], mo=True)
    cmds.parentConstraint(spine_anim, ribbon_clstr_list[1], mo=True)
    cmds.parentConstraint(chest_anim, ribbon_clstr_list[2], mo=True)
    '''

    #cleanup
#    cmds.parent([spine_follicles_grp, ribbon_wire_grp, ribbon_clstrs_grp],
#                 rig_module.dnt_grp)
            
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