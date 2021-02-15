#include <kinefx.h>
#include <kinefx_posedifference.h>

// Calculate offset matrix between joint and it's parent

// Get joint data
string joint_name = chs("../joint") ;
string split[] = split(joint_name, "=");
if(len(split) > 1)
    joint_name = split[1] ;

int joint_id = findattribval(0, "point", "name", joint_name);
matrix joint_move_M  = pointtransform(0, joint_id) ;
matrix joint_stash_M = pointtransform(1, joint_id) ;

// PRINT
printf("\n-------------------------\n") ;
// printf("joint_M:%g\n",joint_M) ;
//printf("diff_M:%g\n",diff_M) ;

// Get space swtich
int chosen_space = chi("../spaceswitch") ;
// printf("Space: %g \n", chosen_space) ;
// Transformation compoments used for blend
int components = chi("../components") ;
printf("components: %g \n", components) ;


// Prep variables
string parent_parm ;
string parent_name ;
int parent_id ;

if(chosen_space >= 0 && chosen_space < chi("../config"))
{
    int i = chosen_space + 1 ;

    // Get parent data
    parent_parm = sprintf("../parent%d", i);
    parent_name = chs(parent_parm) ;
    split = split(parent_name, "=") ;
    if(len(split) > 1)
        parent_name = split[1] ;
    
    // printf("parent::%g\n",parent_name) ;

    parent_id = findattribval(2, "point", "name", parent_name);
    matrix parent_stash_M = pointtransform(2, parent_id) ;
    matrix parent_move_M  = pointtransform(3, parent_id) ;

    // Get diference matrix
    //matrix diff_M = posedifference("opinput:1", "opinput:0", parent_id, joint_id, "", 7, 0, 1);
    //printf("pose diff_M:%g\n\n",diff_M) ;
    printf("parent_move_M:%g\n\n",parent_move_M) ;

    matrix diff_M = joint_stash_M * invert(parent_stash_M) ;
    printf("my   diff_M:%g\n\n",diff_M) ;

    matrix end_M =  diff_M * parent_move_M ;
    printf("end_M:%g\n\n",end_M) ;

    matrix blend_M = blendtransforms(joint_move_M, end_M, 1.0, components) ;

    setpointtransform(0, joint_id, blend_M,1);

    // Add switch_offset attribute
    //int a = addattrib(0, "point", concat("switch_offset_",parent_name), zero);
    //setpointattrib(0, concat(joint_name, "_SWCO_",parent_name), joint_id, diff_M);
}

// printf("-------------------------\n") ;

