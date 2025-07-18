import os
import numpy as np
from cubitpy import CubitPy, cupy

from femref.cubit_utils import print_mesh_statistics
from femref.utils import write_readme

"""
This script generates an input file for simulating a two-dimensional
Hertzian-type contact problem (under large deformation).
"""

############
# CONTROLS #
############

##### GEOMETRY & MESH #########################################################
# radius of the semicircle
RADIUS = 1
# helper width to define the blocks in which the semi circle is divided
H_WIDTH = 0.3
# helper height to define the blocks in which the semi circle is divided
H_HEIGHT = 0.4
# helper location on the semicircle arc to define the blocks in which the semi circle is divided
H_ARCLOC = np.sqrt(0.5)
# approximate mesh size IN the contact region (in units of length)
MESH_SIZE_CONTACT = 0.02
# approximate mesh size AWAY FROM the contact region (in units of length)
MESH_SIZE_COARSE = 0.1
# intermediate mesh size
# (in the middle of the semicircle, where the different blocks join)
MESH_SIZE_INTERMEDIATE = 0.5 * (MESH_SIZE_COARSE + MESH_SIZE_CONTACT) / 2
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
# The maximum prescribed presser on top of the semi circle
PRESSURE = 5  # Degrees
# The number of load steps in which to apply the prescribed rotation
LOAD_STEPS = 50

##### OUTPUT ##################################################################
# flag indicating which intermediate steps should be visualized
SHOW_STEP = [False, False, False, False, False]
# flag indicating that the result of the last step should be visualized
SHOW_FINAL = True


#############
# VARIABLES #
#############

"""Dictionary with options for the CubitPy instance."""
OPTIONS = {
    "title": "Hertzian-type contact with large deformation",
    "description": "We simulate a two-dimensional hertzian-type contact problem by subjecting a 2D semicircle to a pressure on its top surface.",
    "geometry": {
        "radius": RADIUS,
        "h_width": H_WIDTH,
        "h_height": H_HEIGHT,
        "h_arcloc": H_ARCLOC,
    },
    "mesh": {
        "mesh_size_coarse": MESH_SIZE_COARSE,
        "mesh_size_intermediate": MESH_SIZE_INTERMEDIATE,
        "mesh_size_contact": MESH_SIZE_CONTACT,
    },
    "model": {"kinematics": KINEMATICS},
    "material": {
        "constitutive_law": "ELAST_CoupLogNeoHooke",
        "youngs_modulus": YOUNG,
        "poisson_ratio": POISSON,
    },
    "boundary_conditions": {
        "end_pressure": PRESSURE,
        "load_steps": LOAD_STEPS,
    },
}


##########
# SCRIPT #
##########


def generate_semicircle(filename: str) -> None:
    """Generate the input file for this test case.

    Parameters
    ----------
    filename : str
        Name (and path) of the generated simulation input file.
    """

    # Start the cubit session
    cubit = CubitPy()

    # iterate through all vertices clockwise, starting from the origin
    cubit.cmd("create vertex 0 0 0")
    cubit.cmd(f"create vertex {H_WIDTH} 0 0")
    cubit.cmd(f"create vertex {RADIUS} 0 0")
    cubit.cmd(f"create vertex {H_ARCLOC} {-H_ARCLOC} 0")
    # cubit.cmd(f"create vertex 0 {-RADIUS} 0")
    cubit.cmd(f"create vertex {-H_ARCLOC} {-H_ARCLOC} 0")
    cubit.cmd(f"create vertex {-RADIUS} 0 0")
    cubit.cmd(f"create vertex {-H_WIDTH} 0 0")
    # add the additional interior helper vertices
    cubit.cmd(f"create vertex {-0.75 * H_WIDTH} {-H_HEIGHT} 0")
    cubit.cmd(f"create vertex {0.75 * H_WIDTH} {-H_HEIGHT} 0")

    if SHOW_STEP[0]:
        cubit.display_in_cubit()

    # create the outline curves first
    # (IDs referring to vertices in order of creation)
    cubit.cmd("create curve vertex 2 3")
    cubit.cmd(f"create curve arc center vertex 1 3 4 radius {RADIUS}")
    cubit.cmd(f"create curve arc center vertex 1 4 5 radius {RADIUS}")
    cubit.cmd(f"create curve arc center vertex 1 5 6 radius {RADIUS}")
    cubit.cmd("create curve vertex 6 7")
    cubit.cmd("create curve vertex 7 2")
    # then the internal ones
    cubit.cmd("create curve vertex 4 9")
    cubit.cmd("create curve vertex 9 2")
    cubit.cmd("create curve vertex 5 8")
    cubit.cmd("create curve vertex 8 7")
    cubit.cmd("create curve vertex 8 9")

    if SHOW_STEP[1]:
        cubit.display_in_cubit()

    # create the surfaces from their bounding curves
    # (IDs referring to curves in order of creation)
    cubit.cmd("create surface curve 1 2 7 8")
    cubit.cmd("create surface curve 7 3 9 11")
    cubit.cmd("create surface curve 10 9 4 5")
    cubit.cmd("create surface curve 6 8 11 10")
    # create group for semicircle
    cubit.group(add_value="add surface 1 2 3 4", name="semicircle")

    # imprint and merge (i.e., make sure that the shared boundaries of the
    # individual surfaces are recognized as the same boundaries)
    cubit.cmd("imprint all")
    cubit.cmd("merge all")

    # create the surface for the rigid contact obstacle
    thickness = 0.1 * RADIUS
    cubit.cmd(
        f"create surface rectangle width {2 * RADIUS} height {thickness} zplane"
    )
    rigid_id = cubit.get_last_id(cupy.geometry.surface)
    # translate the surface down
    cubit.cmd(
        f"move surface {rigid_id} x 0 y {-RADIUS - 0.5 * thickness} z include_merged"
    )
    # create group for rigid obstacle
    cubit.group(add_value="add surface 5", name="obstacle")

    if SHOW_STEP[2]:
        cubit.display_in_cubit()

    # define the mesh granularity on the important curves that will allow us
    # to refine where needed
    cubit.cmd(
        f"curve 8  scheme bias fine size {MESH_SIZE_INTERMEDIATE} coarse size {MESH_SIZE_COARSE} start vertex 9"
    )
    cubit.cmd(
        f"curve 10 scheme bias fine size {MESH_SIZE_INTERMEDIATE} coarse size {MESH_SIZE_COARSE} start vertex 8"
    )
    cubit.cmd(
        f"curve 7  scheme bias fine size {MESH_SIZE_CONTACT} coarse size {MESH_SIZE_INTERMEDIATE} start vertex 4"
    )
    cubit.cmd(
        f"curve 9  scheme bias fine size {MESH_SIZE_CONTACT} coarse size {MESH_SIZE_INTERMEDIATE} start vertex 5"
    )
    cubit.cmd(
        f"curve 3  scheme bias fine size {MESH_SIZE_CONTACT} factor 1.0 "
    )

    # generate the mesh of the contact plane (one element is enough [Steinbrecher, 2024])
    cubit.cmd(f"surface {rigid_id} size {2 * RADIUS}")

    # mesh the whole geometry
    cubit.cmd("mesh surface all")

    if SHOW_STEP[3]:
        cubit.display_in_cubit()

    # add the node sets for the boundary conditions
    cubit.add_node_set(
        cubit.group(
            add_value=f"add curve with {-EPS} < y_coord and y_coord < {EPS}"
        ),
        name="top_boundary_neumann",
        bc_type=cupy.bc_type.neumann,
        bc_description={
            "NUMDOF": 2,
            "ONOFF": [0, 1],
            "VAL": [0, -PRESSURE],
            "FUNCT": [0, 1],
        },
    )
    cubit.add_node_set(
        cubit.group(add_value=f"add curve with y_coord < {-H_ARCLOC + EPS}"),
        name="bottom_boundary_contact",
        bc_type=cupy.bc_type.solid_to_solid_curve_contact,
        bc_description={
            "InterfaceID": 1,
            "Side": "Slave",
            "Initialization": "Inactive",
        },
    )

    # Finally we have to set the element blocks.
    cubit.add_element_type(
        cubit.group(add_value="add surface in semicircle"),
        el_type=cupy.element_type.quad4,
        bc_description={
            "KINEM": KINEMATICS,
        },
    )
    cubit.add_element_type(
        cubit.group(add_value="add surface in obstacle"),
        el_type=cupy.element_type.quad4,
        bc_description={
            "KINEM": KINEMATICS,
        },
    )

    # Print mesh statistics
    print_mesh_statistics(cubit)

    if SHOW_STEP[4] or SHOW_FINAL:
        cubit.display_in_cubit()


##########
# SCRIPT #
##########

if __name__ == "__main__":
    path = f"./{KINEMATICS}"
    os.makedirs(f"{path}", exist_ok=True)

    generate_semicircle(f"{path}/hertzian_contact.yaml")

    write_readme(f"{path}/README.md", OPTIONS)
