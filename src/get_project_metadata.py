import argparse

import tomllib


def get_project_metadata(key):
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    metadata = data["project"][key]
    return metadata


def get_version(args):
    version = get_project_metadata("version")
    print(version)


def get_name(args):
    name = get_project_metadata("name")
    print(name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract project metadata from pyproject.toml."
    )
    subparsers = parser.add_subparsers(help="sub-command help")

    # Subparser for getting the name
    parser_name = subparsers.add_parser("name", help="Extract project name.")
    parser_name.add_argument(
        "--file",
        type=str,
        default="pyproject.toml",
        help="Path to the pyproject.toml file.",
    )
    parser_name.set_defaults(func=get_name)

    # Subparser for getting the version
    parser_version = subparsers.add_parser("version", help="Extract project version.")
    parser_version.add_argument(
        "--file",
        type=str,
        default="pyproject.toml",
        help="Path to the pyproject.toml file.",
    )
    parser_version.set_defaults(func=get_version)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
