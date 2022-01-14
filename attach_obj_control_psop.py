from kinefx import utils

def attachControlGeo(pt, ctrlgeo, role="control"):
    """
    Attach a control geometry to a point.

    :param pt: point to attach the control geometry to
    :type pt: hou.Point
    :param ctrlgeo: control geometry to attach
    :type ctrlgeo: hou.Geometry or hou.PackedGeometry
    :param role: defines the function of the geometry to be attached: control: the given geometry is being used as control shape
    for easy selections of the given joint. Capture: It is being used as object to modify the capture values calculated by the
    byharmonic joint capture node.
    :return: attached control primitive
    :rtype: hou.PackedGeometry
    """
    geo = pt.geometry()

    geo_dict = dict(role=role)
    if not geo.findPrimAttrib("jointgeo"):
        geo.addAttrib(hou.attribType.Prim, "jointgeo", geo_dict, create_local_variable=False)
    for pr in pt.prims():
        if pr.type() == hou.primType.PackedGeometry:
            current_geo_dict = pr.dictAttribValue('jointgeo')
            if "role" in current_geo_dict and current_geo_dict["role"] == role:
                pr.setEmbeddedGeometry(ctrlgeo)
                pr.setIntrinsicValue("pointinstancetransform", 1)
                return pr

    prim = geo.createPackedGeometry(ctrlgeo, pt)
    prim.setIntrinsicValue("pointinstancetransform", 1)

    return prim

node = hou.pwd()
geo = node.geometry()
ctrl_geo = node.inputGeometry(1)

role_key   = 'role'
name_key   = 'name'
folder_key = 'folder'
xray_key   = 'xray'
t_lock_key = 't_lock'
r_lock_key = 'r_lock'
s_lock_key = 's_lock'
metadata_template = {
    role_key: "" ,
    t_lock_key : 0 ,
    r_lock_key : 0 ,
    s_lock_key : 0  
}
shapesource_attr = '__shapesource'

controls = {}
for p in ctrl_geo.prims():
    g = p.getEmbeddedGeometry()
    g.freeze(True, True)
    controls[p.attribValue("name")] = g

ctrl_parm = node.parm("../shapes")
role = node.parm('../role')
parms = ctrl_parm.multiParmInstances()
multiparm_len = len(ctrl_parm.parmTemplate().parmTemplates())
grp_name = node.evalParm("../controlgroup")
ctrl_grp = geo.findPrimGroup(grp_name)
if grp_name and not ctrl_grp:
    ctrl_grp = geo.createPrimGroup(grp_name)

lit = node.evalParm("../uselighting") > 0

if not geo.findGlobalAttrib("gl_lit"):
    geo.addAttrib(hou.attribType.Global, "gl_lit", 0, create_local_variable=False)
geo.setGlobalAttribValue("gl_lit", lit)

visited = set()


# Global settings
geo.addAttrib(hou.attribType.Global, "mirror_scale", [1.0,1.0,1.0])

scale_enable = node.parm("../scale_enable").eval()
mirror_scale = [1.0, 1.0, 1.0]
if(scale_enable):
    mirror_scale = node.parmTuple("../mirror_scale").eval()
    # Global settings
    geo.setGlobalAttribValue("mirror_scale", mirror_scale)


# reset assigned names per point for the packed geo var

for idx in reversed(range(ctrl_parm.eval())):
    group = parms[(idx * multiparm_len)]

    # Get control settings
    ctrl_name = parms[(idx * multiparm_len) + 1].eval()
    folder    = parms[(idx * multiparm_len) + 3].evalAsString()
    xray      = parms[(idx * multiparm_len) + 4].eval()
    t_lock    = parms[(idx * multiparm_len) + 5].eval()
    r_lock    = parms[(idx * multiparm_len) + 6].eval()
    s_lock    = parms[(idx * multiparm_len) + 7].eval()

    grp_sel = hou.Selection(geo, hou.geometryType.Points, group.eval())
    grp_pts = grp_sel.points(geo)
    for pt in grp_pts:
        if pt in visited:
            continue
        visited.add(pt)
        if ctrl_name in controls:
            ctrl_prim = attachControlGeo(pt, controls[ctrl_name])
            if ctrl_grp:
                ctrl_grp.add(ctrl_prim)

            # add the control name to the dictionary
            packed_geo_metadata = metadata_template
            if geo.findPrimAttrib("jointgeo"):
                for current_prim in pt.prims():
                    # in case of multiple control geos use the metadata of the first found prim
                    current_metadata = current_prim.dictAttribValue('jointgeo')
                    if role_key in current_metadata and current_metadata[role_key] == role.eval():
                        packed_geo_metadata = current_prim[0].dictAttribValue('jointgeo')
                        break
            
            # Set dictionary values
            packed_geo_metadata[role_key] = role.evalAsString()
            packed_geo_metadata[folder_key] = folder
            packed_geo_metadata[xray_key]   = xray
            packed_geo_metadata[t_lock_key] = t_lock
            packed_geo_metadata[r_lock_key] = r_lock
            packed_geo_metadata[s_lock_key] = s_lock
            
            if not geo.findPrimAttrib("name"):
                geo.addAttrib(hou.attribType.Prim, "name", ctrl_name, create_local_variable=False)
            ctrl_prim.setAttribValue("name", ctrl_name)
            
            if not geo.findPrimAttrib("jointgeo"):
                geo.addAttrib(hou.attribType.Prim, "jointgeo", metadata_template, create_local_variable=False)
            ctrl_prim.setAttribValue('jointgeo', packed_geo_metadata)
            if not geo.findPointAttrib(shapesource_attr):
                geo.addAttrib(hou.attribType.Point, shapesource_attr, "", create_local_variable=False)
            pt.setAttribValue(shapesource_attr, "library")