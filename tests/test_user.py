from common import deploy, dryrun


def test_user(project, pg_url):

    project.compile(
        f"""
    import postgresql
    import ip

    host = ip::Host(name="test", ip="10.0.0.1", os=std::linux)

    server = postgresql::PostgresqlServer(host=host, managed=false)

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

    host = ip::Host(name="test", ip="10.0.0.1", os=std::linux)

    server = postgresql::PostgresqlServer(host=host, managed=false)

    user2=postgresql::User(username="test",password="test", server=server, purged=true)


    """
    )
    user2 = project.get_resource("postgresql::User", username="test")
    c1 = dryrun(project, pg_url, user2)
    assert "purged" in c1
    deploy(project, pg_url, user2)
    c1 = dryrun(project, pg_url, user2)
    assert not c1
