from cubitpy import CubitPy, cupy

from femref.cubit_utils import print_mesh_statistics
from femref.utils import write_readme

"""
This file generates the geometry for a simple bending beam test case.
The bending beam domain is made from a hyper-elastic material and large
deformations are considered, thus the kinematic behavior is non-linear.
The deformation is driven by a shear force at the end of the beam which depends
on the load step.
"""

############
# CONTROLS #
############

##### GEOMETRY & MESH #########################################################
# length of the bending beam geometry
LENGTH = 20  # [m]
# height of the bending beam geometry
HEIGHT = 2  # [m]
# integer indicating the mesh granularity, ranging from 1 (finest) to 10
# (coarsest)
MESH_SIZE = 0.1  # [m]
# tolerance for identifying BCs based on point coordinates
EPS = 1e-5

##### MODEL ###################################################################
# kinematics (relation between strains and displacements)
KINEMATICS = "nonlinear"
# closure equation for computing the stresses from the strains
STRESS_STRAIN_MODEL = "plane_strain"

##### MATERIAL ################################################################
# https://github.com/4C-multiphysics/4C/blob/main/src/mat/elast/4C_mat_elast_couplogneohooke.cpp#L32
# C1 - Shear modulus
MUE = 4.17e9  # [Pa] (4.17GPa)
# C2 - Lamé parameter
LAMBDA = 2.78e9  # [Pa] (2.78GPa)
# Young's modulus
YOUNG = MUE * (3.0 * LAMBDA + 2.0 * MUE) / (LAMBDA + MUE)  # [Pa]
# Poisson's ratio
NUE = LAMBDA / (2.0 * (LAMBDA + MUE))  # [-]

##### BOUNDARY CONDITIONS #####################################################
# The prescribed shear load at the right end of the beam
SHEAR_FORCE = 10.0e6  # [Pa] (10MPa)
# The number of load steps in which to apply the prescribed shear force
LOAD_STEPS = 50

##### OUTPUT ##################################################################
# flag indicating which intermediate steps should be visualized
SHOW_STEP = [False, False, False]
# flag indicating that the result of the last step should be visualized
SHOW_FINAL = False


#############
# VARIABLES #
#############

"""Dictionary with options for the CubitPy instance."""
OPTIONS = {
    "title": "Hyperelastic bending beam with nonlinear kinematics under shear force",
    "description": "We simulate the large deformation of a hyperelastic bending beam by prescribing a Neumann BC which increases with the load step.",
    "geometry": {
        "length": LENGTH,
        "height": HEIGHT,
    },
    "mesh": {
        "mesh_size": MESH_SIZE,
    },
    "model": {
        "kinematics": KINEMATICS,
        "stress_closure": STRESS_STRAIN_MODEL,
    },
    "material": {
        "constitutive_law": "ELAST_CoupLogNeoHooke",
        "shear_modulus": MUE,
        "lame_parameter": LAMBDA,
    },
    "boundary_conditions": {
        "max_shear_force": SHEAR_FORCE,
        "load_steps": LOAD_STEPS,
    },
}


##########
# SCRIPT #
##########


def generate_bending_beam(filename: str) -> None:
    """ """

    cubit = CubitPy()

    # create a rectangle with specified width and height
    cubit.cmd(
        f"create surface rectangle width {LENGTH} height {HEIGHT} zplane"
    )

    # retrieve the id of the beam that was just added
    beam = cubit.surface(cubit.get_last_id(cupy.geometry.surface))

    if SHOW_STEP[0]:
        cubit.display_in_cubit()

    # generate the mesh of the beam
    cubit.cmd(f"surface {beam.id()} size {MESH_SIZE}")
    cubit.cmd(f"mesh surface {beam.id()}")

    if SHOW_STEP[1]:
        cubit.display_in_cubit()

    # add the boundary conditions
    cubit.add_node_set(
        cubit.group(add_value=f"add curve with y_coord < {-HEIGHT / 2 + EPS}"),
        name="bottom",
        bc_type=cupy.bc_type.dirichlet,
        bc_description="NUMDOF 2 ONOFF 0 0 VAL 0 0 FUNCT 0 0",
    )
    cubit.add_node_set(
        cubit.group(add_value=f"add curve with x_coord < {-LENGTH / 2 + EPS}"),
        name="left",
        bc_type=cupy.bc_type.dirichlet,
        bc_description="NUMDOF 2 ONOFF 1 1 VAL 0 0 FUNCT 0 0",
    )
    cubit.add_node_set(
        cubit.group(add_value=f"add curve with y_coord > {HEIGHT / 2 - EPS}"),
        name="top",
        bc_type=cupy.bc_type.dirichlet,
        bc_description="NUMDOF 2 ONOFF 0 0 VAL 0 0 FUNCT 0 0",
    )
    cubit.add_node_set(
        cubit.group(add_value=f"add curve with x_coord > {LENGTH / 2 - EPS}"),
        name="right",
        bc_type=cupy.bc_type.neumann,
        bc_description=f"NUMDOF 2 ONOFF 0 1 VAL 0 {-SHEAR_FORCE} FUNCT 0 1",
    )

    # Finally we have to set the element blocks.
    cubit.add_element_type(
        beam.surfaces()[0],
        el_type=cupy.element_type.quad4,
        bc_description=f"KINEM {KINEMATICS} EAS none THICK 1 STRESS_STRAIN {STRESS_STRAIN_MODEL} GP 2 2",
    )

    # Print mesh statistics
    print_mesh_statistics(cubit)

    if SHOW_STEP[2] or SHOW_FINAL:
        cubit.display_in_cubit(labels=[cupy.geometry.curve])

    # Set the head string.
    cubit.head = f"""------------------------------------------------------------------PROBLEM SIZE
    DIM                             2
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
    INTERVAL_STEPS                  {LOAD_STEPS / 10.0}
    EVERY_ITERATION                 no
    -----------------------------------------------IO/RUNTIME VTK OUTPUT/STRUCTURE
    OUTPUT_STRUCTURE                yes
    DISPLACEMENT                    yes
    ELEMENT_OWNER                   yes
    STRESS_STRAIN                   yes
    ------------------------------------------------------------STRUCTURAL DYNAMIC
    INT_STRATEGY                    Standard
    DYNAMICTYPE                     Statics
    RESULTSEVERY                    1
    RESTARTEVERY                    1
    TIMESTEP                        {1.0 / LOAD_STEPS}
    NUMSTEP                         {LOAD_STEPS}
    MAXTIME                         1
    PREDICT                         TangDis
    NORM_RESF                       Rel
    TOLDISP                         1e-7
    TOLRES                          1e-7
    LINEAR_SOLVER                   1
    NLNSOL                          fullnewton
    MAXITER                         50
    ----------------------------------------------------------------------SOLVER 1
    NAME                            Structure_Solver
    SOLVER                          Superlu
    -----------------------------------------------------------STRUCT NOX/Printing
    Outer Iteration                 = Yes
    Inner Iteration                 = No
    Outer Iteration StatusTest      = No
    ---------------------------------------------------------------------MATERIALS
    MAT 1  MAT_ElastHyper NUMMAT 1 MATIDS 10 DENS 0.1
    MAT 10 ELAST_CoupLogNeoHooke MODE Lame C1 {MUE} C2 {LAMBDA}
    ------------------------------------------------------------------------FUNCT1
    SYMBOLIC_FUNCTION_OF_SPACE_TIME t"""

    # Write the input file.
    cubit.create_dat(filename)


##########
# SCRIPT #
##########

if __name__ == "__main__":
    generate_bending_beam("./hyperelastic_bending_beam.dat")

    write_readme("./README.md", OPTIONS)
