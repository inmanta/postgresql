import json
import os
import subprocess
import uuid
from pathlib import Path

from pytest import fixture


@fixture(scope="session", autouse=True)
def postgres_docker_container():
    # If "PG_TEST_HOST" is set, no need for a docker container
    if os.getenv("PG_TEST_HOST"):
        yield

    # Run before the other session-scoped fixtures, like the project_factory in pytest-inmanta
    image_name = f"test-module-postgres-{uuid.uuid4()}"
    subprocess.run(
        ["sudo", "docker", "build", ".", "-t", image_name,], check=True,
    )
    container_id = (
        subprocess.run(
            [
                "sudo",
                "docker",
                "run",
                "--privileged",
                "--expose=22",
                "--rm",
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
    subprocess.run(
        [
            "sudo",
            "docker",
            "cp",
            f"{Path.home()}/.ssh/id_rsa.pub",
            f"{container_id}:/root/.ssh/authorized_keys",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    subprocess.run(
        [
            "sudo",
            "docker",
            "exec",
            container_id,
            "chown",
            "root.",
            "/root/.ssh/authorized_keys",
        ],
        check=True,
    )
    yield container_id
    subprocess.run(["sudo", "docker", "stop", container_id], check=True)


@fixture
def pg_host(postgres_db, postgres_docker_container):
    if os.getenv("PG_TEST_HOST"):
        return os.getenv("PG_TEST_HOST")
    inspect_output = (
        subprocess.run(
            ["sudo", "docker", "inspect", postgres_docker_container],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        .stdout.decode("utf-8")
        .strip()
    )
    ipadress = json.loads(inspect_output)[0]["NetworkSettings"]["Networks"]["bridge"][
        "IPAddress"
    ]
    return ipadress


@fixture
def pg_host_user(postgres_db):
    return os.getenv("PG_TEST_HOST_USER") or "root"


@fixture
def pg_host_line(pg_host, pg_host_user):
    return f"""ip::Host(name="testhost", ip="{pg_host}", remote_agent=true,  remote_user={pg_host_user})"""


@fixture
def pg_url(pg_host, pg_host_user):
    return f"""{pg_host_user}@{pg_host}"""
