"""
module for creating rig controls
"""

import maya.cmds as cmds

class Control():
    
    """
    class for creating rig controls
    """
    
    def __init__(
                self,
                shape = '',
                prefix='new',
                scale=1.0,
                translate_to='',
                rotate_to='',
                parent='',
                lock_channels=['v']
                ):
        
        """
        @param prefix: str, prefix to the name of new modules
        @param scale: float, scale value for control shapes
        @param translate_to: str, reference object for control position
        @param rotate_to: str, reference object for control orientation
        @param parent: str, object to be parent of new control
        @param lock_channels: list(str), list of channels on control to be locked and non-keyable
        @return: None 
        """
        
        if cmds.objExists(shape):
            ctrl_object = cmds.duplicate(shape)[0]
            cmds.scale(scale, scale, scale, ctrl_object, pivot=(0, 0, 0), absolute=True)
            cmds.makeIdentity(ctrl_object, t=0, r=0, s=1, apply=True)
            cmds.parent(ctrl_object, world=True)
        
        else:
            ctrl_object = cmds.circle(ch=False, normal=[1,0,0], radius=scale)[0]

        ctrl_object = cmds.rename(ctrl_object, prefix+'_ctrl')
        ctrl_offset = cmds.group(n=prefix+'_ofst', empty=True)
        cmds.parent(ctrl_object, ctrl_offset)
        
        #color control
        ctrl_shape = cmds.listRelatives(ctrl_object, shapes=True)[0]
        cmds.setAttr(ctrl_shape + '.ove', 1) #enable overrides
        
        if prefix.startswith('l'):
            cmds.setAttr(ctrl_shape + '.ovc', 6) #override color

        elif prefix.startswith('r'):
            cmds.setAttr(ctrl_shape + '.ovc', 13) #override color
        
        else:
            cmds.setAttr(ctrl_shape + '.ovc', 22) #override color
        
        
        #translate control
        if cmds.objExists(translate_to):
            cmds.delete(cmds.pointConstraint(translate_to, ctrl_offset))
        #rotate control
        if cmds.objExists(rotate_to):
            cmds.delete(cmds.orientConstraint(rotate_to, ctrl_offset))
        #parent control
        if cmds.objExists(parent):
            cmds.parent(ctrl_offset, parent)    
           
        #lock control channels
        single_attr_lock_list = []
        for lock_channel in lock_channels:
            if lock_channel in ['t','r','s']:
                for axis in ['x','y','z']:
                    single_attr_lock_list.append(lock_channel+axis)
        
            else:
                single_attr_lock_list.append(lock_channel)
                
        for attr in single_attr_lock_list:
            cmds.setAttr(ctrl_object+'.'+attr, lock=True, keyable=False)
            
            
        #add public members
        self.ctrl = ctrl_object
        self.ofst = ctrl_offset
    