
import argparse
import sys

from labops import __version__

from labops.docker import (
    DockerUnavailableError,
    DockerCommandError,
    get_docker_status,
    stop_services,
    get_service_logs,
)

from labops.ansible import (
    AnsibleExecutionError,
    AnsibleUnavailableError,
    run_playbook,
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

    print("Docker Engine: Online")
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


def deploy():
    print("\nDeploying LabOps platform...")
    print("=" * 40)

    try:
        result = run_playbook("site")

    except AnsibleUnavailableError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    except AnsibleExecutionError as error:
        print("Deployment failed.", file=sys.stderr)
        print(error, file=sys.stderr)
        return 1

    print(result.stdout)

    if result.stderr:
        print(result.stderr, file=sys.stderr)

    print("\nLabOps deployment completed successfully.")

    return 0


def stop():
    print("\nStopping LabOps services...")
    print("=" * 40)

    try:
        result = stop_services()

    except (DockerUnavailableError, DockerCommandError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    print("LabOps services stopped successfully.")

    return 0


def show_logs(tail=100):
    print("\nLabOps Service Logs")
    print("=" * 40)

    try:
        result = get_service_logs(tail)

    except (DockerUnavailableError, DockerCommandError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(result.stdout or "No logs available.")

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

    # Status command
    subparsers.add_parser(
        "status",
        help="Show platform status",
    )

    # Deploy command
    subparsers.add_parser(
        "deploy",
        help="Prepare, deploy and validate the platform",
    )

    # Stop command
    subparsers.add_parser(
        "stop",
        help="Stop LabOps services",
    )

    # Logs command
    logs_parser = subparsers.add_parser(
        "logs",
        help="Display service logs",
    )

    logs_parser.add_argument(
        "--tail",
        type=int,
        default=100,
        help="Number of log lines to display (default: 100)",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "status":
        return show_status()

    if args.command == "deploy":
        return deploy()

    if args.command == "stop":
        return stop()

    if args.command == "logs":
        return show_logs(args.tail)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
