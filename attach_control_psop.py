# Updated code for Attach Control Geometry SOP

from kinefx import utils

node = hou.pwd()
geo = node.geometry()
ctrl_geo = node.inputGeometry(1)

controls = {}
for p in ctrl_geo.prims():
    g = p.getEmbeddedGeometry()
    controls[p.attribValue("name")] = g
    
ctrl_parm = node.parm("../controls")
parms = ctrl_parm.multiParmInstances()
#print(parms)
multiparm_len = len(ctrl_parm.parmTemplate().parmTemplates())
grp_name = node.evalParm("../controlgroup")
ctrl_grp = geo.findPrimGroup(grp_name)
if grp_name and not ctrl_grp:
    ctrl_grp = geo.createPrimGroup(grp_name)

lit = node.evalParm("../uselighting") > 0

if not geo.findGlobalAttrib("gl_lit"):
    geo.addAttrib(hou.attribType.Global, "gl_lit", 0, create_local_variable=False)
geo.setGlobalAttribValue("gl_lit", lit)

world_space = node.evalParm("../world_space")


# Global settings
geo.addAttrib(hou.attribType.Global, "mirror_scale", [1.0,1.0,1.0])

scale_enable = node.parm("../scale_enable").eval()
mirror_scale = [1.0, 1.0, 1.0]
if(scale_enable):
    mirror_scale = node.parmTuple("../mirror_scale").eval()
    # Global settings
    geo.setGlobalAttribValue("mirror_scale", mirror_scale)


# Per control attributes
geo.addAttrib(hou.attribType.Point, "shape_name", "")
geo.addAttrib(hou.attribType.Point, "control_scale", [1.0,1.0,1.0])
geo.addAttrib(hou.attribType.Point, "control_offset", [0.0,0.0,0.0])
geo.addAttrib(hou.attribType.Point, "control_color", [0.5,0.5,0.5])
geo.addAttrib(hou.attribType.Point, "control_folder", "")
geo.addAttrib(hou.attribType.Point, "control_xray", 0)
geo.addAttrib(hou.attribType.Point, "world_space", 0)
geo.addAttrib(hou.attribType.Point, "channel_lock", [0, 0, 0])
        
visited = set()
    
for idx in reversed(range(ctrl_parm.eval())):
    group     = parms[(idx * multiparm_len) + (idx*6)]
    ctrl_name = parms[(idx * multiparm_len) + (idx*6) + 1].eval()
    scale     = parms[(idx * multiparm_len) + (idx*6) + 2].tuple().eval()
    offset    = parms[(idx * multiparm_len) + (idx*6) + 5].tuple().eval()
    color     = parms[(idx * multiparm_len) + (idx*6) + 8].tuple().eval()
    folder    = parms[(idx * multiparm_len) + (idx*6) + 11].tuple().eval()
    xray      = parms[(idx * multiparm_len) + (idx*6) + 12].eval()
    t_lock    = parms[(idx * multiparm_len) + (idx*6) + 13].eval()
    r_lock    = parms[(idx * multiparm_len) + (idx*6) + 14].eval()
    s_lock    = parms[(idx * multiparm_len) + (idx*6) + 15].eval()
    
    # Create control transformation matrix 
    trans          = hou.hmath.buildTranslate(offset)
    control_matrix = hou.hmath.buildScale(scale)
    control_matrix *= trans 
    
    grp_sel = hou.Selection(geo, hou.geometryType.Points, group.eval())
    grp_pts = grp_sel.points(geo)
    for pt in grp_pts:
        if pt in visited:
            continue
        visited.add(pt)
        if ctrl_name in controls:

            g_ctrl = hou.Geometry(controls[ctrl_name])
            
            # Packed control color 
            if not g_ctrl.findPrimAttrib("Cd"):
                g_ctrl.addAttrib(hou.attribType.Prim, "Cd", color)
            
            for prim in g_ctrl.prims():
                prim.setAttribValue("Cd", color)
            
            # Transform control 
            g_ctrl.transform(control_matrix)
            g_ctrl.freeze(True, True)

            ctrl_prim = utils.attachControlGeo(pt, g_ctrl)
            if ctrl_grp:
                ctrl_grp.add(ctrl_prim)
            
            # Add control name as point attribute 
            pt.setAttribValue("shape_name",     ctrl_name)
            pt.setAttribValue("control_scale",  scale)
            pt.setAttribValue("control_offset", offset)
            pt.setAttribValue("control_color",  color)
            pt.setAttribValue("control_folder", folder)
            pt.setAttribValue("control_xray",   xray)
            pt.setAttribValue("world_space",    world_space)
            pt.setAttribValue("channel_lock",   [t_lock, r_lock, s_lock])

    
    