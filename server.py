#!/usr/bin/env python3
# -*- encoding: utf-8
# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 12020 - 12022 HE, Emporia.AI Pte Ltd

__banner__ = """













""" # __banner__

import globals

from hypercorn.trio import serve
from hypercorn.config import Config

from quart_trio import QuartTrio
from quart_schema import QuartSchema

from common.computersays import ComputerSays

from pathlib import Path

from eliot import start_action, to_file

cs = ComputerSays()

cs.load("redis_cfg", """

```

'01FDDZG5XXMG0GF1MHYXEMX00Z id

'127.0.0.1 'host !

""")

print(cs.redis_cfg["host"])

app = QuartTrio("EMPORIA-AI-ENGINE")
QuartSchema(app, version="0.42.10", title="")

import routes.engine
app.register_blueprint(routes.engine.blueprint)

import routes.manage
app.register_blueprint(routes.manage.blueprint)

import routes.locate
app.register_blueprint(routes.locate.blueprint)

import routes.value
app.register_blueprint(routes.value.blueprint)

import routes.alter
app.register_blueprint(routes.alter.blueprint)

import routes.genre
app.register_blueprint(routes.genre.blueprint)

import routes.space
app.register_blueprint(routes.space.blueprint)

import routes.thing
app.register_blueprint(routes.thing.blueprint)

import routes.where
app.register_blueprint(routes.where.blueprint)

import routes.broker
app.register_blueprint(routes.broker.blueprint)

import routes.keeper
app.register_blueprint(routes.keeper.blueprint)


from objects.engine import *

async def app_worker():

    while True:

        running_version = persist_running.version

        globals.engines.clear(); globals.handles.clear()

        for id, space in persist_running.spaces.items():
            globals.engines[id] = Engine(**space)

        if len(globals.engines):
            async with trio.open_nursery() as nursery:
                for id, engine in globals.engines.items():
                    nursery.start_soon(engine.maintain)

        else:
            # idle when there are no running engines
            await trio.sleep(0.2)

        if persist_staging.version != running_version:
            persist_running.clone(persist_staging, require_verification=False)


async def app_serve(*args, **kw):
    async with trio.open_nursery() as nursery:
        nursery.start_soon(serve, *args)
        nursery.start_soon(app_worker)

cs.load("hypercorn_cfg", """

```

'01FEPGEGR1F85ED0TMQKRWK00Z id

'0.0.0.0:10000 'ENGINE_BIND os_getenv 'bind !

""")

config = Config()
config.bind = [cs.hypercorn_cfg['bind']]

if 1:
    i = 5
    from pathlib import Path
    p = Path(f"server_{i}.log");
    if p.exists(): p.unlink()
    i -= 1
    while i >= 0:
        p = Path(f"server_{i}.log")
        if p.exists():
            p.rename(Path(f"server_{i+1}.log"))
        i -= 1

to_file(open("server_0.log", "w"))

trio.run(app_serve, app, config)







