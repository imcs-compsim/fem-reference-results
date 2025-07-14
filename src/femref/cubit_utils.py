from typing import List, Union

from cubitpy import CubitPy


def cubit_cmd(
    command: str,
    cubit: CubitPy,
    track_id: str = "volume",
    flatten_if_possible: bool = True,
) -> Union[List[int], int]:
    """Performs a cubit operation and returns the IDs of the added entities.

    Parameters
    ----------
    command : str
        The cubit command to execute.
    cubit : CubitPy
        The CubitPy instance to use for executing the command.
    track_id : str, optional
        The type of entity to track (default is "volume").
    flatten_if_possible : bool, optional
        If True and only one ID would be returned, the ID will be returned as a single value instead of as a list with one single entry.

    Returns
    -------
    Union[List[int], int]
        A list of new IDs created by the command.
    """
    # Step 1: Get current IDs of entities to be tracked
    before_cmd = set(cubit.parse_cubit_list(track_id, "all"))
    # Step 2: Perform cubit command
    cubit.cmd(command)
    # Step 3: Get IDs after the cubit command
    after_cmd = set(cubit.parse_cubit_list(track_id, "all"))
    # Step 4: New IDs are the difference
    new_ids = list(after_cmd - before_cmd)
    # If the list contains only one ID, return it as a single value
    if len(new_ids) == 1 and flatten_if_possible:
        return new_ids[0]
    # Otherwise, return the list of new IDs
    return new_ids


def print_mesh_statistics(cubit: CubitPy) -> None:
    """Prints statistics about the generated mesh.

    The statics comprise the total number of nodes, total number of elements
    as well as the number of nodes in each nodeset.

    Parameters
    ----------
    cubit : CubitPy
        The CubitPy instance to use for retrieving mesh statistics.
    """
    # Print information about the total number of nodes and elements in the mesh
    num_nodes = cubit.get_node_count()
    num_elements = cubit.get_element_count()
    print(f"Total nodes:        {num_nodes}")
    print(f"Total elements:     {num_elements}")
    # Print information about the number of nodes in each nodeset
    nodeset_ids = cubit.parse_cubit_list("nodeset", "all")
    for nsid in nodeset_ids:
        print(f"Nodes in Nodeset {nsid}: {cubit.get_nodeset_node_count(nsid)}")
