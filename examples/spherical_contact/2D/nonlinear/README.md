# Hertzian-type contact with large deformation

We simulate a two-dimensional hertzian-type contact problem by subjecting a 2D semicircle to a pressure on its top surface.


## geometry
| Parameter | Value |
|:--|:--|
| radius | 1 |
| h_width | 0.3 |
| h_height | 0.4 |
| h_arcloc | 0.7071067811865476 |


## mesh
| Parameter | Value |
|:--|:--|
| mesh_size_coarse | 0.1 |
| mesh_size_intermediate | 0.030000000000000002 |
| mesh_size_contact | 0.02 |


## model
| Parameter | Value |
|:--|:--|
| kinematics | nonlinear |


## material
| Parameter | Value |
|:--|:--|
| constitutive_law | ELAST_CoupLogNeoHooke |
| youngs_modulus | 1.33 |
| poisson_ratio | 0.33 |


## boundary_conditions
| Parameter | Value |
|:--|:--|
| end_pressure | 5 |
| load_steps | 50 |


Last updated: July 17, 2025 at 07:19PM
