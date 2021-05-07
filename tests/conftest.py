import os
import subprocess
import uuid

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


def start_container():
    image_name = f"test-module-postgres-{uuid.uuid4()}"
    
    docker_build_cmd = ["sudo", "docker", "build", ".", "-t", image_name]

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
    print(f"Started container with id {container_id}")
    return container_id


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
