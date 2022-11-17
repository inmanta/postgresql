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


def test_db(project, pg_url):

    # Create

    project.compile(
        """
    import postgresql
    import ip

    host = ip::Host(name="test", ip="10.0.0.1", os=std::OS(name="fq-python-linux", python_cmd="python3", family=std::linux))

    server = postgresql::PostgresqlServer(host=host, managed=false)

    user=postgresql::User(username="postgres",password="test", server=server)

    db = postgresql::Database(server=server, db_name="testdb", owner=user)

    """
    )
    resource = project.get_resource("postgresql::Database")

    # Dryrun: changes
    c1 = dryrun(project, pg_url, resource)
    assert "purged" in c1

    # Deploy
    deploy(project, pg_url, resource)

    # Dryrun: no changes
    c1 = dryrun(project, pg_url, resource)
    assert not c1

    # Update owner

    project.compile(
        """
    import postgresql
    import ip

    host = ip::Host(name="test", ip="10.0.0.1", os=std::OS(name="fq-python-linux", python_cmd="python3", family=std::linux))

    server = postgresql::PostgresqlServer(host=host, managed=false)

    user=postgresql::User(username="testuserx",password="test", server=server)

    db = postgresql::Database(server=server, db_name="testdb", owner=user)

    """
    )

    resource = project.get_resource("postgresql::Database")
    c1 = dryrun(project, pg_url, resource)
    assert "owner" in c1

    # make user
    user = project.get_resource("postgresql::User")
    deploy(project, pg_url, user)

    # Deploy
    deploy(project, pg_url, resource)

    # Dryrun: no changes
    c1 = dryrun(project, pg_url, resource)
    assert not c1

    # Delete

    project.compile(
        """
    import postgresql
    import ip

    host = ip::Host(name="test", ip="10.0.0.1", os=std::OS(name="fq-python-linux", python_cmd="python3", family=std::linux))

    server = postgresql::PostgresqlServer(host=host, managed=false)

    user=postgresql::User(username="postgres",password="test", server=server)

    db = postgresql::Database(server=server, db_name="testdb", owner=user, purged=true)

    """
    )
    resource = project.get_resource("postgresql::Database")
    c1 = dryrun(project, pg_url, resource)
    assert "purged" in c1
    deploy(project, pg_url, resource)
    c1 = dryrun(project, pg_url, resource)
    assert not c1
