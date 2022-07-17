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

blueprint = Blueprint('things', __name__)

#
# the list of all named things
#

@dataclass
class Things_GET:
    things: List[Thing]

@tag(['thing'])
@blueprint.route('/api/config/v1/things', methods=['GET'])
@validate_response(Things_GET, 200)
async def get_things():
    """
    Get thing fields of all thing objects.  ?full=0 for basic information.
    """
    action = {"mode":"get", "args":request.args}
    outgoing = Manage_DATA(action=action, things=[Thing(id="*")])
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    return Things_GET(things=decoding.things)

#
# get identified thing or all when: id == '*'
#

@tag(['thing'])
@blueprint.route('/api/config/v1/things/<csv_or_wild>', methods=['GET'])
@validate_response(Things_GET, 200)
async def get_things_csv(csv_or_wild):
    """
    Get thing fields by id or name when wild.  ?full=0 for basic information.
    """
    things = []
    for id in csv_or_wild.split(','):
        things.append(Thing(id=id))
    action = {"mode":"get", "args":request.args}
    outgoing = Manage_DATA(action=action, things=things)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    return Things_GET(things=decoding.things)


#
# adds news thing, id can be anything as its overwritten with ULID
#

@dataclass
class Things_DATA_POST:
    things: List[Thing]

@dataclass
class Things_POST:
    obj_id: List[str]
    eclass: List[str]
    eabout: List[str]

@tag(['thing'])
@blueprint.route('/api/config/v1/things', methods=['POST'])
@validate_request(Things_DATA_POST)
@validate_response(Things_POST, 200)
async def post_things(data: Things_DATA_POST):
    action = {"mode":"post", "args":request.args}
    outgoing = Manage_DATA(action=action, things=data.things)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    results = Things_POST([], [], [])
    for thing in decoding.things:
        results.obj_id.append(thing.id)
        results.eclass.append(thing.name)
        results.eabout.append(thing.tags)
    return results


#
#
#

@dataclass
class Things_DATA_PUT:
    things: List[Thing]

@dataclass
class Things_PUT:
    eclass: List[str]
    eabout: List[str]

@tag(['thing'])
@blueprint.route('/api/config/v1/things', methods=['PUT'])
@validate_request(Things_DATA_PUT)
@validate_response(Things_PUT, 200)
async def put_things(data: Things_DATA_PUT):
    action={"mode":"put", "args":request.args}
    outgoing = Manage_DATA(action=action, things=data.things)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    results = Things_PUT([], [])
    for thing in decoding.things:
        results.eclass.append(thing.name)
        results.eabout.append(thing.tags)
    return results


#
#
#

@dataclass
class Things_DATA_PATCH:
    things: List[Thing]

@dataclass
class Things_PATCH:
    eclass: List[str]
    eabout: List[str]

@tag(['thing'])
@blueprint.route('/api/config/v1/things', methods=['PATCH'])
@validate_request(Things_DATA_PATCH)
@validate_response(Things_PATCH, 200)
async def patch_things(data: Things_DATA_PATCH):
    action={"mode":"patch", "args":request.args}
    outgoing = Manage_DATA(action=action, things=data.things)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    results = Things_PATCH([], [])
    for thing in decoding.things:
        results.eclass.append(thing.name)
        results.eabout.append(thing.tags)
    return results



#
# delete identified thing(s)
#

@dataclass
class Things_DELETE:
    eclass: List[str]
    eabout: List[str]

@tag(['thing'])
@blueprint.route('/api/config/v1/things/<csv_or_wild>', methods=['DELETE'])
@validate_response(Things_DELETE, 200)
async def delete_things(csv_or_wild):
    things = []
    for id in csv_or_wild.split(','):
        things.append(Thing(id=id))
    action={"mode":"delete", "args":request.args}
    outgoing = Manage_DATA(action=action, things=things)
    incoming = await manage_post(outgoing)
    incoming = Manage(**incoming)
    results = Things_DELETE([], [])
    for thing in incoming.things:
        results.eclass.append(thing.name)
        results.eabout.append(thing.tags)
    return results
