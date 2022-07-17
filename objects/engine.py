#!/usr/bin/env python3
# -*- encoding: utf-8
# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 12020 - 12022 HE, Emporia.AI Pte Ltd

__banner__ = """













""" # __banner__

import globals, os, re, sys, rich, trio, toml, json, pendulum, hashlib
from common import *
from objects.locate import *
from cubed4th import FORTH
from eliot import start_action, write_traceback

class Engine:

    def __init__(self, name, **kw):

        self.name = name

        for k, v in kw.items():
            self.__dict__[k] = v

        self.batches = {}
        self.h_batch = {}

        self.manual = False # is the engine in automatic or manual (test) mode
        self.step = 0 # when in manual mode, incrementing this causes a phase change
        self.trace = True

        #self.targets = [0.060, 0.080, 0.100, 0.120, 0.220]
        self.targets = [0.000, 0.300, 0.350, 0.400, 0.450, 0.500]

        self.demand_abi = """

```

: abi drop ;

"""
        self.supply_abi = """

```

: abi drop ;

"""
        self.thing_abi = """

```

: abi drop ({}) 'choices ! ;

"""

    def phase_next(self):
        self.step = self.step + 1

    def phase_trace(self, ctx):
        if not self.trace: return

        ctx.log(message_type="settings", epoch=self.epoch.to_iso8601_string(), batchid=self.batchid)

        if self.manual:
            print(f"In Engine (MANUAL) {self.id}, {self.name} ({self.step}) Phase={self.phase}")
            return

        seconds = (pendulum.now("UTC") - self.epoch).total_seconds()

        print(f"In Engine (AUTO) {self.id}, {self.name} Phase={self.phase} {seconds}")

    async def maintain(self):

        self.step = 0
        self.phase = 0

        self.manual = False
        # TODO: factor this out for other engine settings
        if 'manual' in persist_running.values:
            self.manual = json.loads(persist_running.values["manual"]["storage"])

        running_version = persist_running.version

        if self.manual:

            while running_version == persist_staging.version:

                print(f"Running (MANUAL) {self.id}, {self.name}")

                for phase in range(0, 5):
                    self.phase = phase

                    with start_action(action_type="engine", phase=phase) as ctx:

                        if   phase == 0: await self.phase_0SETUP(ctx)
                        elif phase == 1: await self.phase_1ENTER(ctx)
                        elif phase == 2: await self.phase_2OFFER(ctx)
                        elif phase == 3: await self.phase_3THINK(ctx)
                        elif phase == 4: await self.phase_4LEAVE(ctx)

                        step = self.step
                        while step == self.step:
                            if phase == 0:
                                if not running_version == persist_staging.version:
                                    return
                            await trio.sleep(0.03)


        else:

            while running_version == persist_staging.version:

                for phase in range(0, 5):
                    self.phase = phase

                    if phase == 1 and len(self.batch) == 0: break # nothing to do

                    with start_action(action_type="engine", phase=phase) as ctx:

                        # TODO: put this into a keyed dict of functions or getattr
                        if   phase == 0: await self.phase_0SETUP(ctx)
                        elif phase == 1: await self.phase_1ENTER(ctx)
                        elif phase == 2: await self.phase_2OFFER(ctx)
                        elif phase == 3: await self.phase_3THINK(ctx)
                        elif phase == 4: await self.phase_4LEAVE(ctx)

                        # figure out how long to sleep for the phase we are in
                        dwell = self.epoch.add(seconds=self.targets[phase+1])
                        dwell = dwell - pendulum.now("UTC")
                        dwell = dwell.total_seconds()

                        if dwell < 0:
                            print(f"phase = {phase}, dwell = {dwell}")
                            assert dwell >= 0

                        await trio.sleep(dwell)


    async def route_SETUP(self, data: Setup_DATA, **kw) -> Setup:

        result = Setup()

        if self.manual:
            assert self.phase == 0 # !for testing, not expected to be used in prod
        else:
            if not self.phase == 0:
                # called setup but the engine is in a different phase
                period = self.epoch.add(seconds=self.targets[-1]) - pendulum.now("UTC")
                result.dwell = period.total_seconds()
                result.clock = pendulum.now("UTC").to_iso8601_string()
                print("setup called while not in phase 0")
                print(result)
                return result

        result.handle = str(ULID())[:-3] + '0BH'

        with start_action(action_type="route_SETUP", batchid=result.handle) as ctx:

            data.trace(ctx)

            result.next = "1.ENTER"

            globals.handles[result.handle] = data.space_id
            self.batches[self.batchid]["handles"].append(result.handle)
            self.h_batch[result.handle] = self.batchid
            batch = self.batches[self.batchid]["batch"]
            batch[result.handle] = {"batchid":self.batchid, "setup":data}

            await trio.sleep(0)
            if not self.manual:
                period = self.epoch.add(seconds=self.targets[1]) - pendulum.now("UTC")
                result.dwell = period.total_seconds()
            result.clock = pendulum.now("UTC").to_iso8601_string()

            result.trace(ctx)

        return result

    async def route_ENTER(self, data: Enter_DATA, **kw) -> Enter:

        if self.manual:
            assert self.phase == 1
        else:
            if not self.phase == 1:
                print(f"!!!! route_ENTER called && phase = {self.phase}")
            pass

        batch = self.batches[self.h_batch[data.handle]]["batch"]
        batch[data.handle]["enter"] = data

        result = Enter()

        await trio.sleep(0)
        if not self.manual:
            period = self.epoch.add(seconds=self.targets[2]) - pendulum.now("UTC")
            result.dwell = period.total_seconds()
        result.clock = pendulum.now("UTC").to_iso8601_string()
        return result

    async def route_OFFER(self, data: Offer_DATA, **kw) -> Offer:

        if self.manual:
            assert self.phase == 2
        else:
            if not self.phase == 2:
                print(f"!!!! route_OFFER called && phase = {self.phase}")
            pass

        batchid = self.h_batch[data.handle]

        result = Offer()

        with start_action(action_type="route_OFFER", batchid=batchid) as ctx:

            data.trace(ctx)

            valid = True

            if data.supply:
                for supply in data.supply:
                    forth = FORTH.Engine(run=self.supply_abi, sandbox=3)
                    try:
                        forth.execute(supply.program)
                    except:
                        write_traceback()
                        valid = False
                        break

            if data.demand:
                for demand in data.demand:
                    forth = FORTH.Engine(run=self.demand_abi, sandbox=3)
                    try:
                        forth.execute(demand.program)
                    except:
                        write_traceback()
                        valid = False
                        break

            if not valid:
                abort(403)

            batch = self.batches[batchid]["batch"]
            batch[data.handle]["offer"] = data

            await trio.sleep(0)
            if not self.manual:
                period = self.epoch.add(seconds=self.targets[3]) - pendulum.now("UTC")
                result.dwell = period.total_seconds()
            result.clock = pendulum.now("UTC").to_iso8601_string()

        return result

    async def route_THINK(self, data: Think_DATA, **kw) -> Think:

        if self.manual:
            assert self.phase == 3
        else:
            if not self.phase == 3:
                print(f"!!!! route_THINK called && phase = {self.phase}")
            pass

        batch = self.batches[self.h_batch[data.handle]]["batch"]
        batch[data.handle]["think"] = data

        result = Think()

        await trio.sleep(0)
        if not self.manual:
            period = self.epoch.add(seconds=self.targets[4]) - pendulum.now("UTC")
            result.dwell = period.total_seconds()
        result.clock = pendulum.now("UTC").to_iso8601_string()
        return result

    async def route_LEAVE(self, data: Leave_DATA, **kw) -> Leave:

        if self.manual:
            assert self.phase == 4
        else:
            if not self.phase == 4:
                print(f"!!!! route_LEAVE called && phase = {self.phase}")
            pass

        batchid = self.h_batch[data.handle]

        epoch = self.batches[batchid]["epoch"]
        batch = self.batches[batchid]["batch"]
        matches = self.batches[batchid]["matches"]

        result = Leave()

        with start_action(action_type="route_LEAVE", batchid=batchid) as ctx:

            data.trace(ctx)

            offer = batch[data.handle].get("offer", None)
            if offer == None:
                await trio.sleep(0)
                if not self.manual:
                    period = self.epoch.add(seconds=self.targets[5]) - pendulum.now("UTC")
                    result.dwell = period.total_seconds()
                result.clock = pendulum.now("UTC").to_iso8601_string()
                return result

            demand_ids = {}
            if not offer.demand == None:
                for demand in offer.demand:
                    demand_ids[demand.id] = True

            supply_ids = {};
            if not offer.supply == None:
                for supply in offer.supply:
                    supply_ids[supply.id] = True

            for thing, supply, demand, choices in matches:
                await trio.sleep(0)
                if not (supply.id in supply_ids or demand.id in demand_ids):
                    continue

                settle = Settle()
                settle.thing = thing
                settle.supply = supply
                settle.demand = demand
                settle.choices = choices
                settle.alters = []

                if demand.id in demand_ids: del demand_ids[demand.id]
                if supply.id in supply_ids: del supply_ids[supply.id]

                if result.settle == None:
                    result.settle = []
                result.settle.append(settle)

            if not self.manual:
                period = epoch.add(seconds=self.targets[-1]) - pendulum.now("UTC")
                result.dwell = period.total_seconds()
            result.clock = pendulum.now("UTC").to_iso8601_string()

            result.trace(ctx)

        return result


    async def phase_0SETUP(self, ctx):

        self.epoch = pendulum.now("UTC")

        self.batchid = str(ULID())[:-2] + '0B'

        self.batches[self.batchid] = {"batch":{}, "handles":[], "matches":[]}
        self.batches[self.batchid]["epoch"] = self.epoch

        self.batch = self.batches[self.batchid]["batch"]

        self.phase_trace(ctx)


    async def phase_1ENTER(self, ctx):

        self.phase_trace(ctx)

    async def phase_2OFFER(self, ctx):

        self.phase_trace(ctx)

    async def phase_3THINK(self, ctx):

        self.phase_trace(ctx)

        matches = self.batches[self.batchid]["matches"]

        supply_dicts = []; demand_dicts = []
        for k, data in self.batch.items():
            if not "offer" in data: continue
            if data["offer"].supply:
                for v in data["offer"].supply:
                    supply_dicts.append({"object":v})

            if data["offer"].demand:
                for v in data["offer"].demand:
                    demand_dicts.append({"object":v})

        if len(supply_dicts) == 0: return
        if len(demand_dicts) == 0: return

        def by_id(elem):
            return (elem["object"].id,)

        supply_dicts.sort(key=by_id)
        demand_dicts.sort(key=by_id)

        #
        stable_sort = []
        for obj in supply_dicts: stable_sort.append(obj["object"].id)
        for obj in demand_dicts: stable_sort.append(obj["object"].id)
        stable_sort = hashlib.sha256(";".join(stable_sort).encode("utf-8")).hexdigest()
        stable_sort = hashlib.sha256(stable_sort.encode("utf-8")).hexdigest()

        def by_price(elem):
            my_sort = elem["object"].id + stable_sort
            my_sort = hashlib.sha256(my_sort.encode("utf-8")).hexdigest()
            # TODO: deal with crossrates
            return (elem["object"].price.value,my_sort)

        supply_dicts.sort(key=by_price)
        demand_dicts.sort(key=by_price, reverse=True)

        for iter in supply_dicts:
            iter["buyer"] = None
            iter["forth"] = FORTH.Engine(run=self.supply_abi, sandbox=3)
            iter["forth"].execute(iter["object"].program)
            iter["forth"].save(save_stack=False)
            iter["thing"] = Thing(**storage.things[iter["object"].thing_id])
            iter["thing_forth"] = FORTH.Engine(run=self.thing_abi, sandbox=3)
            iter["thing_forth"].execute(iter["thing"].program)
            iter["thing_forth"].save(save_stack=False)

        for iter in demand_dicts:
            iter["seller"] = None
            iter["forth"] = FORTH.Engine(run=self.demand_abi, sandbox=3)
            iter["forth"].execute(iter["object"].program)
            iter["forth"].save(save_stack=False)

        supply_sold = {}
        demand_sold = {}

        for round in [1, 2, 3]:

            # these objects are only updated at the start of the round
            round_supply_sold = copy.copy(supply_sold)
            round_demand_sold = copy.copy(demand_sold)

            for demand in demand_dicts:

                for supply in supply_dicts:

                    # the thing has alreay been purchased
                    if demand["seller"] or supply["buyer"]:
                        continue

                    if demand["object"].price.value < supply["object"].price.value:
                        continue

                    demand_forth = demand["forth"]
                    demand_forth.load()
                    demand_forth.poke("round", round)
                    demand_forth.poke("sold", round_demand_sold)

                    supply_forth = supply["forth"]
                    supply_forth.load()
                    supply_forth.poke("round", round)
                    supply_forth.poke("sold", round_supply_sold)

                    thing_forth = supply["thing_forth"]
                    thing_forth.load()

                    if not "inspect-thing" in demand_forth.root.words:
                        print("inspect-thing not in root words!!!")
                        continue

                    demand_forth.poke("thing", thing_forth)
                    demand_forth.execute("inspect-thing", include=True)
                    if not demand_forth.peek("buy", False):
                        continue

                    choices = thing_forth.peek("choices", {})
                    if not isinstance(choices, dict):
                        continue

                    if "inspect-seller" in demand_forth.root.words:
                        demand_forth.poke("seller", supply_forth)
                        demand_forth.execute("inspect-seller", include=True)
                        if not demand_forth.peek("allow", True):
                            print("inspect-seller allow != True")
                            continue

                    if "inspect-buyer" in supply_forth.root.words:
                        supply_forth.poke("buyer", demand_forth)
                        supply_forth.execute("inspect-buyer", include=True)
                        if not supply_forth.peek("allow", True):
                            print("inspect-buyer allow != True")
                            continue

                    supply["buyer"] = demand
                    supply_sold[supply["object"].id] = True

                    demand["seller"] = supply
                    demand_sold[demand["object"].id] = True

                    match = (supply["thing"], supply["object"], demand["object"], choices)
                    matches.append(match)

                    print(f'woo hoo, {supply["object"].thing_id} sold!!!!!')


    async def phase_4LEAVE(self, ctx):

        self.phase_trace(ctx)



