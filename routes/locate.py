#!/usr/bin/env python3
# -*- encoding: utf-8
# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 12020 - 12022 HE, Emporia.AI Pte Ltd

__banner__ = """













""" # __banner__

from quart import Blueprint, abort
from quart_schema import validate_request, validate_response

from routes import *
from common import *
from objects.auth import *
from objects.locate import *

blueprint = Blueprint('LOCATE', __name__)

@blueprint.route("/api/engine/1v0/LOCATE", methods=["POST"])
@validate_request(Locate_DATA)
@validate_response(Locate, 200)
async def app_LOCATE(data: Locate_DATA) -> Locate:
    """
    """
    try:
        return await object_locate.route_LOCATE(data=data)
    except:
        abort(400)


