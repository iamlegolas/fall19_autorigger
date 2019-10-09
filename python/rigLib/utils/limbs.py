"""
limb utils @utils
has different service functions required while working with limbs
"""

import maya.cmds as cmds

def create_pole_vector_locator(prefix, mid_jnt, t_vec):
    """
    create locator where control for IK pole vector needs to be
    
    @param mid_jnt: str, name of the limb's mid joint i.e. the elbow or knee
    @return name of the locator
    """
    
    loc = prefix+'_temp_loc'
    cmds.spaceLocator(n=loc)
    cmds.delete(cmds.parentConstraint(mid_jnt, loc, mo=False))
    cmds.parent(loc, mid_jnt)

    cmds.xform(loc, os=True, t=t_vec)

    cmds.parent(loc, w=True)
    cmds.makeIdentity(loc, t=1, r=1, s=1, apply=True)

    return loc

def setup_ikfk_switch(base_rig, side, prefix, 
                      ik_jnts, fk_jnts, bnd_jnts, ik_anim_grp, fk_anim_grp):

    blend_attr_name = side+'_'+prefix
    cmds.addAttr(base_rig.ikfk_ctrl.ctrl, k=True , ln=blend_attr_name,
                 defaultValue=0.0, minValue=0.0, maxValue=1.0)
    
    for i in range(len(bnd_jnts)):
        rotate_blend_node_name = side+'_'+prefix+'_ikfk_rotate_blend_node_'+str(i)
        cmds.shadingNode('blendColors', asUtility=True, name=rotate_blend_node_name)
        
        cmds.connectAttr(base_rig.ikfk_ctrl.ctrl+'.'+blend_attr_name, 
                         rotate_blend_node_name+'.blender')
        cmds.connectAttr(fk_jnts[i]+'.rotate', rotate_blend_node_name+'.color2')
        cmds.connectAttr(ik_jnts[i]+'.rotate', rotate_blend_node_name+'.color1')
        cmds.connectAttr(rotate_blend_node_name+'.output', bnd_jnts[i]+'.rotate')
        
        cmds.setDrivenKeyframe(fk_anim_grp, at='visibility', 
                               cd=base_rig.ikfk_ctrl.ctrl+'.'+blend_attr_name, 
                               dv=0, v=1)
        cmds.setDrivenKeyframe(fk_anim_grp, at='visibility', 
                               cd=base_rig.ikfk_ctrl.ctrl+'.'+blend_attr_name, 
                               dv=1, v=0)
        cmds.setDrivenKeyframe(ik_anim_grp, at='visibility', 
                               cd=base_rig.ikfk_ctrl.ctrl+'.'+blend_attr_name, 
                               dv=1, v=1)
        cmds.setDrivenKeyframe(ik_anim_grp, at='visibility', 
                               cd=base_rig.ikfk_ctrl.ctrl+'.'+blend_attr_name, 
                               dv=0, v=0)
        
        
        '''
        translate_blend_node_name = side+'_'+prefix+'_ikfk_translate_blend_node_'+str(i)
        cmds.shadingNode('blendColors', asUtility=True, name=translate_blend_node_name)
        
        cmds.connectAttr(base_rig.ikfk_ctrl.ctrl+'.'+blend_attr_name, 
                         translate_blend_node_name+'.blender')
        cmds.connectAttr(fk_jnts[i]+'.translate', translate_blend_node_name+'.color2')
        cmds.connectAttr(ik_jnts[i]+'.translate', translate_blend_node_name+'.color1')
        cmds.connectAttr(translate_blend_node_name+'.output', bnd_jnts[i]+'.translate')
        '''
        
        