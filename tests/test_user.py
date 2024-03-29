"""
    Copyright 2020 Inmanta

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

from common import deploy, dryrun


def test_user(project, pg_url, pg_version_fallback):
    project.compile(
        f"""
    import postgresql
    import ip
    import std

    host = ip::Host(name="test", ip="10.0.0.1", os=std::linux)
    pg_version=std::get_env_int("PG_MAJOR_VERSION", {pg_version_fallback})
    server = postgresql::PostgresqlServer(host=host, managed=false, pg_version=pg_version)

    user=postgresql::User(username="postgres",password="test", server=server)
    user2=postgresql::User(username="test",password="test", server=server)


    """
    )
    user = project.get_resource("postgresql::User", username="postgres")
    user2 = project.get_resource("postgresql::User", username="test")

    c1 = dryrun(project, pg_url, user)
    assert "purged" not in c1
    assert not c1
    c1 = dryrun(project, pg_url, user2)
    assert "purged" in c1

    deploy(project, pg_url, user2)
    c1 = dryrun(project, pg_url, user2)
    assert not c1

    project.compile(
        f"""
    import postgresql
    import ip
    import std

    host = ip::Host(name="test", ip="10.0.0.1", os=std::linux)

    pg_version=std::get_env_int("PG_MAJOR_VERSION", {pg_version_fallback})

    server = postgresql::PostgresqlServer(host=host, managed=false, pg_version=pg_version)

    user2=postgresql::User(username="test",password="test", server=server, purged=true)


    """
    )
    user2 = project.get_resource("postgresql::User", username="test")
    c1 = dryrun(project, pg_url, user2)
    assert "purged" in c1
    deploy(project, pg_url, user2)
    c1 = dryrun(project, pg_url, user2)
    assert not c1
