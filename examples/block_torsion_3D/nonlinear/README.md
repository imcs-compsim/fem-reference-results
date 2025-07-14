# Torsion of a block with non-linear kinematic behavior

We simulate the torsion of a block by prescribing a Dirichlet BC which increases with the load step.


## geometry
| Parameter | Value |
|:--|:--|
| length | 4 |
| height | 1 |
| depth | 1 |


## mesh
| Parameter | Value |
|:--|:--|
| mesh_size | 0.1 |


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
| end_rotation | 150 |
| load_steps | 50 |


Last updated: July 14, 2025 at 05:37PM
