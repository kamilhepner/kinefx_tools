import hou 
import nodegraphalign


def _get_names(node):
    """ Get values of name attribute

    Args:
        node (hou.Node): <create zero attr> node 

    Returns: 
        names [(str),...] 
    
    """
    
    names = []
    geo   = node.geometry()

    for p in geo.points():
        names.append(p.attribValue('name'))
    
    return names


def _is_control_defined(node, point_id):
    """ Checks if control should be created on specified point id
    
    Args:
        name (str):     Name of a control
        point_id (int): Skeleton point number
    
    Returns:
        (bool)
    
    """
    
    node_pt    = node.geometry().iterPoints()[point_id]
    shape_name = node_pt.stringAttribValue('shape_name')

    return True if shape_name != '' else False


def _align_node(nodes):
    """ Align nodes in network editor 
    
    Args:
        nodes ([hou.Node,...]): Nodes to align
    """

    network_editor = None
    for pane_tab in hou.ui.paneTabs():
        if isinstance(pane_tab, hou.NetworkEditor):
            network_editor = pane_tab
            break
    
    if network_editor != None:
        nodegraphalign.alignItems(network_editor, nodes, nodes[0], None, "down")

        # Add to network box
        box = nodes[0].parentNetworkBox()
        if box != None:
            for n in nodes[1:]:
                box.addNode(n)
    else:
        print("No network editor")



def _create_obj_control(name, point_id, zero_wrangle, rig_pose, network=None):
    """ Create OBJ level control
    
    Args:
        name (str):              Name of a control
        point_id (int):          Skeleton point number
        zero_wrangle (hou.Node): <create zero attr> node
        rig_pose (hou.Node):     Rig pose node
        network (hou.Node):      Network where controls should be created. Need to OBJ type. Default: OBJ level 

    Returns: 
        (zero_node, control, parent): (hou.Node, hou.Node, hou.Node)
    """
    
    # Use /OBJ network as default
    if network == None:
        network = hou.node('/obj')

    zero_wrangle_pt = zero_wrangle.geometry().iterPoints()[point_id]

    # ---------
    # CONTROL

    # If exist delete it
    control = hou.node( '{}/{}'.format(network.path(), name))
    if control != None:
        control.destroy()
    
    shape_name = zero_wrangle_pt.stringAttribValue('shape_name')
    scale      = zero_wrangle_pt.attribValue('control_scale')
    offset     = zero_wrangle_pt.attribValue('control_offset')
    color      = zero_wrangle_pt.attribValue('control_color')
    xray       = zero_wrangle_pt.intAttribValue('control_xray')
    world_space= zero_wrangle_pt.intAttribValue('world_space')
    print("shape_name: {}  world_space: {}".format(shape_name, world_space))

    control = network.createNode('rig_control::1.0', node_name=name )
    control.parm('shape_name').set(shape_name)
    control.parmTuple('size').set(scale)
    control.parm('use_dcolor').set(1)
    control.parmTuple('dcolor').set(color)

    control.parmTuple('t2').set(offset)

    if xray:
        control.setGenericFlag(hou.nodeFlag.XRay, True)

    control.moveToGoodPosition()


    # ---------
    # ZERO NODE
    
    # If exist delete it
    zero_node = hou.node( '{}/{}_zero'.format(network.path(), name))
    if zero_node != None:
        zero_node.destroy()

    # Create new one
    zero_node = network.createNode('rig_zero::1.0', node_name='{}_zero'.format(name) )

    # Parent control
    control.setInput(0, zero_node)
    
    zero_node.parm('tdisplay').set(1)
    zero_node.parm('display').set(0)
    zero_node.parm('data_input').set(zero_wrangle.path())

    # If joint have a parent, zero-out offset of zero group

    zero_node.parm('tx').setExpression("detail(chs(\"data_input\"),opname(\".\")+\"_tr\",0)")
    zero_node.parm('ty').setExpression("detail(chs(\"data_input\"),opname(\".\")+\"_tr\",1)")
    zero_node.parm('tz').setExpression("detail(chs(\"data_input\"),opname(\".\")+\"_tr\",2)")

    zero_node.parm('rx').setExpression("detail(chs(\"data_input\"),opname(\".\")+\"_rot\",0)")
    zero_node.parm('ry').setExpression("detail(chs(\"data_input\"),opname(\".\")+\"_rot\",1)")
    zero_node.parm('rz').setExpression("detail(chs(\"data_input\"),opname(\".\")+\"_rot\",2)")

    # for a in 'xyz':
    #     zero_node.parm( 'p{}'.format(a)).set(zero_node.parm('t{}'.format(a)).eval() * -1)
    #     zero_node.parm('pr{}'.format(a)).set(zero_node.parm('r{}'.format(a)).eval() * -1)

    zero_node.moveToGoodPosition()


    # ---------
    # RIG POSE

    entries = rig_pose.parm('transformations').evalAsInt()
    rig_pose.parm('transformations').set(entries+1)

    rig_pose.parm('group{}'.format(entries)).set('@name={}'.format(name))
    rig_pose.parm('t{}x'.format(entries)).set(control.parm('tx'))
    rig_pose.parm('t{}y'.format(entries)).set(control.parm('ty'))
    rig_pose.parm('t{}z'.format(entries)).set(control.parm('tz'))

    rig_pose.parm('r{}x'.format(entries)).set(control.parm('rx'))
    rig_pose.parm('r{}y'.format(entries)).set(control.parm('ry'))
    rig_pose.parm('r{}z'.format(entries)).set(control.parm('rz'))

    rig_pose.parm('worldspace').set(world_space)
    

    # Hierarchy
    parent_pt = zero_wrangle.geometry().iterPoints()[point_id]._getPointParent()
    if parent_pt == None:
        parent = None
    else:
        parent = parent_pt.attribValue('name')



    return (zero_node, control, parent)


def _have_control_attributes(node):
    """
    Validates if node have all attributes needed for control creation
    """

    if not isinstance(node, hou.SopNode):
        print('type: {}'.format(type(node)))
        return False

    geo = node.geometry()

    attrs = [
        'shape_name', 
        'control_scale', 
        'control_color', 
        'control_offset', 
        'control_xray', 
        'world_space'
        ]

    for attr in attrs:
        if geo.findPointAttrib(attr) == None:
            raise IOError('Attribute missing: {}'.format(attr))
            return False
    
    return True



def run():
    nodes = hou.selectedNodes() 
    controls_network = hou.node('/obj')

    # Check node types
    for node in nodes:
        if not _have_control_attributes(node):
            raise IOError('Please select nodes with controls attributes')
        

        connections = node.outputConnections()
        rig_network = node.parent()
        
        # Create zeros node
        zero_wrangle = rig_network.createNode('create_zero_attr::1.0', node_name='{}_zeros'.format(node.name()))
        zero_wrangle.setInput(0, node)
        zero_wrangle.moveToGoodPosition()

        # Rig pose
        rig_pose = rig_network.createNode('kinefx::rigpose', node_name='{}_rpose'.format(node.name()))
        rig_pose.setInput(0, zero_wrangle)
        rig_pose.moveToGoodPosition()

        # Align
        _align_node([node,zero_wrangle,rig_pose])

        # Connect output
        for connection in connections:
            i_index = connection.inputIndex()
            o_node  = connection.outputNode()

            o_node.setInput(i_index, rig_pose)

        # Get names
        ctrls_names = _get_names(zero_wrangle)

        # Get world space attribute which is only on custom Attach control geometry HDA
        # world_space = node.parm('world_space')
        # if world_space == None:
        #     world_space = 0
        # else:
        #     world_space = world_space.eval()
        #
        # NOTE: Now it's passed as point attribute

        to_parent = []

        # Create controls
        for point_id, ctrl_name in enumerate(ctrls_names):

            # Create control only on 
            if  not _is_control_defined(zero_wrangle, point_id):
                print('skipping {0}'.format(ctrl_name))
                continue

            zero_node, control, parent_name =_create_obj_control(
                ctrl_name, 
                point_id, 
                zero_wrangle, 
                rig_pose, 
                controls_network
                )
            
            to_parent.append((zero_node, control, parent_name))
        
        # Create hierarchy 
        for zero_node, control, parent_name in to_parent:

            print('Parenting \'{0}\' to \'{1}\''.format(zero_node.name(), parent_name))
            
            if parent_name == None:
                continue
            
            parent = controls_network.node(parent_name)
            if parent == None:
                print('\tParent {0} doesn\'t exists'.format(parent_name))
                continue

            zero_node.setInput(0, parent)

            







#import sys ; sys.path.append('T:\\devcode\\python\\houdini') ; from kinefx_extra import create_obj_ctrls ; from importlib import reload
#import kinefx_extra
#from kinefx_extra import create_obj_ctrls
#  from importlib import reload