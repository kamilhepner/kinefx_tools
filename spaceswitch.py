import hou



def _ui_get_spaces_names(node):
    """ Get all valid names of spaces """

    # Validate
    n_type = node.type()
    desc   = n_type.description()

    if not 'Space switch' in desc:
        raise ValueError("Node isn\'t type of Space switch")

    config_parm   = node.parm("config")
    parms         = config_parm.multiParmInstances()
    multiparm_len = len(config_parm.parmTemplate().parmTemplates())

    names = []

    for idx in range(config_parm.eval()):
        name     = parms[(idx * multiparm_len)].eval()
        parent   = parms[(idx * multiparm_len) + 1].eval()

        if name != '' :
            names.append(name)
    

    return names




