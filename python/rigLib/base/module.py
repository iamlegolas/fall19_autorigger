"""
module for creating top rig structure and rig module
"""

import maya.cmds as cmds
from . import control

scene_object_type = 'rig'

class Base():
    
    """
    class for creating top rig structure
    """
    
    def __init__(
            self,
            character_name='new',
            scale=1.0,
            main_ctrl_attach_obj=''
            ):
        
        """
        @param character_name: str, character name
        @param scale: float, general scale of the rig
        @return: None
        """
        
        self.top_grp = cmds.group(name=character_name+'_rig_grp', empty=True)
        self.rig_grp = cmds.group(name='rig_grp', empty=True, parent=self.top_grp)
        self.geo_grp = cmds.group(name='geo_grp', empty=True, parent=self.top_grp)
        
        character_name_attr = 'character_name'
        scene_object_type_attr = 'scene_object_type'
        
        for attr in [character_name_attr, scene_object_type_attr]:
            cmds.addAttr(self.top_grp, longName=attr, dataType='string')

        cmds.setAttr(self.top_grp+'.'+character_name_attr, character_name, type='string', lock=True)
        cmds.setAttr(self.top_grp+'.'+scene_object_type_attr, scene_object_type, type='string', lock=True)
        
        #create global control
        global_1_ctrl = control.Control(
                        prefix='global_01',
                        scale=scale*20,
                        parent=self.rig_grp,
                        lock_channels=['v'])
        global_2_ctrl = control.Control(
                        prefix='global_02',
                        scale=scale*18,
                        parent=global_1_ctrl.ctrl_name,
                        lock_channels=['s', 'v'])
        
        self.__flatten_global_ctrl_shape(global_1_ctrl.ctrl_name)
        self.__flatten_global_ctrl_shape(global_2_ctrl.ctrl_name)
        
        for axis in ['y','z']:
            cmds.connectAttr(global_1_ctrl.ctrl_name+'.sx', global_1_ctrl.ctrl_name+'.s'+axis)
            cmds.setAttr(global_1_ctrl.ctrl_name+'.s', keyable=False)
            
        #make more groups
        self.jnt_grp = cmds.group(name='jnt_grp', empty=True, parent=global_2_ctrl.ctrl_name)
        self.module_grp = cmds.group(name='module_grp', empty=True, parent=global_2_ctrl.ctrl_name)
        
        self.parts_grp = cmds.group(name='parts_grp', empty=True, parent=self.rig_grp) #this will not inherit the rig movement
        cmds.setAttr(self.parts_grp+'.it', False, l=True) #.it = inheritTransforms
        
        # make main ctrl
        main_ctrl = control.Control(
                        prefix='main',
                        scale=scale*2,
                        parent=global_2_ctrl.ctrl_name,
                        translate_to = main_ctrl_attach_obj,
                        lock_channels=['t','r','s','v'])
        
        self._adjust_main_ctrl_shape(main_ctrl, scale)
        
        if cmds.objExists(main_ctrl_attach_obj):
            cmds.parentConstraint(main_ctrl_attach_obj, main_ctrl.ofst_name, mo=True)
            
        main_vis_attrs = ['modelVis', 'jointsVis']
        main_disp_attrs = ['modelDisp', 'jointsDisp']
        main_obj_list = [self.geo_grp, self.jnt_grp]
        main_obj_list_df_list = [1, 0] #df = default value
        
        #add rig visibility connections
        for at, obj, dfVal in zip(main_vis_attrs, main_obj_list, main_obj_list_df_list):
            
            cmds.addAttr(main_ctrl.ctrl_name, ln=at, at='enum', enumName='off:on', k=True, dv=dfVal)
            cmds.setAttr(main_ctrl.ctrl_name+'.'+at, cb=True)
            cmds.connectAttr(main_ctrl.ctrl_name+'.'+at, obj+'.v')

        #add rig display type connections
        for at, obj in zip(main_disp_attrs, main_obj_list):
            
            cmds.addAttr(main_ctrl.ctrl_name, ln=at, at='enum', enumName='normal:template:reference', k=True, dv=2)
            cmds.setAttr(main_ctrl.ctrl_name+'.'+at, cb=True)
            cmds.setAttr(obj + '.ove', True)
            cmds.connectAttr(main_ctrl.ctrl_name+'.'+at, obj+'.ovdt')
        
    def _adjust_main_ctrl_shape(self, ctrl, scale):
        #adjust shape of main control
        ctrl_shapes = cmds.listRelatives(ctrl.ctrl_name, s=True, type='nurbsCurve')
        cls_handle = cmds.cluster(ctrl_shapes)[1]
        cmds.setAttr(cls_handle+'.ry', 90)
        cmds.delete(ctrl_shapes, ch=True)
        
        cmds.move(15*scale, ctrl.ofst_name, moveY=True, relative=True)
        
    
    def __flatten_global_ctrl_shape(self, ctrl_obj):
        ctrl_shapes = cmds.listRelatives(ctrl_obj, s=True, type='nurbsCurve')
        cls_handle = cmds.cluster(ctrl_shapes)[1]
        cmds.setAttr(cls_handle+'.rz', 90)
        cmds.delete(ctrl_shapes, ch=True)
        

class Module():
    
    """
    class for creating module rig structure
    """
    
    def __init__(
            self,
            prefix='new',
            base_obj=None 
            ):
        
        """
        @param prefix: str, prefix to the name of new modules
        @param base_obj: instance of base.module.Base class
        @return: None
        """
        
        self.top_grp = cmds.group(name=prefix+'_module_grp', empty=True)
        
        self.ctrl_grp = cmds.group(name=prefix+'_ctrl_grp', empty=True, parent=self.top_grp)
        self.jnt_grp = cmds.group(name=prefix+'_jnt_grp', empty=True, parent=self.top_grp)
        
        self.misc_grp = cmds.group(name=prefix+'_misc_grp', empty=True, parent=self.top_grp) #for ik handles and such
        self.parts_grp = cmds.group(name=prefix+'_parts_grp', empty=True, parent=self.top_grp) #fot things that aren't going to have transformations
        cmds.setAttr(self.parts_grp+'.it', False, l=True) #.it = inheritTransforms
        
        #parent module
        if base_obj:
            cmds.parent(self.top_grp, base_obj.module_grp)
            
            