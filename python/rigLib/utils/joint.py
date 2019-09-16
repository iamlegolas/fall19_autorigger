"""
joint utils @utils
has different service functions required while working with joints
"""

import maya.cmds as cmds

def list_jnt_hierarchy(top_jnt, with_end_jnts=True):
    """
    list joint hierarchy starting with top_jnt
    
    @param top_jnt: str, joint to get listed with its joint hierarchy
    @param with_end_jnts: boolean, list hierarchy to include end joints or not?
    @return list(str), listed joints starting with top joint
    """
    
    listed_jnts = cmds.listRelatives(top_jnt, type='joint', allDescendents=True)
    listed_jnts.append(top_jnt)
    listed_jnts.reverse()
    
    complete_jnts = listed_jnts[:]
    
    if not with_end_jnts:
        complete_jnts = [j for j in listed_jnts if cmds.listRelatives(j, c=True, type='joint')]
        
    return complete_jnts