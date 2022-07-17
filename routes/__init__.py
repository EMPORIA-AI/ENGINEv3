#!/usr/bin/env python3
# -*- encoding: utf-8
# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 12020 - 12022 HE, Emporia.AI Pte Ltd

__banner__ = """













""" # __banner__

import trio, asks, json

from pydantic.json import pydantic_encoder

from quart import abort

from objects.manage import singleton_manage

async def manage_post(incoming):
    outgoing = await singleton_manage.route_MANAGE(data=incoming)
    return outgoing.dict()

