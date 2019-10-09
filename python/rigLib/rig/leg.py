"""
spine @ rig
"""

import maya.cmds as cmds

from ..base import module
from ..base import control
from rigLib.utils import joint, limbs, transform

def build(
        leg_jnts,
        side='l',
        prefix='leg',
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
    rig_module = module.Module(prefix=side+'_'+prefix, base_obj=base_rig, create_dnt_grp=True, drv_pos_obj='pelvis')
    
    #create drv skels
    ik_leg_jnts = joint.duplicate(leg_jnts, prefix='ik', maintain_hierarchy=True)
    fk_leg_jnts = joint.duplicate(leg_jnts, prefix='fk', maintain_hierarchy=True)
    cmds.parent(ik_leg_jnts[0], fk_leg_jnts[0], rig_module.drv_grp)
    
    #create IK controls
    ik_anim_grp = side+'_'+prefix+'_ik_anim_grp'
    cmds.group(n=ik_anim_grp, em=True, p=rig_module.ctrl_grp)
    
    temp_pole_loc = limbs.create_pole_vector_locator(side+'_'+prefix, leg_jnts[1], [0,-30,0])
    ik_foot_ctrl = control.Control(shape=side+'_foot_ctrl_template', prefix=side+'_foot_IK',
                                translate_to=leg_jnts[2], scale=rig_scale,
                                parent=ik_anim_grp, lock_channels=['s', 'v'])
    
    ik_knee_ctrl = control.Control(shape='sphere_ctrl_template', prefix=side+'_knee_IK',
                                translate_to=temp_pole_loc, scale=rig_scale,
                                parent=ik_anim_grp, lock_channels=['v'])
    cmds.delete(temp_pole_loc)
    ik_ctrl_list = [ik_foot_ctrl, ik_knee_ctrl]
    
    #create FK controls
    fk_anim_grp = side+'_'+prefix+'_fk_anim_grp'
    cmds.group(n=fk_anim_grp, em=True, p=rig_module.ctrl_grp)

    fk_thigh_ctrl = control.Control(shape='cube_ctrl_template', prefix=side+'_thigh_FK',
                                    translate_to=[leg_jnts[0], leg_jnts[1]], rotate_to=leg_jnts[0],
                                    scale=rig_scale, parent=fk_anim_grp, 
                                    lock_channels=['s', 'v'])
    transform.snap_pivot(leg_jnts[0], fk_thigh_ctrl.ctrl)
    transform.snap_pivot(leg_jnts[0], fk_thigh_ctrl.ofst)
    
    fk_calf_ctrl = control.Control(shape='cube_ctrl_template', prefix=side+'_calf_FK',
                                    translate_to=[leg_jnts[1], leg_jnts[2]], rotate_to=leg_jnts[1],
                                    scale=rig_scale*0.7, parent=fk_thigh_ctrl.ctrl, 
                                    lock_channels=['s', 'v'])
    transform.snap_pivot(leg_jnts[1], fk_calf_ctrl.ctrl)
    transform.snap_pivot(leg_jnts[1], fk_calf_ctrl.ofst)
    
    fk_foot_ctrl = control.Control(shape='cube_ctrl_template', prefix=side+'_foot_FK',
                                translate_to=[leg_jnts[2], leg_jnts[3]], rotate_to=leg_jnts[3],
                                scale=rig_scale*0.6, parent=fk_calf_ctrl.ctrl, 
                                lock_channels=['s', 'v'])
    transform.snap_pivot(leg_jnts[2], fk_foot_ctrl.ctrl)
    transform.snap_pivot(leg_jnts[2], fk_foot_ctrl.ofst)
        
    #hook up FK ctrls
    fk_ctrl_list = [fk_thigh_ctrl, fk_calf_ctrl, fk_foot_ctrl]
    for i in range(len(fk_ctrl_list)):
        cmds.orientConstraint(fk_ctrl_list[i].ctrl, fk_leg_jnts[i], mo=False)
    
    #set up ik
    leg_ik_handle = cmds.ikHandle(n=side+'_leg_ikHandle', sj=ik_leg_jnts[0], ee=ik_leg_jnts[2], sol='ikRPsolver')[0]
    ball_ik_handle = cmds.ikHandle(n=side+'ball_ikHandle', sj=ik_leg_jnts[2], ee=ik_leg_jnts[3], sol='ikSCsolver')[0]
    toe_ik_handle = cmds.ikHandle(n=side+'toe_ikHandle_', sj=ik_leg_jnts[3], ee=ik_leg_jnts[4], sol='ikSCsolver')[0]
    
    ik_list = [leg_ik_handle, ball_ik_handle, toe_ik_handle]
    cmds.hide(ik_list)
    cmds.parent(ik_list, ik_foot_ctrl.ctrl)
    cmds.poleVectorConstraint(ik_knee_ctrl.ctrl, leg_ik_handle)
    
    #set up ik/fk switch
    limbs.setup_ikfk_switch(base_rig, side, prefix, 
                            ik_leg_jnts[0:3], fk_leg_jnts[0:3], leg_jnts[0:3], 
                            ik_anim_grp, fk_anim_grp)
    
    #cleanup
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    