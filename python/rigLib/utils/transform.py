"""
transform utils @ utils

functions to manipulate and create transforms
"""

import maya.cmds as cmds
from . import name

def make_offset_grp(obj, prefix=''):
    """
    make offset group for given object
    
    @param object: str, transform object we're giving the offset group to
    @param prefix: str, name of the offset group to be followed by '_ofst'
    @return: str, name of new offset group
    """
    
    if not prefix:
        prefix = name.remove_suffix(obj)
        
    offset_grp = cmds.group(n=prefix+'ofst', empty=True)
    
    object_parents = cmds.listRelatives(obj, p=True)
    if object_parents:
        cmds.parent(offset_grp, object_parents[0])
    
    #match object transforms
    cmds.delete(cmds.parentConstraint(obj, offset_grp))
    cmds.delete(cmds.scaleConstraint(obj, offset_grp))
    
    #parent object under offset group
    cmds.parent(obj, offset_grp)
    
    return offset_grp
    
    
def snap(driver, driven):
    """
    matches the translation and orientation of an object to another object
    
    @param driver: str, name of object to be snapped to
    @param driven: str, name of object being snapped
    @return: None
    """
    cmds.delete(cmds.parentConstraint(driver, driven)[0])
    
    
def point_snap(driver, driven):
    """
    matches the translation of an object to another object
    
    @param driver: str, name of object to be snapped to
    @param driven: str, name of object being snapped
    @return: None
    """
    cmds.delete(cmds.pointConstraint(driver, driven)[0])
    
def snap_pivot(pivot, obj):
    piv = cmds.xform(pivot, q=True, ws=True, t=True)
    cmds.xform(obj, ws=True, piv=piv)
    
    
    
    
