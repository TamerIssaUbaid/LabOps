import argparse
import sys

from labops import __version__
from labops.docker import (
    DockerUnavailableError,
    get_docker_status,
)


def show_status():
    print("\nLabOps Platform Status")
    print("=" * 30)

    try:
        status = get_docker_status()

    except DockerUnavailableError as error:
        print("Docker Engine: Offline")
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Docker Engine: Online")
    print(f"Docker Version: {status['engine_version']}")

    print("\nLabOps Containers")
    print("-" * 30)

    containers = status["containers"]

    if not containers:
        print("No LabOps containers found.")

    else:
        for container in containers:
            print(
                f"{container['name']}: "
                f"{container['status']}"
            )

    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="labops",
        description="LabOps - Infrastructure Automation Platform",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available operations",
    )

    subparsers.add_parser(
        "status",
        help="Show platform status",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "status":
        return show_status()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
