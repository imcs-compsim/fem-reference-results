import datetime
from typing import Dict, Union


def write_readme(
    filepath: str, options: Dict[str, Union[int, float, str]]
) -> None:
    """Generates a README file with basic information about the problem.

    Parameters
    ----------
    filepath : str
        The path where the README file will be created.
    options : Dict[str, Union[int,float,str]]
        A dictionary containing information about the problem parameters as
        key-value pairs.
    """
    # ensure the filepath contains README.md
    if not filepath.endswith("README.md"):
        filepath = f"{filepath}/README.md"
    # create and open th README file
    with open(filepath, "w") as f:
        # write the header
        f.write(f"# {options['title']}\n\n")
        f.write(f"{options['description']}\n\n\n")
        # write the parameters
        for key, value in options.items():
            if hasattr(value, "items"):
                f.write(f"## {key}\n")
                f.write("| Parameter | Value |\n|:--|:--|\n")
                for param, val in value.items():
                    f.write(f"| {param} | {val} |\n")
                f.write("\n\n")
        f.write(
            f"Last updated: {datetime.datetime.now().strftime('%B %d, %Y at %I:%M%p ')}\n"
        )
