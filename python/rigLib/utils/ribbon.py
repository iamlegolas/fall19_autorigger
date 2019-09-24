"""
ribbon utils @utils
has different service functions required while working with ribbons
"""

import maya.cmds as cmds

def create_curve_using(curve, pos_ref_list):
    """
    create CV curve with CVs at positions of the objects in pos_ref_list
    
    @param curve: str, name of the CV curve to be created
    @param pos_ref_list: list(str), list of object names to extract positions from
    @return None
    """
    
    obj_pos_list = []
    for obj in pos_ref_list:
        obj_pos_list.append(cmds.xform(obj, q=True, ws=True, t=True))
    
    cmds.curve(n=curve, point=[obj_pos_list[0]])

    for i in range(1, len(pos_ref_list)):
        cmds.curve(curve, append=True, point=[obj_pos_list[i]], ws=True)
        
def loft_using_curve(curve, width, ribbon_sfc):
    """
    duplicate curve and loft
    @param curve: str, given CV curve name to process
    @param width: double, width of the CV curve
    @param ribbon_sfc: str, name of the ribbon surface to be created
    @return: 
    """
    
    curve_02 = cmds.duplicate(curve)
    cmds.xform(curve, ws=True, t=(4,0,0))
    cmds.xform(curve_02, ws=True, t=(-4,0,0))