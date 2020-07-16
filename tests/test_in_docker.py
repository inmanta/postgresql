import os
import subprocess

import pytest


@pytest.mark.skipif(
    not os.getenv("INMANTA_TEST_INFRA_SETUP", "false").lower() == "true",
    reason="Only run when test infra environment variable is set to true",
)
def test_docker(docker_container):
    print(f"Running tests in container {docker_container}")
    subprocess.run(
        [
            "sudo",
            "docker",
            "exec",
            f"{docker_container}",
            "env/bin/pytest",
            "tests/",
            "-v",
            "-s",
            "--log-cli-level",
            "DEBUG",
            "--junitxml=junit.xml",
        ],
        check=True,
    )
