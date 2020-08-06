from common import deploy, dryrun


def test_db(project, pg_url):

    # Create

    project.compile(
        """
    import postgresql
    import ip

    host = ip::Host(name="test", ip="10.0.0.1", os=std::linux)

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

    host = ip::Host(name="test", ip="10.0.0.1", os=std::linux)

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

    host = ip::Host(name="test", ip="10.0.0.1", os=std::linux)

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
