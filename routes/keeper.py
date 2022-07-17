#!/usr/bin/env python3
# -*- encoding: utf-8
# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 12020 - 12022 HE, Emporia.AI Pte Ltd

__banner__ = """













""" # __banner__

from quart import Blueprint, request, abort
from quart_schema import *

from routes import *
from common import *
from objects.auth import *

blueprint = Blueprint('keepers', __name__)

#
# the list of all named keepers
#

@dataclass
class Keepers_GET:
    keepers: List[Keeper]

@tag(['keeper'])
@blueprint.route('/api/config/v1/keepers', methods=['GET'])
@validate_response(Keepers_GET, 200)
async def get_keepers():
    """
    Get keeper fields of all keeper objects.  ?full=0 for basic information.
    """
    action = {"mode":"get", "args":request.args}
    outgoing = Manage_DATA(action=action, keepers=[Keeper(id="*")])
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    return Keepers_GET(keepers=decoding.keepers)

#
# get identified keeper or all when: id == '*'
#

@tag(['keeper'])
@blueprint.route('/api/config/v1/keepers/<csv_or_wild>', methods=['GET'])
@validate_response(Keepers_GET, 200)
async def get_keepers_csv(csv_or_wild):
    """
    Get keeper fields by id or name when wild.  ?full=0 for basic information.
    """
    keepers = []
    for id in csv_or_wild.split(','):
        keepers.append(Keeper(id=id))
    action = {"mode":"get", "args":request.args}
    outgoing = Manage_DATA(action=action, keepers=keepers)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    return Keepers_GET(keepers=decoding.keepers)


#
# adds news keeper, id can be anything as its overwritten with ULID
#

@dataclass
class Keepers_DATA_POST:
    keepers: List[Keeper]

@dataclass
class Keepers_POST:
    obj_id: List[str]
    eclass: List[str]
    eabout: List[str]

@tag(['keeper'])
@blueprint.route('/api/config/v1/keepers', methods=['POST'])
@validate_request(Keepers_DATA_POST)
@validate_response(Keepers_POST, 200)
async def post_keepers(data: Keepers_DATA_POST):
    action = {"mode":"post", "args":request.args}
    outgoing = Manage_DATA(action=action, keepers=data.keepers)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    results = Keepers_POST([], [], [])
    for keeper in decoding.keepers:
        results.obj_id.append(keeper.id)
        results.eclass.append(keeper.name)
        results.eabout.append(keeper.tags)
    return results


#
#
#

@dataclass
class Keepers_DATA_PUT:
    keepers: List[Keeper]

@dataclass
class Keepers_PUT:
    eclass: List[str]
    eabout: List[str]

@tag(['keeper'])
@blueprint.route('/api/config/v1/keepers', methods=['PUT'])
@validate_request(Keepers_DATA_PUT)
@validate_response(Keepers_PUT, 200)
async def put_keepers(data: Keepers_DATA_PUT):
    action={"mode":"put", "args":request.args}
    outgoing = Manage_DATA(action=action, keepers=data.keepers)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    results = Keepers_PUT([], [])
    for keeper in decoding.keepers:
        results.eclass.append(keeper.name)
        results.eabout.append(keeper.tags)
    return results


#
#
#

@dataclass
class Keepers_DATA_PATCH:
    keepers: List[Keeper]

@dataclass
class Keepers_PATCH:
    eclass: List[str]
    eabout: List[str]

@tag(['keeper'])
@blueprint.route('/api/config/v1/keepers', methods=['PATCH'])
@validate_request(Keepers_DATA_PATCH)
@validate_response(Keepers_PATCH, 200)
async def patch_keepers(data: Keepers_DATA_PATCH):
    action={"mode":"patch", "args":request.args}
    outgoing = Manage_DATA(action=action, keepers=data.keepers)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    results = Keepers_PATCH([], [])
    for keeper in decoding.keepers:
        results.eclass.append(keeper.name)
        results.eabout.append(keeper.tags)
    return results



#
# delete identified keeper(s)
#

@dataclass
class Keepers_DELETE:
    eclass: List[str]
    eabout: List[str]

@tag(['keeper'])
@blueprint.route('/api/config/v1/keepers/<csv_or_wild>', methods=['DELETE'])
@validate_response(Keepers_DELETE, 200)
async def delete_keepers(csv_or_wild):
    keepers = []
    for id in csv_or_wild.split(','):
        keepers.append(Keeper(id=id))
    action={"mode":"delete", "args":request.args}
    outgoing = Manage_DATA(action=action, keepers=keepers)
    incoming = await manage_post(outgoing)
    incoming = Manage(**incoming)
    results = Keepers_DELETE([], [])
    for keeper in incoming.keepers:
        results.eclass.append(keeper.name)
        results.eabout.append(keeper.tags)
    return results
