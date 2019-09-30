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

    connect_twist_ribbon(prefix, twist_handle, hip_ctrl, 'start')
    connect_twist_ribbon(prefix, twist_handle, chest_ctrl, 'end')
    
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
    
    
    
    #set up ctrl constraints
    cmds.parentConstraint(hip_ctrl.ctrl, ribbon_clstr_list[0], mo=True)
    cmds.parentConstraint(spine_ctrl.ctrl, ribbon_clstr_list[1], mo=True)
    cmds.parentConstraint(chest_ctrl.ctrl, ribbon_clstr_list[2], mo=True)


    #cleanup
    cmds.group([ribbon_sfc, ribbon_twist_sfc], name='spine_sfc_grp')
    cmds.group(twist_handle, name='spine_deformers_grp')
#    cmds.parent([spine_follicles_grp, ribbon_wire_grp, ribbon_clstrs_grp],
#                 rig_module.dnt_grp)


def connect_twist_ribbon(prefix, twist_handle, ctrl='', angle='start'): 
    if angle == 'start':
        twist_mult_node = prefix+'_twist_start_mult_node'
    elif angle == 'end':
        twist_mult_node = prefix+'_twist_end_mult_node'
    else: 
        print 'Error: Angle parameter can either be "start" or "end"'
        pass
    
    cmds.createNode('multiplyDivide', n=twist_mult_node)
    cmds.setAttr(twist_mult_node+'.input2X', -1)
    cmds.connectAttr(ctrl.ctrl+'.rotateY', twist_mult_node+'.input1X')
#    cmds.connectAttr(twist_mult_node+'.outputX', twist_handle[0]+'.'+angle+'Angle')

    
    
    
    
    
    
        