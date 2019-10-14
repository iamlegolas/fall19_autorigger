"""
transform utils @ utils

functions to manipulate and create transforms
"""

import maya.cmds as cmds
from . import name
from pymel.api.plugins import Transform

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
    
def setup_distance_dimension_node(prefix, start_obj, end_obj):
    transform_node = prefix+'_distance_dim'
    shape_node = cmds.createNode('distanceDimShape', n=transform_node+'_shape')    
    cmds.rename(cmds.listRelatives(shape_node, parent=True)[0], transform_node)
    
    start_obj_dcmps_node = prefix+'_start_obj_decomposeMatrix_node'
    end_obj_dcmps_node = prefix+'_end_obj_decomposeMatrix_node'
    cmds.shadingNode('decomposeMatrix', asUtility=True, name=start_obj_dcmps_node)
    cmds.shadingNode('decomposeMatrix', asUtility=True, name=end_obj_dcmps_node)
    
    cmds.connectAttr(start_obj+'.worldMatrix[0]', start_obj_dcmps_node+'.inputMatrix')
    cmds.connectAttr(end_obj+'.worldMatrix[0]', end_obj_dcmps_node+'.inputMatrix')
    
    cmds.connectAttr(start_obj_dcmps_node+'.outputTranslate', shape_node+'.startPoint')
    cmds.connectAttr(end_obj_dcmps_node+'.outputTranslate', shape_node+'.endPoint')
    
    return [transform_node, shape_node]
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
