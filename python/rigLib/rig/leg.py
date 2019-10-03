"""
spine @ rig
"""

import maya.cmds as cmds

from ..base import module
from ..base import control
from rigLib.utils import joint, ribbon
from rigLib.utils.ribbon import loft_using_curve, create_ep_curve

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
    rig_module = module.Module(prefix=side+'_'+prefix, base_obj=base_rig, create_dnt_grp=True)
    
    
    #make spine controls
    ik_foot_ctrl = control.Control(shape=side+'_foot_ctrl_template', prefix=side+'_foot_IK',
                                translate_to=leg_jnts[2], scale=rig_scale,
                                parent=rig_module.ctrl_grp, lock_channels=['s', 'v'])
    
    ik_knee_ctrl = control.Control(shape='sphere_ctrl_template', prefix=side+'_knee_IK',
                                translate_to=leg_jnts[1], rotate_to=leg_jnts[1], scale=rig_scale,
                                parent=rig_module.ctrl_grp, lock_channels=['v'])
    
    cmds.parent(ik_knee_ctrl.ctrl, leg_jnts[1])
    cmds.makeIdentity(ik_knee_ctrl.ctrl, t=1, r=1, s=1, apply=True)
    if side == 'l':
        cmds.xform(ik_knee_ctrl.ctrl, os=True, t=(0,-30,0))
    else:
        cmds.xform(ik_knee_ctrl.ctrl, os=True, t=(0,30,0))
    cmds.parent(ik_knee_ctrl.ctrl, w=True)
    cmds.makeIdentity(ik_knee_ctrl.ctrl, t=1, r=1, s=1, apply=True)
    cmds.parent(ik_knee_ctrl.ofst, ik_knee_ctrl.ctrl)
    cmds.makeIdentity(ik_knee_ctrl.ofst, t=1, r=1, s=1, apply=True)
    cmds.parent(ik_knee_ctrl.ofst, w=True)
    cmds.parent(ik_knee_ctrl.ctrl, ik_knee_ctrl.ofst)
    cmds.parent(ik_knee_ctrl.ofst, rig_module.ctrl_grp)
    
    leg_ik_handle = cmds.ikHandle(n=side+'_'+prefix+'_ikHandle', sj=leg_jnts[0], ee=leg_jnts[2], sol='ikRPsolver')[0]
    cmds.hide(leg_ik_handle)
    ball_ik_handle = cmds.ikHandle(n=side+'_'+prefix+'_ball_ikHandle', sj=leg_jnts[2], ee=leg_jnts[3], sol='ikSCsolver')[0]
    cmds.hide(ball_ik_handle)
    toe_ik_handle = cmds.ikHandle(n=side+'_'+prefix+'_toe_ikHandle_', sj=leg_jnts[3], ee=leg_jnts[4], sol='ikSCsolver')[0]
    cmds.hide(toe_ik_handle)
    cmds.parent([leg_ik_handle, ball_ik_handle, toe_ik_handle], ik_foot_ctrl.ctrl)
    
    
    cmds.poleVectorConstraint(ik_knee_ctrl.ctrl, leg_ik_handle)
    
    

    
    pass