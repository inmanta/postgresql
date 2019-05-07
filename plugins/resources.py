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

import psycopg2

from inmanta.agent.handler import provider, CRUDHandler, ResourcePurged, HandlerContext
from inmanta.resources import Resource, resource, PurgeableResource

@resource("postgresql::Database", agent="server.host.name", id_attribute="db_name")
class Database(Resource):

    fields = ("db_name", "username", "purged", "purge_on_delete")

    @staticmethod
    def get_username(exp, obj):
        try:
            if not obj.owner.username:
                raise IgnoreResourceException()
        except Exception as e:
            raise IgnoreResourceException()
        return obj.owner.username



@provider("postgresql::Database", name="postgresql-database")
class DatabaseProvider(CRUDHandler):

    def read_resource(self, ctx: HandlerContext, resource: PurgeableResource) -> None:
        conn = psycopg2.connect("dbname='postgres' user='postgres'")
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{resource.db_name }'")
            rows = cur.fetchall()
            if not rows:
                raise ResourcePurged()
        finally:
            conn.close()

    def create_resource(self, ctx: HandlerContext, resource: PurgeableResource) -> None:
        conn = psycopg2.connect("dbname='postgres' user='postgres'")
        try:
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute(f"CREATE DATABASE { resource.db_name } WITH OWNER='{ resource.username }'")
        finally:
            conn.close()

    def delete_resource(self, ctx: HandlerContext, resource: PurgeableResource) -> None:
        pass

    def update_resource(self, ctx: HandlerContext, changes: dict, resource: PurgeableResource) -> None:
        pass

@resource("postgresql::User", agent="server.host.name", id_attribute="username")
class User(Resource):

    fields = ("username", "password", "purged", "purge_on_delete")


@provider("postgresql::User", name="postgresql-user")
class UserProvider(CRUDHandler):

    def read_resource(self, ctx: HandlerContext, resource: PurgeableResource) -> None:
        conn = psycopg2.connect("dbname='postgres' user='postgres'")
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT 1 FROM pg_user WHERE usename = '{ resource.username }'")
            rows = cur.fetchall()
            if not rows:
                raise ResourcePurged()
        finally:
            conn.close()

    def create_resource(self, ctx: HandlerContext, resource: PurgeableResource) -> None:
        conn = psycopg2.connect("dbname='postgres' user='postgres'")
        try:
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute(f"CREATE USER { resource.username } WITH PASSWORD '{ resource.password }'")
        finally:
            conn.close()

    def delete_resource(self, ctx: HandlerContext, resource: PurgeableResource) -> None:
        pass

    def update_resource(self, ctx: HandlerContext, changes: dict, resource: PurgeableResource) -> None:
        pass
