import os
from cubitpy import CubitPy, cupy

from femref.cubit_utils import print_mesh_statistics
from femref.utils import write_readme

"""
This script generates an input file for simulating the torsion of a block with
non-linear material behavior.
"""

############
# CONTROLS #
############

##### GEOMETRY & MESH #########################################################
# length of the block geometry
LENGTH = 4
# height of the block geometry
HEIGHT = 1
# depth of the block geometry
DEPTH = 1
# integer indicating the mesh granularity, ranging from 1 (finest) to 10
# (coarsest)
MESH_SIZE = 0.1
# tolerance for identifying BCs based on point coordinates
EPS = 1e-5

##### MODEL ###################################################################
# kinematics (relation between strains and displacements)
KINEMATICS = "nonlinear"

##### MATERIAL ################################################################
# https://github.com/4C-multiphysics/4C/blob/main/src/mat/elast/4C_mat_elast_couplogneohooke.cpp#L32
# Young's modulus
YOUNG = 1.33
# Poisson's ratio
POISSON = 0.33

##### BOUNDARY CONDITIONS #####################################################
# The maximum prescribed rotation at the right end of the block
END_ROTATION = 150  # Degrees
# The number of load steps in which to apply the prescribed rotation
LOAD_STEPS = 50

##### OUTPUT ##################################################################
# flag indicating which intermediate steps should be visualized
SHOW_STEP = [False, False, False, False]
# flag indicating that the result of the last step should be visualized
SHOW_FINAL = True


#############
# VARIABLES #
#############

"""Dictionary with options for the CubitPy instance."""
OPTIONS = {
    "title": "Torsion of a block with non-linear kinematic behavior",
    "description": "We simulate the torsion of a block by prescribing a Dirichlet BC which increases with the load step.",
    "geometry": {
        "length": LENGTH,
        "height": HEIGHT,
        "depth": DEPTH,
    },
    "mesh": {
        "mesh_size": MESH_SIZE,
    },
    "model": {"kinematics": KINEMATICS},
    "material": {
        "constitutive_law": "ELAST_CoupLogNeoHooke",
        "youngs_modulus": YOUNG,
        "poisson_ratio": POISSON,
    },
    "boundary_conditions": {
        "end_rotation": END_ROTATION,
        "load_steps": LOAD_STEPS,
    },
}


##########
# SCRIPT #
##########


def generate_block(filename: str) -> None:
    """ """

    cubit = CubitPy()

    # create a rectangle with specified width and height
    cubit.cmd(f"brick x {LENGTH} y {HEIGHT} z {DEPTH}")

    # retrieve the id of the block that was just added
    block = cubit.volume(cubit.get_last_id(cupy.geometry.volume))

    if SHOW_STEP[0]:
        cubit.display_in_cubit()

    # translate the block to the origin
    cubit.cmd(
        f"move volume {block.id()} x {LENGTH / 2} y 0 z 0 include_merged"
    )

    if SHOW_STEP[1]:
        cubit.display_in_cubit()

    # generate the mesh of the block
    cubit.cmd(f"volume {block.id()} size {MESH_SIZE}")
    cubit.cmd(f"mesh volume {block.id()}")

    if SHOW_STEP[2]:
        cubit.display_in_cubit()

    # add the boundary conditions
    cubit.add_node_set(
        cubit.group(add_value=f"add surface with x_coord < {EPS}"),
        name="rigid_left",
        bc_type=cupy.bc_type.dirichlet,
        bc_description="NUMDOF 3 ONOFF 1 1 1 VAL 0 0 0 FUNCT 0 0 0",
    )
    cubit.add_node_set(
        cubit.group(add_value=f"add surface with x_coord > {LENGTH - EPS}"),
        name="torsion_right",
        bc_type=cupy.bc_type.dirichlet,
        bc_description="NUMDOF 3 ONOFF 1 1 1 VAL 0 1 1 FUNCT 0 1 2",
    )

    if SHOW_STEP[3] or SHOW_FINAL:
        cubit.display_in_cubit(labels=[cupy.geometry.surface])

    # Finally we have to set the element blocks.
    cubit.add_element_type(
        block.volumes()[0],
        el_type=cupy.element_type.hex8,
        bc_description=f"KINEM {KINEMATICS}",
    )

    # Print mesh statistics
    print_mesh_statistics(cubit)

    # Set the head string.
    cubit.head = f"""------------------------------------------------------------------PROBLEM SIZE
    DIM                             3
    ------------------------------------------------------------------PROBLEM TYPE
    PROBLEMTYPE                     Structure
    ----------------------------------------------------------------------------IO
    OUTPUT_BIN                      no
    STRUCT_DISP                     yes
    FILESTEPS                       1000
    VERBOSITY                       Standard
    STRUCT_STRAIN                   gl
    STRUCT_STRESS                   cauchy
    OUTPUT_SPRING                   Yes
    WRITE_INITIAL_STATE             yes
    ---------------------------------------------------------IO/RUNTIME VTK OUTPUT
    OUTPUT_DATA_FORMAT              binary
    INTERVAL_STEPS                  5
    EVERY_ITERATION                 no
    -----------------------------------------------IO/RUNTIME VTK OUTPUT/STRUCTURE
    OUTPUT_STRUCTURE                yes
    DISPLACEMENT                    yes
    ELEMENT_OWNER                   yes
    STRESS_STRAIN                   yes
    ------------------------------------------------------------STRUCTURAL DYNAMIC
    INT_STRATEGY                    Standard
    DYNAMICTYPE                     Statics
    RESULTSEVERY                    5
    RESTARTEVERY                    {LOAD_STEPS}
    TIMESTEP                        {1.0 / LOAD_STEPS}
    NUMSTEP                         {LOAD_STEPS}
    MAXTIME                         1
    PREDICT                         ConstDis
    NORM_RESF                       Rel
    TOLDISP                         1e-7
    TOLRES                          1e-7
    NORMCOMBI_DISPPRES              And
    LINEAR_SOLVER                   1
    NLNSOL                          fullnewton
    MAXITER                         20
    ----------------------------------------------------------------------SOLVER 1
    NAME                            Structure_Solver
    SOLVER                          Superlu
    -----------------------------------------------------------STRUCT NOX/Printing
    Outer Iteration                 = Yes
    Inner Iteration                 = No
    Outer Iteration StatusTest      = Yes
    ---------------------------------------------------------------------MATERIALS
    MAT 1  MAT_ElastHyper NUMMAT 1 MATIDS 10 DENS 1
    MAT 10 ELAST_CoupLogNeoHooke MODE YN C1 {YOUNG} C2 {POISSON}
    ------------------------------------------------------------------------FUNCT1
    SYMBOLIC_FUNCTION_OF_SPACE_TIME y*cos({2 * END_ROTATION / 360}*pi*t)-z*sin({2 * END_ROTATION / 360}*pi*t)-y
    ------------------------------------------------------------------------FUNCT2
    SYMBOLIC_FUNCTION_OF_SPACE_TIME y*sin({2 * END_ROTATION / 360}*pi*t)+z*cos({2 * END_ROTATION / 360}*pi*t)-z"""

    # Write the input file.
    cubit.create_dat(filename)


##########
# SCRIPT #
##########

if __name__ == "__main__":
    path = f"./{KINEMATICS}"
    os.makedirs(f"{path}", exist_ok=True)

    generate_block(f"{path}/block_torsion.dat")

    write_readme(f"{path}/README.md", OPTIONS)
