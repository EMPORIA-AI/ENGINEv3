#!/usr/bin/env python3
# -*- encoding: utf-8
# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 12020 - 12022 HE, Emporia.AI Pte Ltd

__banner__ = """













""" # __banner__

from quart import Blueprint, abort
from quart_trio import QuartTrio
from quart_schema import validate_request, validate_response

from routes import *
from common import *
from objects.auth import *
from objects.manage import singleton_manage

blueprint = Blueprint('MANAGE', __name__)

@blueprint.route("/api/engine/v1/MANAGE", methods=["POST"])
@validate_request(Manage_DATA)
@validate_response(Manage, 200)
async def engine_MANAGE(data: Manage_DATA) -> Manage:
    """
    """
    if 1: #try:

        result = await singleton_manage.route_MANAGE(data=data)

        return result
    #except:
    #    abort(400)


