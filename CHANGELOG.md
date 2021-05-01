# Changelog

Changes documentation
Author: Kamil Hepner



## [0.2.1] - 2021.05.01
### Changed
- (create_obj_ctrls.py) - get_object_level_network() bug fixes, now works with subnetworks inside of rig networks.
- (create_obj_ctrls.py) - run(), mirror bug fix. 
- space_switch 1.0 -> 1.1 - Added "Stash Inputs" button to initialize transform offsets. Usually needs to be restashed
if your hierarchy or input skeletons changed

## [0.2.0] - 2021.03.23
### Changed
- Attach Control Geometry (new version 1.2) added attribute to specify if the skeleton was mirrored by the scale
and not rotation. Updated python code inside of that HDA to support that change.

- Create zero attr (new version 1.1) added support for controls being mirrored by the scale and not rotation.
Also, the node will output an additional detail attribute called: 
<control_name>_zero_world_tr and <control_name>_zero_world_rot <- those values will be used by zero node
in the case if control doesn't have a parent. 


## [0.1.1] - 2021-02-17
### Added 
- Space switch node. 

### Changed
- Readme reogranized a bit


## [0.1.0] - 2021-01-15
### Added

- Config file to specifying HDAs definitions. That will help us to keep 
everything in sync with every tool release.

- Connection for a scale parameter between object control and rig pose

- New function promote_control() which automates promotion of transformation channels from
controls to your rig HDA.

- Functionality to specify which transformation channels should be locked on Attach Geometry 
Control node. 

- New function _add_to_group() will be used to add newly created controls to the controls group. 
Groups are very handy when you want for example select all nodes in group and them promote all 
transformation channels to your hda rig definition

### Changed
- Code for creating zero_node inside _create_obj_control() function
has been moved into separated functionL _create_zero_node()

- run() function now takes argument controls_network which allows you explicitly specify
which at which network controls should be created. /Obj network isn't default anymore.
As default value script searches for first object level network of your rig node.

- Ddefinition of "Attach Geometry Control custom" to "kinefx::attach_geometry_control::1.1"
to help keep things more organized


