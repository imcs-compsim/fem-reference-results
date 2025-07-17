# Hyperelastic bending beam with nonlinear kinematics under shear force

We simulate the large deformation of a hyperelastic bending beam by prescribing a Neumann BC which increases with the load step.


## geometry
| Parameter | Value |
|:--|:--|
| length | 20 |
| height | 2 |


## mesh
| Parameter | Value |
|:--|:--|
| mesh_size | 0.1 |


## model
| Parameter | Value |
|:--|:--|
| kinematics | nonlinear |
| stress_closure | plane_strain |


## material
| Parameter | Value |
|:--|:--|
| constitutive_law | ELAST_CoupLogNeoHooke |
| shear_modulus | 4170000000.0 |
| lame_parameter | 2780000000.0 |


## boundary_conditions
| Parameter | Value |
|:--|:--|
| max_shear_force | 10000000.0 |
| load_steps | 50 |


Last updated: July 17, 2025 at 02:49PM
