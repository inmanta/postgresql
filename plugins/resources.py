"""
    Copyright 2019 Inmanta
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

from inmanta.agent.handler import provider, CRUDHandler, ResourcePurged, HandlerContext
from inmanta.resources import Resource, resource, PurgeableResource

@resource("postgresql::Database", agent="server.host.name", id_attribute="db_name")
class Database(PurgeableResource):

    fields = ("db_name", "owner", "purged", "purge_on_delete")

    @staticmethod
    def get_owner(exp, obj):
        try:
            if not obj.owner.username:
                raise IgnoreResourceException()
        except Exception as e:
            raise IgnoreResourceException()
        return obj.owner.username


class PSQLProvider(CRUDHandler):

    def execute_sql(self, ctx: HandlerContext, cmd:str):
        cmd = ["-u", "postgres", "--", "psql", "-q", "-t", "-A", "-z", "-c", cmd]
        out, err, code = self._io.run("sudo", cmd, cwd="/")
        ctx.info("ran command sudo %(cmd)s, return code %(code)d", cmd = cmd, code=code, out=out, err=err)
        if code != 0:
            raise Exception("Command returned non zero exit code\n" +  err)
        return [record for record in (line.split('\0') for line in out.split("\n") if line) if record]



@provider("postgresql::Database", name="postgresql-database")
class DatabaseProvider(PSQLProvider):

    def read_resource(self, ctx: HandlerContext, resource: PurgeableResource) -> None:
        results = self.execute_sql(ctx, f"SELECT pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname = '{resource.db_name }'")
        if not results:
            raise ResourcePurged()
        if not len(results) == 1:
            raise Exception("Found multiple databases with the same name")
        rec = results[0]
        resource.owner = rec[0]
        

    def create_resource(self, ctx: HandlerContext, resource: PurgeableResource) -> None:
        self.execute_sql(ctx, f"CREATE DATABASE { resource.db_name } WITH OWNER='{ resource.owner }'")

    def delete_resource(self, ctx: HandlerContext, resource: PurgeableResource) -> None:
        self.execute_sql(ctx, f"DROP DATABASE { resource.db_name }")

    def update_resource(self, ctx: HandlerContext, changes: dict, resource: PurgeableResource) -> None:
         self.execute_sql(ctx, f"ALTER DATABASE { resource.db_name } OWNER TO { resource.owner }")


@resource("postgresql::User", agent="server.host.name", id_attribute="username")
class User(PurgeableResource):

    fields = ("username", "password", "purged", "purge_on_delete")


@provider("postgresql::User", name="postgresql-user")
class UserProvider(PSQLProvider):

    def read_resource(self, ctx: HandlerContext, resource: PurgeableResource) -> None:
        records = self.execute_sql(ctx, f"SELECT 1 FROM pg_user WHERE usename = '{ resource.username }'")
        if not records:
            raise ResourcePurged()

    def create_resource(self, ctx: HandlerContext, resource: PurgeableResource) -> None:
        self.execute_sql(ctx, f"CREATE USER { resource.username } WITH PASSWORD '{ resource.password }'")

    def delete_resource(self, ctx: HandlerContext, resource: PurgeableResource) -> None:
        self.execute_sql(ctx, f"DROP USER { resource.username }")

    def update_resource(self, ctx: HandlerContext, changes: dict, resource: PurgeableResource) -> None:
        raise Exception("Not supported")
