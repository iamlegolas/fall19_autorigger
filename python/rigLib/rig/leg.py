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
    
    pass