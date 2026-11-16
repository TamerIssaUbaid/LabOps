
from pathlib import Path
import subprocess


class DockerUnavailableError(Exception):
    """Raised when Docker Engine is unavailable."""


class DockerCommandError(Exception):
    """Raised when a Docker operation fails."""


def _run_compose(*arguments, timeout=60):
    project_dir = Path(__file__).resolve().parents[3]
    compose_file = project_dir / "infrastructure" / "docker" / "compose.yaml"

    command = [
        "docker",
        "compose",
        "--project-directory",
        str(project_dir),
        "-f",
        str(compose_file),
        *arguments,
    ]

    try:
        result = subprocess.run(
            command,
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

    except FileNotFoundError:
        raise DockerUnavailableError("Docker CLI was not found.")

    except subprocess.TimeoutExpired:
        raise DockerCommandError("Docker command timed out.")

    if result.returncode != 0:
        raise DockerCommandError(
            result.stderr.strip() or "Docker operation failed."
        )

    return result


def get_docker_status():
    try:
        engine = subprocess.run(
            ["docker", "info", "--format", "{{.ServerVersion}}"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        if engine.returncode != 0:
            raise DockerUnavailableError(
                engine.stderr.strip() or "Docker Engine is unavailable."
            )

        containers = subprocess.run(
            [
                "docker",
                "ps",
                "-a",
                "--filter",
                "label=com.docker.compose.project=labops",
                "--format",
                "{{.Names}}\t{{.Status}}",
            ],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        if containers.returncode != 0:
            raise DockerUnavailableError(containers.stderr.strip())

    except FileNotFoundError:
        raise DockerUnavailableError("Docker CLI was not found.")

    except subprocess.TimeoutExpired:
        raise DockerUnavailableError("Docker command timed out.")

    container_list = []

    for line in containers.stdout.splitlines():
        name, status = line.split("\t", maxsplit=1)
        container_list.append({
            "name": name,
            "status": status,
        })

    return {
        "engine_version": engine.stdout.strip(),
        "containers": container_list,
    }


def stop_services():
    return _run_compose("stop", timeout=120)


def get_service_logs(tail=100):
    if tail < 1:
        raise DockerCommandError("Log line count must be greater than zero.")

    return _run_compose(
        "logs",
        "--tail",
        str(tail),
        timeout=30,
    )
