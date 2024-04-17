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

from tornado import ioloop

from inmanta import const
from inmanta.agent import cache, handler
from inmanta.agent.handler import HandlerContext
from inmanta.export import cfg_env


class MockProcess(object):
    """
    A mock agentprocess
    """

    def __init__(self):
        self._io_loop = ioloop.IOLoop.current()


class MockAgent(object):
    """
    A mock agent for unit testing
    """

    def __init__(self, uri):
        self.uri = uri
        self.process = MockProcess()
        self._env_id = cfg_env.get()
        # This is for the new agent api in inmanta.agent.executor.AgentInstance
        self.eventloop = self.process._io_loop


def get_handler(project, resource, remote):
    c = cache.AgentCache()
    agent = MockAgent(f"ssh://{remote}")

    c.open_version(resource.id.version)
    try:
        p = handler.Commander.get_provider(c, agent, resource)
        p.set_cache(c)
        p.get_file = lambda x: project.get_blob(x)
        p.stat_file = lambda x: project.stat_blob(x)
        p.upload_file = lambda x, y: project.add_blob(x, y)
        p.run_sync = ioloop.IOLoop.current().run_sync

        return p
    except Exception as e:
        raise e


def dryrun(project, pg_url, resource):
    return deploy(project, pg_url, resource, True)


def deploy(
    project, pg_url, resource, dryrun=False, status=const.ResourceState.deployed
):
    handler = get_handler(project, resource, pg_url)
    ctx = HandlerContext(resource)
    handler.execute(ctx, resource, dryrun)
    project.finalize_context(ctx)
    if dryrun:
        assert ctx.status == const.ResourceState.dry
    else:
        assert ctx.status == status
    return ctx.changes
