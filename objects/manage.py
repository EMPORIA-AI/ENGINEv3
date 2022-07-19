#!/usr/bin/env python3
# -*- encoding: utf-8
# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 12020 - 12022 HE, Emporia.AI Pte Ltd

__banner__ = """













""" # __banner__

import globals, json, copy
from common import *
from ulid import ULID
from objects.persist import *
from quart import abort
from icecream import ic

class singleton_Manage:

    def __init__(self, db, **kw):
        self.db = db

        self.fields = {}
        self.fields['value'] = list(Where().schema()["properties"].keys())
        self.fields['genre'] = list(Genre().schema()["properties"].keys())
        self.fields['where'] = list(Where().schema()["properties"].keys())
        self.fields['space'] = list(Space().schema()["properties"].keys())
        self.fields['thing'] = list(Thing().schema()["properties"].keys())
        self.fields['alter'] = list(Alter().schema()["properties"].keys())
        self.fields['broker'] = list(Broker().schema()["properties"].keys())
        self.fields['keeper'] = list(Keeper().schema()["properties"].keys())

    async def manage_OBJECTS(self, action, database, otype, objects, **kw):
        result = {}
        results = []

        if objects == None:
            return (None, result)

        cleanup = []
        for object in objects:
            if object.id == "": continue
            cleanup.append(object)
        objects = cleanup

        factory = database.factory

        if action['mode'] == 'search':

            return object.find(action, database, factory, otype, objects)

        elif action['mode'] == 'ids':
            for key in database.keys():
                results.append(factory(id=key))

        ### GET: read data from your API
        elif action['mode'] == 'get':

            args = action.get("args", {})
            full = args.get("full", 1)

            # the client only wants some of the fields
            if 'fields' in action:

                if action['fields'] == '*':
                    fields = self.fields[otype]
                else:
                    fields = []
                    for field in action['fields']:
                        if field in self.fields[otype]:
                            fields.append(field)

                # all objects, selected fields
                if objects[0].id == '*':
                    for key in database.keys():
                        object = database[key]
                        values = {}
                        for field in fields:
                            values[field] = object[field]
                        results.append(factory(**values))

                # selected objects, selected fields
                else:
                    for object in objects:
                        object = database[object.id]
                        values = {}
                        for field in fields:
                            values[field] = object[field]
                        results.append(factory(**values))

            else:

                # simpler path, all values on all or selected keys
                if objects[0].id == '*':
                    for key in database.keys():
                        results.append(database[key])
                else:
                    for object in objects:
                        results.append(database[object.id])

                if not full:
                    for object in results:
                        object.program = ""
                        object.storage = ""


        ### POST: add new data to your API
        elif action['mode'] == 'post' or action['mode'] == 'new':
            proto = factory()
            for object in objects:
                if object.id == "!":
                    id = str(ULID())[:-2] + '0' + proto.get_letter()
                    while persist.id_exists(id):
                        id = str(ULID())[:-2] + '0' + proto.get_letter()
                        # and buy a lottery ticket!
                    object.id = id
                database[object.id] = object
                results.append(factory(id=object.id, name="", tags=""))

        ### PUT: update existing data with your API
        elif action['mode'] == 'put':
            for object in objects:
                o = database[object.id]
                for field in self.fields[otype]:
                    o[field] = getattr(object, field)
                database[object.id] = o

        ### PATCH: updates a subset of existing data with your API
        elif action['mode'] == 'patch':
            for object in objects:
                o = database[object.id]
                for field in self.fields[otype]:
                    value = getattr(object, field)
                    if value == "": continue
                    value = "" if value == "<<<NONE>>>" else value
                    o[field] = value
                database[object.id] = o

        ### DELETE: remove data (usually a single resource) from your API
        elif action['mode'] == 'delete':
            for object in objects:
                if object.id == "": continue
                if object.id == "*":
                    if not action.get("args", {}).get("confirm", "") == "YES":
                        abort(403)
                    database.clear()
                else:
                    del database[object.id]

        return (results, result)

    async def manage_GLOBAL(self, action):
        result = {}

        for mode in action["mode"].split(";"):

            if mode == "verify_and_commit":

                running_version = persist_running.get_version()
                if persist.get_version() == running_version:
                    return result

                issues = persist.verify()
                assert issues == []
                persist_staging.clone(persist)

                while not persist_staging.get_version() == persist_running.get_version():
                    await trio.sleep(0.07)

            elif mode == "touch":
                persist.touch()

            elif mode == "verify":
                result["issues"] = persist.verify()

            elif mode == "commit":
                persist_staging.clone(persist)

            elif mode == "backup":
                persist_backups.clone(persist)

            elif mode == "restore_latest":
                persist.clone(persist_backups)

            elif mode == "step":

                current = {}
                for id, engine in globals.engines.items():
                    current[id] = engine.phase

                for id, engine in globals.engines.items():
                    engine.phase_next()

                pending = True
                while pending:
                    await trio.sleep(0.007)
                    pending = False
                    for id, phase in current.items():
                        if phase == globals.engines[id].phase:
                            pending = True

        return result

    async def route_MANAGE(self, data: Manage_DATA, **kw) -> Manage:
        args = {}

        args["result"] = await self.manage_GLOBAL(data.action)


        #
        # TODO: now the persist object has the factory refactor these calls
        #

        param = [data.action, storage.things, 'thing', data.things]
        args['things'], result = await self.manage_OBJECTS(*param)
        for k, v in result.items(): args["result"][k] = v

        param = [data.action, persist.values, 'value', data.values]
        args['values'], result = await self.manage_OBJECTS(*param)
        for k, v in result.items(): args["result"][k] = v

        param = [data.action, persist.genres, 'genre', data.genres]
        args['genres'], result = await self.manage_OBJECTS(*param)
        for k, v in result.items(): args["result"][k] = v

        param = [data.action, persist.wheres, 'where', data.wheres]
        args['wheres'], result = await self.manage_OBJECTS(*param)
        for k, v in result.items(): args["result"][k] = v

        param = [data.action, persist.spaces, 'space', data.spaces]
        args['spaces'], result = await self.manage_OBJECTS(*param)
        for k, v in result.items(): args["result"][k] = v

        param = [data.action, persist.alters, 'alter', data.alters]
        args['alters'], result = await self.manage_OBJECTS(*param)
        for k, v in result.items(): args["result"][k] = v

        param = [data.action, persist.brokers, 'broker', data.brokers]
        args['brokers'], result = await self.manage_OBJECTS(*param)
        for k, v in result.items(): args["result"][k] = v

        param = [data.action, persist.keepers, 'keeper', data.keepers]
        args['keepers'], result = await self.manage_OBJECTS(*param)
        for k, v in result.items(): args["result"][k] = v

        return Manage(**args)

singleton_manage = singleton_Manage(persist)

