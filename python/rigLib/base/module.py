"""
module for creating top rig structure and rig module
"""

import maya.cmds as cmds
from . import control

scene_object_type = 'rig'

master_ctrl_temp = 'master_ctrl_template'
teardrop_ctrl_temp = 'teardrop_ctrl_template'
cube_ctrl_temp = 'cube_ctrl_template'
sphere_ctrl_temp = 'sphere_ctrl_template'
pin_ctrl_temp = 'pin_ctrl_template'
bowl_ctrl_temp = 'bowl_ctrl_template'

class Base():
    
    """
    class for creating top rig structure
    """
    
    def __init__(
            self,
            character_name='new',
            scale=1.0,
            ):
        
        """
        @param character_name: str, character name
        @param scale: float, general scale of the rig
        @return: None
        """
        
        self.top_grp = cmds.group(name=character_name+'_grp', empty=True)
        self.geo_grp = cmds.group(name='geo_grp', empty=True, parent=self.top_grp)
        self.rig_grp = cmds.group(name='rig_grp', empty=True, parent=self.top_grp)
        
        #create attrs for top_grp
        character_name_attr = 'character_name'
        scene_object_type_attr = 'scene_object_type'
        for attr in [character_name_attr, scene_object_type_attr]:
            cmds.addAttr(self.top_grp, longName=attr, dataType='string')

        cmds.setAttr(self.top_grp+'.'+character_name_attr, character_name, type='string', lock=True)
        cmds.setAttr(self.top_grp+'.'+scene_object_type_attr, scene_object_type, type='string', lock=True)
        
        #create master control
        self.master_ctrl = control.Control(
                        prefix='master',
                        shape=master_ctrl_temp,
                        scale=scale*2,
                        parent=self.rig_grp,
                        lock_channels=['s', 'v'])
        
        self.dnt_grp = cmds.group(name='rig_dnt_grp', empty=True, parent=self.rig_grp) #this will not inherit the rig movement
        cmds.setAttr(self.dnt_grp+'.visibility', False)
        #cmds.setAttr(self.dnt_grp+'.it', False, l=True) #.it = inheritTransforms        

class Module():
    
    """
    class for creating module rig structure
    """
    
    def __init__(
            self,
            prefix='new',
            create_dnt_grp=False,
            base_obj=None
            ):
        
        """
        @param prefix: str, prefix to the name of new modules
        @param base_obj: instance of base.module.Base class
        @return: None
        """
        
        self.top_grp = cmds.group(name=prefix+'_module_grp', empty=True)
        
        self.jnt_grp = cmds.group(name=prefix+'_drv_grp', empty=True, parent=self.top_grp)
        self.ctrl_grp = cmds.group(name=prefix+'_anim_grp', empty=True, parent=self.top_grp)
        
        if create_dnt_grp == True:
            self.dnt_grp = cmds.group(name=prefix+'_dnt_grp', empty=True, parent=base_obj.dnt_grp)
        
        #self.misc_grp = cmds.group(name=prefix+'_misc_grp', empty=True, parent=self.top_grp) #for ik handles and such
        #self.dnt_grp = cmds.group(name=prefix+'_parts_grp', empty=True, parent=self.top_grp) #for things that aren't going to have transformations
        #cmds.setAttr(self.dnt_grp+'.it', False, l=True) #.it = inheritTransforms
        
        #parent module
        if base_obj:
            cmds.parent(self.top_grp, base_obj.master_ctrl.ctrl)
            
            