# FEM reference results
This is a repository for collecting high-fidelity FEM reference results obtained with the open-source multi-physics simulation code [`4C`](https://github.com/4C-multiphysics/4C). These reference results might be used, e.g., to benchmark SciML applications.

Every example in this repository comes with a python script that uses [`CubitPy`](https://github.com/imcs-compsim/cubitpy/) to generate the respective `4C` input file.

# Requirements
This project requires:
- [Git Large File Storage](https://git-lfs.com)
- [pre-commit](https://pre-commit.com)

If you do not want to set it up via `conda`/`mamba` please make sure to look up the installation guidelines for your system to make sure that everything is running smoothly.

## Installation via `conda`/`mamba`
To install all dependencies required for development, a `environment.yml` is provided. Simply create an environment by running
```sh
mamba env create -f environment.yml
```
Afterwards you can activate your environment through
```sh
mamba activate fem-ref-env
```
and you are good to go.

Once all requirements are installed, you just need to initialize `git-lfs` and `pre-commit` by running
```sh
git lfs install
pre-commit install
```
