"""
ribbon utils @utils
has different service functions required while working with ribbons
"""

import maya.cmds as cmds
from _ast import Num
from . import name 

def create_cv_curve(curve, pos_ref_list, degree=3):
    """
    create CV curve with CVs at positions of the objects in pos_ref_list
    
    @param curve: str, name of the CV curve to be created
    @param pos_ref_list: list(str), list of object names to extract positions from
    @param degree: the degree of the new curve
    @return None
    """
    
    obj_pos_list = []
    for obj in pos_ref_list:
        obj_pos_list.append(cmds.xform(obj, q=True, ws=True, t=True))
    
    cmds.curve(n=curve, point=[obj_pos_list[0]], d=degree)

    for i in range(1, len(pos_ref_list)):
        cmds.curve(curve, append=True, point=[obj_pos_list[i]], ws=True)
   
        
def create_ep_curve(curve, pos_ref_list, degree=3):
    """
    create EP curve with EditPoints at positions of the objects in pos_ref_list
    
    @param curve: str, name of the EP curve to be created
    @param pos_ref_list: list(str), list of object names to extract positions from
    @param degree: the degree of the new curve
    @return None
    """
    obj_pos_list = []
    for obj in pos_ref_list:
        obj_pos_list.append(cmds.xform(obj, q=True, ws=True, t=True))
    
    cmds.curve(n=curve, ep=obj_pos_list, d=degree)
        
def get_curve_num_cvs(curve):
    """
    calculate and return number of CVs in a curve
    
    @param curve: str, name of the curve to be created
    @return int: number of CVs in the curve
    """
    curve_degree = cmds.getAttr(curve + '.degree')
    curve_spans = cmds.getAttr(curve + '.spans')
    
    return curve_degree + curve_spans
    
    
        
def loft_using_curve(curve, width, axis, prefix):
    """
    duplicate curve and loft
    
    @param curve: str, given CV curve name to process
    @param width: double, width of the CV curve
    @param prefix: str, name of body part for which the ribbon is being constructed
    @return: str: name of the created ribbon nurbs surface object
    """
    curve_02 = cmds.duplicate(curve)[0]

    curve_cv_list = []    
    curve_02_cv_list = []
    for i in range(get_curve_num_cvs(curve)):
        curve_cv_list.append(curve+'.cv[%d]' % i)
        curve_02_cv_list.append(curve_02+'.cv[%d]' % i)
    print curve_cv_list
    print curve_02_cv_list
        
    if axis=='x':
        cmds.move( width/2,0,0, curve_cv_list, relative=True, cs=True, ls=True, wd=True )
        cmds.move( width/-2,0,0, curve_02_cv_list, relative=True, cs=True, ls=True, wd=True )
    elif axis=='y':
        cmds.move( 0,width/2,0, curve_cv_list, relative=True, cs=True, ls=True, wd=True )
        cmds.move( 0,width/-2,0, curve_02_cv_list, relative=True, cs=True, ls=True, wd=True )
    elif axis=='z':
        cmds.move( 0,0,width/2, curve_cv_list, relative=True, cs=True, ls=True, wd=True )
        cmds.move( 0,0,width/-2, curve_02_cv_list, relative=True, cs=True, ls=True, wd=True )
    else:
        print 'Invalid entry for "axis" parameter.'
        return None
    
    ribbon_sfc = prefix+'_ribbon_sfc'
    cmds.loft(curve, curve_02, name=ribbon_sfc, 
              ch=True, u=True, ar=True, po=0, d=1, ss=1)
    cmds.delete(curve, curve_02)
    '''NEED A SEPARATE FUNCTION FOR REBUILDING SURFACES'''
#    cmds.rebuildSurface(ribbon_sfc, su=0, sv=3, du=1, dv=3, ch=True)
#    cmds.reverseSurface(ribbon_sfc, ch=True, rpo=True, d=0 )
    
    return ribbon_sfc


def add_follicles(sfc_shape, num_foll=1, on_edges=True, create_joints=False):
    """
    create as many equidistant follicles along the length of a surface
    
    @param sfc_shape: str, name of the surface we want follicles attached to
    @param num_foll: int, number of follicles created on the surface
    @return: list(str): list of follicles
    """
    foll_list = []
    jnt_list = []
    for i in range(0, num_foll):
        if on_edges:
            foll = create_follicle(sfc_shape, 0.5, i/(num_foll-1.00))
        else:
            foll = create_follicle(sfc_shape, 0.5, ((1.0/num_foll)*i)+(0.5/num_foll))
        foll_list.append(foll)
        
        if create_joints:
            temp_jnt = '_'.join((name.remove_suffix(sfc_shape),'jnt',str(i+1).zfill(2)))
            cmds.select(d=True)
            cmds.joint(name=temp_jnt)
            cmds.delete(cmds.parentConstraint(foll, temp_jnt))
            jnt_list.append(temp_jnt)
            cmds.parent(temp_jnt, foll)
            cmds.makeIdentity(temp_jnt, t=0, r=1, s=0, apply=True)
            
    #foll_grp = sfc_shape+'_follicles_grp'
    #cmds.group(name=foll_grp, world=True, em=True)
    #cmds.parent(foll_list, foll_grp)
    
    if create_joints:
        return [foll_list, jnt_list]
    return foll_list


def create_follicle(sfc_shape, u_pos=0.0, v_pos=0.0):
    """
    create a single follicle at given u&v on a surface and make necessary attribute connections
    
    @param sfc_shape: str, name of the surface we want follicles attached to
    @param u_pos: double, x position of follicle relative to surface
    @param v_pos: double, y position of follicle relative to surface
    @return: str, follicle transform node
    """
    # manually place and connect a follicle onto a nurbs surface.
    if cmds.objectType(sfc_shape) == 'transform':
        sfc_shape = cmds.listRelatives(sfc_shape, shapes=True)[0]
    elif cmds.objectType(sfc_shape) == 'nurbsSurface':
        pass
    else:
        print 'Warning: Input must be a nurbs surface.'
        return False

    foll_p_name = '_'.join((sfc_shape,'follicle','#'.zfill(2)))

    foll = cmds.createNode('follicle', name=foll_p_name)
    foll_transform = cmds.listRelatives(foll, parent=True)[0]
    cmds.connectAttr(sfc_shape+'.local', foll+'.inputSurface')
    
    cmds.connectAttr(sfc_shape+'.worldMatrix[0]', foll+'.inputWorldMatrix')
    cmds.connectAttr(foll+'.outRotate', foll_transform+'.rotate')
    cmds.connectAttr(foll+'.outTranslate', foll_transform+'.translate')
    cmds.setAttr(foll + ".parameterU", u_pos)
    cmds.setAttr(foll + ".parameterV", v_pos)
    
    cmds.setAttr( foll_transform+'.translate', lock=True )
    cmds.setAttr( foll_transform+'.rotate', lock=True )
    
    return foll_transform
    
    
def create_twist_deformer(sfc, prefix=''):
    """
    create a single follicle at given u&v on a surface and make necessary attribute connections
    
    @param sfc: str, name of the surface we want apply bend deformer to
    @param prefix: str, name of body part for which the ribbon is being constructed
    @return: list(str), list of length 2 with names of deformer twist obj and twist-handle obj
    """
    
    twist_handle = cmds.nonLinear(sfc, type='twist')
    cmds.rename(twist_handle[0], prefix+'_twist')
    cmds.rename(twist_handle[1], prefix+'_twist_handle')
    twist_handle[0] = prefix+'_twist'
    twist_handle[1] = prefix+'_twist_handle'
    
    return twist_handle

















    