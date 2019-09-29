"""
ribbon utils @utils
has different service functions required while working with ribbons
"""

import maya.cmds as cmds

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
    
    
        
def loft_using_curve(curve, width, prefix):
    """
    duplicate curve and loft
    
    @param curve: str, given CV curve name to process
    @param width: double, width of the CV curve
    @param prefix: str, name of body part for which the ribbon is being constructed
    @return: str: name of the created ribbon nurbs surface object
    """
    curve_pos = cmds.xform(curve, q=True, ws=True, t=True)
    curve_02 = cmds.duplicate(curve)
    
    cmds.xform(curve, ws=True, t=(curve_pos[0]+(width/2),0,0))
    cmds.xform(curve_02, ws=True, t=(curve_pos[0]+(width/-2),0,0))
    
    ribbon_sfc = prefix+'_ribbon_sfc'
    cmds.loft(curve, curve_02, name=ribbon_sfc, 
              ch=True, u=True, ar=True, po=0, d=1, ss=1)
    cmds.delete(curve, curve_02)
    cmds.rebuildSurface(ribbon_sfc, su=0, sv=3, du=1, dv=3, ch=True)
    cmds.reverseSurface(ribbon_sfc, ch=True, rpo=True, d=0 )
    
    return ribbon_sfc


def add_follicles(sfc_shape, num_foll=1):
    """
    create as many equidistant follicles along the length of a surface
    
    @param sfc_shape: str, name of the surface we want follicles attached to
    @param num_foll: int, number of follicles created on the surface
    @return: list(str): list of follicles
    """
    foll_list = []
    for i in range(0, num_foll):
        foll = create_follicle('spine_ribbon_sfc', 0.5, i/(num_foll-1.00))
        foll_list.append(foll)
        
    #foll_grp = sfc_shape+'_follicles_grp'
    #cmds.group(name=foll_grp, world=True, em=True)
    #cmds.parent(foll_list, foll_grp)
    
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
    
    
    

    