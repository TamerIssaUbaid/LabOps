from pathlib import Path
import subprocess


class AnsibleUnavailableError(Exception):
    """Raised when Ansible is not installed or unavailable."""


class AnsibleExecutionError(Exception):
    """Raised when an Ansible playbook execution fails."""


def run_playbook(playbook, timeout=300):
    project_dir = Path(__file__).resolve().parents[3]
    ansible_dir = project_dir / "automation" / "ansible"

    try:
        result = subprocess.run(
            [
                "ansible-playbook",
                f"playbooks/{playbook}.yml",
            ],
            cwd=ansible_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

    except FileNotFoundError:
        raise AnsibleUnavailableError(
            "Ansible executable was not found."
        )

    except subprocess.TimeoutExpired:
        raise AnsibleExecutionError(
            "Ansible playbook execution timed out."
        )

    if result.returncode != 0:
        output = "\n".join(
            part for part in (result.stdout, result.stderr) if part
        )

        raise AnsibleExecutionError(
            output or "Ansible playbook execution failed."
        )

    return result
