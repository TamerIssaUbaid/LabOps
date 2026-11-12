import subprocess


class DockerUnavailableError(Exception):
    """Raised when Docker Engine is unavailable."""


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
