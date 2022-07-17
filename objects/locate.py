#!/usr/bin/env python3
# -*- encoding: utf-8
# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 12020 - 12022 HE, Emporia.AI Pte Ltd

__banner__ = """













""" # __banner__

import json, copy
from common import *
from objects.persist import *
from pydantic.json import pydantic_encoder

class config_LOCATE:

    def __init__(self, db, **kw):
        self.db = db

    async def route_LOCATE(self, data: Locate_DATA, **kw) -> Locate:
        args = {}
        await trio.sleep(0)
        return Locate(**args)

single_locate = config_LOCATE(persist)
