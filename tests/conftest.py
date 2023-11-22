"""
    Copyright 2022 Inmanta

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Contact: code@inmanta.com
"""
import os
import subprocess
import time
import uuid
import sys

import pytest
from pytest import fixture

collect_ignore = []
if os.getenv("INMANTA_TEST_INFRA_SETUP", "false").lower() == "true":
    # If the INMANTA_TEST_INFRA_SETUP is on, ignore the tests when running outside of docker except the "test_in_docker" one.
    # That test executes the rest of the tests inside a docker container
    # (and skips itself, because the environment variable will be off in the container).
    test_dir = os.path.dirname(os.path.realpath(__file__))
    test_modules = [
        module for module in os.listdir(test_dir) if "test_in_docker" not in module
    ]

    collect_ignore += test_modules


@pytest.fixture(scope="function")
def docker_container() -> None:
    container_id = start_container()
    yield container_id
    stop_container(container_id)


def start_container(pg_version: int = 10):
    image_name = f"test-module-postgres-{uuid.uuid4()}"

    docker_build_cmd = ["sudo", "docker", "build", ".", "-t", image_name]
    docker_build_cmd.append("--build-arg")
    docker_build_cmd.append(f"PG_MAJOR_VERSION={pg_version}")

    # Set PYTHON_VER build argument
    python_version='.'.join([str(part) for part in sys.version_info[0:3]])
    docker_build_cmd.append("--build-arg")
    docker_build_cmd.append(f"PYTHON_VER={python_version}")

    pip_index_url = os.environ.get("PIP_INDEX_URL", None)
    if pip_index_url is not None:
        docker_build_cmd.append("--build-arg")
        docker_build_cmd.append(f"PIP_INDEX_URL={pip_index_url}")
    pip_pre = os.environ.get("PIP_PRE", None)
    if pip_pre is not None:
        docker_build_cmd.append("--build-arg")
        docker_build_cmd.append(f"PIP_PRE={pip_pre}")

    subprocess.run(
        docker_build_cmd,
        check=True,
    )
    container_id = (
        subprocess.run(
            [
                "sudo",
                "docker",
                "run",
                "--rm",
                "-e",
                f"POSTGRES_PASSWORD={uuid.uuid4()}",
                "-d",
                image_name,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        .stdout.decode("utf-8")
        .strip()
    )
    wait_until_postgresql_process_is_up(container_id)
    print(f"Started container with id {container_id}")
    return container_id


def wait_until_postgresql_process_is_up(docker_container) -> None:
    """
    Execute a busy wait until the PostgreSQL process has finished starting.
    An exception is raised after 30 failed is ready checks.
    """
    retries = 30
    while retries > 0:
        try:
            subprocess.run(
                [
                    "sudo",
                    "docker",
                    "exec",
                    f"{docker_container}",
                    "pg_isready",
                ],
                check=True,
            )
        except subprocess.CalledProcessError:
            retries -= 1
            time.sleep(1)
        else:
            return
    raise Exception("Timeout while waiting for PostgreSQL server to start")


def stop_container(container_id: str):
    subprocess.run(
        [
            "sudo",
            "docker",
            "cp",
            f"{container_id}:/module/postgresql/junit.xml",
            "junit_docker.xml",
        ],
        check=True,
    )
    no_clean = os.getenv("INMANTA_NO_CLEAN", "false").lower() == "true"
    print(f"Skipping cleanup: {no_clean}")
    if not no_clean:
        subprocess.run(["sudo", "docker", "stop", f"{container_id}"], check=True)


@fixture(scope="function")
def pg_host():
    yield os.getenv("PG_TEST_HOST", "localhost")


@fixture
def pg_host_user():
    return os.getenv("PG_TEST_HOST_USER", "root")


@fixture
def pg_host_line(pg_host, pg_host_user):
    return f"""ip::Host(name="testhost", ip="{pg_host}", remote_agent=true,  remote_user={pg_host_user})"""


@fixture
def pg_url(pg_host, pg_host_user):
    return f"""{pg_host_user}@{pg_host}"""


@fixture
def pg_version_fallback():
    """Default to this Major Postgres version for tests running outside of a docker container
    if the PG_MAJOR_VERSION env variable is not set"""
    return 10
