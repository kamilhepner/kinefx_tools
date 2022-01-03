import hou 
import nodegraphalign
import local_config as conf

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




def _create_zero_node(control, zero_wrangle):
    """ Creates  zero node for a control on object level
        
    Args:
        control (hou.Node): Object level control created by script
        zero_wrangle (hou.Node): <create zero attr> node
    
    Returns:
        zero_node (hou.Node) 
    """
    
    # NOTE: Takes the name and network from the control
    # instead of passing it explicitly 
    # TODO: Add validation, to check if control exists
    name    = control.name()
    network = control.parent()

    # If exist delete it
    zero_node = hou.node( '{}/{}_zero'.format(network.path(), name))
    if zero_node != None:
        zero_node.destroy()

    # Create new one
    zero_node = network.createNode(
        conf.hda_def['rig_zero'], 
        node_name='{}_zero'.format(name) )

    # Parent control
    control.setInput(0, zero_node)
    
    zero_node.parm('tdisplay').set(1)
    zero_node.parm('display').set(0)
    zero_node.parm('data_input').set(zero_wrangle.path())

    # If joint have a parent, zero-out offset of zero group
    zero_node.parm('tx').setExpression("if(ch(\"world_space\"),ch(\"world_tx\"),ch(\"local_tx\"))")
    zero_node.parm('ty').setExpression("if(ch(\"world_space\"),ch(\"world_ty\"),ch(\"local_ty\"))")
    zero_node.parm('tz').setExpression("if(ch(\"world_space\"),ch(\"world_tz\"),ch(\"local_tz\"))")

    zero_node.parm('rx').setExpression("if(ch(\"world_space\"),ch(\"world_rx\"),ch(\"local_rx\"))")
    zero_node.parm('ry').setExpression("if(ch(\"world_space\"),ch(\"world_ry\"),ch(\"local_ry\"))")
    zero_node.parm('rz').setExpression("if(ch(\"world_space\"),ch(\"world_rz\"),ch(\"local_rz\"))")

    
    # Read local transformation
    zero_node.parm('local_tx').setExpression("detail(chs(\"data_input\"),opname(\".\")+\"_tr\",0)")
    zero_node.parm('local_ty').setExpression("detail(chs(\"data_input\"),opname(\".\")+\"_tr\",1)")
    zero_node.parm('local_tz').setExpression("detail(chs(\"data_input\"),opname(\".\")+\"_tr\",2)")

    zero_node.parm('local_rx').setExpression("detail(chs(\"data_input\"),opname(\".\")+\"_rot\",0)")
    zero_node.parm('local_ry').setExpression("detail(chs(\"data_input\"),opname(\".\")+\"_rot\",1)")
    zero_node.parm('local_rz').setExpression("detail(chs(\"data_input\"),opname(\".\")+\"_rot\",2)")

    # Read world transformation
    zero_node.parm('world_tx').setExpression("detail(chs(\"data_input\"),opname(\".\")+\"_world_tr\",0)")
    zero_node.parm('world_ty').setExpression("detail(chs(\"data_input\"),opname(\".\")+\"_world_tr\",1)")
    zero_node.parm('world_tz').setExpression("detail(chs(\"data_input\"),opname(\".\")+\"_world_tr\",2)")

    zero_node.parm('world_rx').setExpression("detail(chs(\"data_input\"),opname(\".\")+\"_world_rot\",0)")
    zero_node.parm('world_ry').setExpression("detail(chs(\"data_input\"),opname(\".\")+\"_world_rot\",1)")
    zero_node.parm('world_rz').setExpression("detail(chs(\"data_input\"),opname(\".\")+\"_world_rot\",2)")

    zero_node.moveToGoodPosition()

    return zero_node



def _drive_rigpose_with_control(rig_pose, control):
    """ This function will connect object level control to the rig pose

    Args:
        rig_pose (hou.Node):  kinefx::rigpose node
        control (hou.Node): Object level control created by script
    """
    name = control.name()

    entries = rig_pose.parm('transformations').evalAsInt()
    rig_pose.parm('transformations').set(entries+1)

    rig_pose.parm('group{}'.format(entries)).set('@name={}'.format(name))

    for att in 'trs':
        for axis in 'xyz':
            r_parm = '{0}{1}{2}'.format(att, entries, axis)
            c_parm = '{0}{1}'.format(att, axis)
            rig_pose.parm(r_parm).set(
                control.parm(c_parm)
                )
            
            if control.parm(c_parm).isLocked():
                rig_pose.parm(r_parm).lock(True)


    # rig_pose.parm('t{}x'.format(entries)).set(control.parm('tx'))
    # rig_pose.parm('t{}y'.format(entries)).set(control.parm('ty'))
    # rig_pose.parm('t{}z'.format(entries)).set(control.parm('tz'))

    # rig_pose.parm('r{}x'.format(entries)).set(control.parm('rx'))
    # rig_pose.parm('r{}y'.format(entries)).set(control.parm('ry'))
    # rig_pose.parm('r{}z'.format(entries)).set(control.parm('rz'))

    # rig_pose.parm('s{}x'.format(entries)).set(control.parm('sx'))
    # rig_pose.parm('s{}y'.format(entries)).set(control.parm('sy'))
    # rig_pose.parm('s{}z'.format(entries)).set(control.parm('sz'))



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
    
    # Query point attributes created by attach control geometry node (custom)
    shape_name   = zero_wrangle_pt.stringAttribValue('shape_name')
    scale        = zero_wrangle_pt.attribValue('control_scale')
    offset       = zero_wrangle_pt.attribValue('control_offset')
    color        = zero_wrangle_pt.attribValue('control_color')
    folder       = zero_wrangle_pt.stringAttribValue('control_folder')
    xray         = zero_wrangle_pt.intAttribValue('control_xray')
    world_space  = zero_wrangle_pt.intAttribValue('world_space')
    channel_lock = zero_wrangle_pt.attribValue('channel_lock')
    print("shape_name: {}  world_space: {}".format(shape_name, world_space))

    print("rig_control: {}  network: {}".format(conf.hda_def['rig_control'], network))
    control = network.createNode(conf.hda_def['rig_control'], node_name=name )

    # Set control parameters
    control.parm('shape_name').set(shape_name)
    control.parm('control_folder').set(folder)
    control.parmTuple('size').set(scale)
    control.parm('use_dcolor').set(1)
    control.parmTuple('dcolor').set(color)
    control.parmTuple('t2').set(offset)

    if xray:
        control.setGenericFlag(hou.nodeFlag.XRay, True)

    control.moveToGoodPosition()

    # Lock control channels
    for p, axis in list(zip('trs',channel_lock)):
        if axis & 1 :
            control.parm('{}x'.format(p)).lock(True)
        if axis & 2 :
            control.parm('{}y'.format(p)).lock(True)
        if axis & 4 :
            control.parm('{}z'.format(p)).lock(True)

    # Create zero node
    zero_node = _create_zero_node(control, zero_wrangle)

    # Connect rig pose to the control
    _drive_rigpose_with_control(rig_pose, control)

    # Attributes
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
        'control_folder',
        'control_scale', 
        'control_color', 
        'control_offset', 
        'control_xray', 
        'channel_lock',
        'world_space',
        ]

    for attr in attrs:
        if geo.findPointAttrib(attr) == None:
            raise IOError('Attribute missing: {}'.format(attr))
            return False
    
    return True



def _add_to_group(network, node, group):
    """
    Add specified node to the group 
    
    Args:
        network (hou.Node):  Network node on which we want to add the group
        node (hou.Node):     Node to add
        group (str):         Group name
    
    """

    # Create group if it doesn\'t exists
    ctrl_group = network.nodeGroup(group)
    if ctrl_group == None:
        ctrl_group = network.addNodeGroup(group)
    
    ctrl_group.addNode(node)



def promote_selected_controls(hda=None):
    """
    Wrapper function to promote selected controls by
    promote_control() function
    """
    nodes = hou.selectedNodes()

    if len(nodes) == 0:
        return None
    
    if hda == None:
        #hda = get_object_level_network(nodes[0])
        hda = nodes[0].parent()
    
    for node in nodes:
        promote_control(node, hda)



def promote_control(control, hda=None):
    """ Promotes control parameters to top rig HDA

    Args:
        control (hou.Node):  Network node on which we want to add the group
    
    """

    if hda == None:
        # Assuming that parent of control is the top of hda
        #hda = get_object_level_network(control)
        hda = control.parent()

    # Get folder name
    folder_parm = control.parm('control_folder')
    if folder_parm == None:
        raise KeyError('Can\'t promote {} control: Can\'t find \'control_folder\' parameter'.format(control.name()))
    folder_label = folder_parm.eval()
    folder_name = folder_label.replace(' ', '_').lower()

    hda_def = hda.type().definition()
    if hda_def == None:
        raise ValueError('Node: {} is not a digital asset'.format(hda.name()))
    control_def = control.type().definition() 

    # Get ParmTemplateGroup
    ptg = hda_def.parmTemplateGroup()
    control_ptg = control_def.parmTemplateGroup()

    # Check if folder exists if does get of it and remove it from hda
    # otherwise create new empty one
    folder = ptg.findFolder(folder_label)
    if folder == None:
        # print('No folder found {}'.format(folder_label))
        folder = hou.FolderParmTemplate(folder_name, folder_label)
    
    # Check which channels should be promoder, if all 3 channels are locked then skip this parameter
    attrs = []
    for att in 'trs':
        locked = 1 
        for axis in 'xyz':
            if not control.parm('{0}{1}'.format(att, axis)).isLocked() :
                locked *= 0 
        
        if locked == 0:
            attrs.append(att)
    
    # Create unlocked channels at folder
    control_name = control.name()
    for att in attrs:
        channel_name  = '{0}_{1}'.format(control_name, att)
        channel_label = '{0} {1}'.format(control_name.replace('_', ' '), att.title())
        
        channel_temp = control_ptg.find(att).clone()
        channel_temp.setName(channel_name)
        channel_temp.setLabel(channel_label)

        # before adding check if it exists
        if ptg.find(channel_name) != None:
            ptg.replace(channel_name, channel_temp)
        else:
            folder.addParmTemplate(channel_temp)
        
        #channel_temp  = hou.FloatParmTemplate(channel_name, channel_label, 3, default_value=(0.0, ))

    # Update HDA definition template
    if ptg.findFolder(folder_label) != None: 
        ptg.remove(ptg.findFolder(folder_label).name())
    ptg.addParmTemplate(folder)
    hda_def.setParmTemplateGroup(ptg)

    # Connect hda channel to the control parameter 
    for att in attrs:
        channel_name   = '{0}_{1}'.format(control_name, att)
        control_parm_t = control.parmTuple(att)
        asset_parm_t   = hda.parmTuple(channel_name)

        if control_parm_t == None or asset_parm_t == None:
            raise ValueError('Something is wrong, parameters doesn\'t exists')

        for i in range(len(control_parm_t)):
            if not control_parm_t[i].isLocked():
                # print('{}->{}'.format(control_parm_t[i], asset_parm_t[i]))
                control_parm_t[i].deleteAllKeyframes()
                control_parm_t[i].set(asset_parm_t[i])



def get_object_level_network(node):
    """
    Query first object level network of selected node

    Args:
        node (hou.Node): Look for first object level network for this node
        
    Returns 
        network (hou.Node): Object level network
    """

    # Check if object have a parent
    parent = node.parent()
    if parent == None:
        return None

    # Get the first object level node
    while True:

        if parent.type().category().name() == 'Object':
            # Stop when you find first object node, usually it's a rig node
            # the next up will be your controls network
            break
        elif parent == None:
            raise ValueError('Can\'t find object level network for {} node'.format(node.name()))

        parent = parent.parent()

    # Try get the next up parent, that will be controls network 
    new_parent = parent.parent()
    if new_parent != None :
        if new_parent.type().category().name() == 'Object' or new_parent.type().category().name() == 'Manager':
            return new_parent
    else:
        return parent
    
    return None



def run(controls_network=None):
    nodes = hou.selectedNodes() 

    if len(nodes) == 0:
         hou.ui.setStatusMessage('No nodes selected!',hou.severityType.Warning )
         return None 

    # Default use 
    if not controls_network:
            controls_network = get_object_level_network(nodes[0])

    # Check node types
    for node in nodes:
        if not _have_control_attributes(node):
            raise IOError('Please select nodes with controls attributes')
        
        connections = node.outputConnections()
        rig_network = node.parent()
        
        # Create zeros node
        zero_wrangle = rig_network.createNode(conf.hda_def['create_zero_attr'], node_name='{}_zeros'.format(node.name()))
        zero_wrangle.setInput(0, node)
        zero_wrangle.moveToGoodPosition()

        mirror_scale = zero_wrangle.geometry().attribValue("mirror_scale")
        zero_wrangle.parmTuple('mirror_scale').set(mirror_scale)

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

            # Add control to group
            _add_to_group(controls_network, control, 'controls')

        # Add rig pose and zero_attr to group
        _add_to_group(rig_network, rig_pose, 'zero_and_rpose')
        _add_to_group(rig_network, zero_wrangle, 'zero_and_rpose')
        
        print("To parent: {}".format(to_parent))
        

        # Create hierarchy 
        for zero_node, control, parent_name in to_parent:

            print('Parenting \'{0}\' to \'{1}\''.format(zero_node.name(), parent_name))
            
            parent = controls_network.node(parent_name)
            
            if parent == None:
                # Read worldspace data
                zero_node.parm("world_space").set(1)

                # Flip axises 
                if mirror_scale != (1.0, 1.0, 1.0) :
                    print(mirror_scale)
                    zero_node.parmTuple('s').set([-1.0, -1.0, -1.0])

                print('\tParent {0} for {1} doesn\'t exists - setting zero nodes to world space'.format(parent_name, control.name() ))
                continue

            zero_node.setInput(0, parent)