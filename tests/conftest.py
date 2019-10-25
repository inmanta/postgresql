from pytest import fixture
import os

@fixture
def pg_host():
    return os.environ["PG_TEST_HOST"]


@fixture
def pg_host_user():
    return os.environ["PG_TEST_HOST_USER"]


@fixture
def pg_host_line(pg_host, pg_host_user):
    return f"""ip::Host(name="testhost", ip="{pg_host}", remote_agent=true,  remote_user={pg_host_user})"""

@fixture
def pg_url(pg_host, pg_host_user):
    return f"""{pg_host_user}@{pg_host}"""
