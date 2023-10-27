# KineFX Tools

A collection of rigging tools and utilities for Houdini's KineFX.

![info | width=30px](images/info.png) These tools are compatible **only** with **Houdini 19.5** and newer versions. If you are using Houdini 18.5, please use the tools from the **h18.5** branch.

## Support

If you find these tools helpful and would like to support my work, consider buying me a virtual coffee:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/P5P337EBN)

## Installation

### Python Scripts

1. Copy all Python scripts to the source Python directory. Refer to the [Houdini Docs for Python script locations](https://www.sidefx.com/docs/houdini/hom/locations.html).
2. Alternatively, add the path to your `sys.path`.

### Digital Assets

Ensure all digital assets are installed and set up before using the scripts.

### Tutorial

Follow these steps for the majority of use cases:

1. Download from GitHub: [https://github.com/kamilhepner/kinefx_tools](https://github.com/kamilhepner/kinefx_tools)

2. Extract the zip to a directory of your choice. By default, it might be named something like *“C:\Users\YourUsername\Downloads\houdini\KineFX_Kamil_Tools\kinefx_tools-main”*

3. Rename the folder `kinefx_tools-main` to `kinefx_tools`.

4. Locate the `houdini.env` file in your Houdini preferences, typically found at: `C:\Users\YourUsername\Documents\houdini19.5\houdini.env`.

5. Update the file to include the path to `kinefx_tools/hda`. For example:
   ```
   KINFX=C:/Users/YourUsername/Downloads/houdini/KineFX_Kamil_Tools/kinefx_tools/hda
   ```
6. Add `$KINFX` to your OTLs path:
   ```
   HOUDINI_OTLSCAN_PATH = $KINFX;$MOPS/otls;@/otls;@/otls;$QLIB/base;$QLIB/future;$QLIB/experimental
   ```
7. Add `kinefx_tools` to the Python path:
   ```
   PYTHONPATH=C:/Users/YourUsername/Downloads/houdini/KineFX_Kamil_Tools;
   ```
8. Launch Houdini.
9. Create a new shelf named `kinefx_tools`.
10. Add a button and paste the following script. This button will create object-level controls:
   ```python
   import kinefx_tools
   kinefx_tools.create_obj_ctrls.run()
   ```
11. Add another button and paste the following script to promote selected controls to the top of your rig HDA:
   ```python
   import kinefx_tools
   kinefx_tools.create_obj_ctrls.promote_selected_controls()
   ```


## Changes in H19.5

KineFX has undergone continuous changes. To ensure the smooth operation of `kinefx_tools`, it's crucial to regularly update your rigs. Below is a list of key modifications needed for your setups:

### Using Existing Rigs

If you don't intend to alter your rigs and only want to animate them, they might function without any hitches. However, if you encounter any issues after updating your Houdini version, it's essential to:
- Upgrade all `kinefx_tools` and associated scripts to the latest versions.
- Recreate all object-level controls.
- Promote controls once more.

### Always Use the Latest Version of **Attach Control Geometry SOP**

Ensure you're using version **1.3** of **Attach Control Geometry SOP**. Regularly updating this component is vital when working on your rigs.

### Adjust Settings for **Attribute Delete** in Specific Setups, like Arms

For the **Attach Control Geometry** to operate flawlessly, certain additional attributes need to be removed. This is especially important in setups with both FK and IK controls, such as Arms or Legs. If you've followed my tutorials on CG Circuit or my YouTube channel, make sure to add the additional attributes to all your **Attribute Delete** nodes.

 - **Point Attributes**: channel_lock control_color control_folder control_offset control_scale control_xray world_space shape_name
 - **Vertex Attributes**:
 - **Primitive Attributes**: name jointgeo
 - **Detail Attributes**: mirror_scale gl_lit world_space

![h19_5_attribute_delete](images/h19_5_attribute_delete.png)

## HDAs
There are a few handy HDAs, some of them are required to be installed in order to use them with scripts. 

* ### Controls library (controls_library::1.0) (OBJ)
Generates different shapes of controls as geometry which can be used in conjunction with **Attach Control Geometry SOP**

required by: **create_obj_ctrls.py**

---

* ### Attach Control Geometry (kinefx::attach_obj_control::1.3) (SOP)
   Modified attach joint geometry sop. Added extra functionality to make the process of creating object level controls much faster. You can assign individual colors for controls, manipulate the scale of controls and their offsets directly from this one node.  
   
   ![attach_geometry_01](images/attach_obj_01.PNG)

   In case if your skeleton for these particular controls has been mirrored by the scale you need to set **Mirrored by scale** -> **ON** and specify at which Axis controls have been mirrored. For example, if your controls been mirrored along X-Axis, set the mirror scale to {-1.0, 1.0, 1.0}
   
   ![attach_geometry_ms_03](images/attach_geometry_ms_03.PNG)

   You can specify which channels will be locked after creating controls by setting **Translate/Rotate/Scale Lock** parameter

   **Control Folder** Let you specify the name of the folder into which controls will be promoted on your rig HDA. It's a second step to promote controls to your HDA, so filling that parameter is optional. 

   Also, this node adds extra attributes the jointgeo dictionary:
   
   ![attach_obj_jointgeo_02](images/attach_obj_jointgeo_02.PNG)
   
   Those extra values are quired during the creation of *object level* controls. Check step by step tutorial. Setting **Xray** parameter **ON** will make *object level* controls automatically set to Xray.

   required by: **create_obj_ctrls.py**

---

* ### rig control 1.0 (rig_control::1.0) (OBJ)
   Node used directly as rig control. Allow for dynamic change of control shape, which is loaded from the controls library. *Thickness* parameter adds easy control of how thick control should be displayed. 
   ![control_node_01](images/control_node_01.PNG)

   This node will be should be used in conjunction with *rig_zero* node as its parent (zero group). 

   required by: **create_obj_ctrls.py**

---

* ### rig zero 1.1 (rig_zero::1.1) (OBJ)
   This acts as a zero group for controls. But also moves them to keep them in sync with the joint's position. That node reads detail attributes generated by *create_zero_attr::1.2*

   ![rig_zero_01.PNG](images/rig_zero_01.PNG)

   All of that is created and connected automatically when using the create_obj_ctrls.py script.

   World space checkbox defines if the position of **rig zero node** should be queried from *local* or *world* transformation. It's handled automatically so you don't need to worry about it but in case if you unparent control which previously had a parent remember to turn **ON** world space

   ![rig_zero_ws_03.PNG](images/rig_zero_ws_03.PNG)

   ![rig_zero_ws_02.PNG](images/rig_zero_ws_02.PNG)

   required by: **create_obj_ctrls.py**

---

* ### create zero attrs 1.1 (create_zero_attr::1.1) (SOP)
   Breaks down *localtransform* matrix per channel and saves it as detail attribute for every joint. That information later is used by *rig_zero* node to move it.
   From version 1.2 it also breaks down world transformation and outputs for *rig_zero* node

   required by: **create_obj_ctrls.py**

---

* ### joint apply offset (joint_apply_offset::1.0) (SOP)
   Applies offset to joints. Useful for example when you do spline IK, after solving IK you would like to keep joints offset in such a way that they will match the original skeleton in the default pose. 

   To see it in action open: start.hiplc

   ![joint_offset](images/joint_offset_01.PNG)
----

* ### Space switch (space_switch::1.1) (SOP)
   The space switch node allows you to change spaces for the specified joint. To the **first input** connect joint/control (those are the same things) for which space switch you want to perform. **Second input** get all parent's information, those transforms will represent your different spaces.

   You can specify as many spaces as you want by adding entries with + sing next to the *Config* parameter

   ![space_switch_01.PNG](images/space_switch_01.png)
 
   In the **Joint** type the joint name with *@name=* at front of it. Space switch will happen for this joint. Use the multi-instance parameter *Config* to chose how many space switches you would like to have.
   
   **Stash Input** Need to be pressed in order to stash transform offsets. Also you need to stash your inputs if incoming skeletons changed (hierarchy or position)

   **Space name**: it's a descriptive name of your space switch. That name will show up on the menu where you can choose your spaces
   **Parent**: Joint name (with *@name=*) of that particular space/transform/parent.

   **Space** Allow you to chose currently active space:
   ![space_switch_02.PNG](images/space_switch_02.png)

   **Components** Let you specify for which transformation components you want to perform space switch. For example, for head FK control you only have a rotation space switch.

   **Tip**: In case if you would like to have a separated *Translation* and *Rotation* space switch. You can stack those two nodes, one after another.
   
   **Tutorial**: Check out this handy tutorial about how to use it:
   
[![Watch the video](https://img.youtube.com/vi/2TvOR7ohPdo/default.jpg)](https://www.youtube.com/watch?v=2TvOR7ohPdo)
----

## Usage

### Create object level control
```python
# You can add this code as button on shelf 
from kinefx_extra import create_obj_ctrls
create_obj_ctrls.run()
```

### Promote selected controls:
After the creating controls with above script. Now at object level you will have a group called controls. 
![controls_group](images/controls_group_01.PNG)

That will let you easily select all controls for your rig. Then just run script:
```python
# You can add this code as button on shelf 
import kinefx_tools
kinefx_tools.create_obj_ctrls.promote_selected_controls()
```

### Create object level controls - Video:
[![Watch the video](https://img.youtube.com/vi/uQ1cNjDZ-fs/default.jpg)](https://www.youtube.com/watch?v=uQ1cNjDZ-fs)

### Easy way of locking channels- Video:
[![Watch the video](https://img.youtube.com/vi/iCS5VFZQDQU/default.jpg)](https://www.youtube.com/watch?v=iCS5VFZQDQU)

### Create object level controls - Video:
[![Watch the video](https://img.youtube.com/vi/8Ev4VLDgE5I/default.jpg)](https://www.youtube.com/watch?v=8Ev4VLDgE5I)

### How to use Space Switch node - Video:
[![Watch the video](https://img.youtube.com/vi/2TvOR7ohPdo/default.jpg)](https://www.youtube.com/watch?v=2TvOR7ohPdo)

## Tips

### Bypass Attach Controls Geometry node
After creating your object level controls, you can bypass all Attach Controls Geometry nodes. That will speedup rig significantly due to the slow Python SOP inside. They aren't needed anymore, but keep them in case you would like to change something later. The bypass is enough. You can create group: or bundle if you prefer to be able to easily switch them ON and OFF. 

### Use blast instead of delete joints SOP
Delete joints sop does an extra reparenting steps via python code. Use blast wherever you can. 


## Contributing and support
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[Apache-2.0](https://choosealicense.com/licenses/apache-2.0/)
