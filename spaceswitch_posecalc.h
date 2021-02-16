// VEX code used by space switch node
//
// Author: Kamil Hepner
// Email: kamilhepnerdeveloper@gmail.com

#include <kinefx.h>
#include <kinefx_posedifference.h>

// Get joint data
string joint_name = chs("../joint") ;
string split[] = split(joint_name, "=");
if(len(split) > 1)
    joint_name = split[1] ;

int joint_id = findattribval(0, "point", "name", joint_name);
matrix joint_move_M  = pointtransform(0, joint_id) ;
matrix joint_stash_M = pointtransform(1, joint_id) ;


// Get space swtich
int chosen_space = chi("../spaceswitch") ;

// Transformation compoments used for blend
int components = chi("../components") ;

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

    parent_id = findattribval(2, "point", "name", parent_name);
    matrix parent_stash_M = pointtransform(2, parent_id) ;
    matrix parent_move_M  = pointtransform(3, parent_id) ;

    // Get diference matrix
    matrix diff_M = joint_stash_M * invert(parent_stash_M) ;
    
    // Finall matrix
    matrix end_M =  diff_M * parent_move_M ;

    // Blend with input 0
    matrix blend_M = blendtransforms(joint_move_M, end_M, 1.0, components) ;
    setpointtransform(0, joint_id, blend_M,1);

}

