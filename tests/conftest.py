import json
import os
import subprocess
import uuid
from pathlib import Path

from pytest import fixture


def start_container():
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
    return container_id


def stop_container(container_id: str):
    subprocess.run(["sudo", "docker", "stop", container_id], check=True)


def get_ip_of_container(container_id):
    inspect_output = (
        subprocess.run(
            ["sudo", "docker", "inspect", container_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        .stdout.decode("utf-8")
        .strip()
    )
    ip_address = json.loads(inspect_output)[0]["NetworkSettings"]["Networks"]["bridge"][
        "IPAddress"
    ]
    return ip_address


# Run before the other session-scoped fixtures, like the project_factory in pytest-inmanta
@fixture(scope="session", autouse=True)
def pg_host():
    # If "PG_TEST_HOST" is set, no need for a docker container
    if os.getenv("PG_TEST_HOST"):
        yield os.getenv("PG_TEST_HOST")
    else:
        container_id = start_container()
        ip_address = get_ip_of_container(container_id)
        yield ip_address
        stop_container(container_id)


@fixture
def pg_host_user():
    return os.getenv("PG_TEST_HOST_USER", "root")


@fixture
def pg_host_line(pg_host, pg_host_user):
    return f"""ip::Host(name="testhost", ip="{pg_host}", remote_agent=true,  remote_user={pg_host_user})"""


@fixture
def pg_url(pg_host, pg_host_user):
    return f"""{pg_host_user}@{pg_host}"""
