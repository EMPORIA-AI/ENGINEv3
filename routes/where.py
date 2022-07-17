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

blueprint = Blueprint('wheres', __name__)

#
# the list of all named wheres
#

@dataclass
class Wheres_GET:
    wheres: List[Where]

@tag(['where'])
@blueprint.route('/api/config/v1/wheres', methods=['GET'])
@validate_response(Wheres_GET, 200)
async def get_wheres():
    """
    Get where fields of all where objects.  ?full=0 for basic information.
    """
    action = {"mode":"get", "args":request.args}
    outgoing = Manage_DATA(action=action, wheres=[Where(id="*")])
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    return Wheres_GET(wheres=decoding.wheres)

#
# get identified where or all when: id == '*'
#

@tag(['where'])
@blueprint.route('/api/config/v1/wheres/<csv_or_wild>', methods=['GET'])
@validate_response(Wheres_GET, 200)
async def get_wheres_csv(csv_or_wild):
    """
    Get where fields by id or name when wild.  ?full=0 for basic information.
    """
    wheres = []
    for id in csv_or_wild.split(','):
        wheres.append(Where(id=id))
    action = {"mode":"get", "args":request.args}
    outgoing = Manage_DATA(action=action, wheres=wheres)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    return Wheres_GET(wheres=decoding.wheres)


#
# adds news where, id can be anything as its overwritten with ULID
#

@dataclass
class Wheres_DATA_POST:
    wheres: List[Where]

@dataclass
class Wheres_POST:
    obj_id: List[str]
    eclass: List[str]
    eabout: List[str]

@tag(['where'])
@blueprint.route('/api/config/v1/wheres', methods=['POST'])
@validate_request(Wheres_DATA_POST)
@validate_response(Wheres_POST, 200)
async def post_wheres(data: Wheres_DATA_POST):
    action = {"mode":"post", "args":request.args}
    outgoing = Manage_DATA(action=action, wheres=data.wheres)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    results = Wheres_POST([], [], [])
    for where in decoding.wheres:
        results.obj_id.append(where.id)
        results.eclass.append(where.name)
        results.eabout.append(where.tags)
    return results


#
#
#

@dataclass
class Wheres_DATA_PUT:
    wheres: List[Where]

@dataclass
class Wheres_PUT:
    eclass: List[str]
    eabout: List[str]

@tag(['where'])
@blueprint.route('/api/config/v1/wheres', methods=['PUT'])
@validate_request(Wheres_DATA_PUT)
@validate_response(Wheres_PUT, 200)
async def put_wheres(data: Wheres_DATA_PUT):
    action={"mode":"put", "args":request.args}
    outgoing = Manage_DATA(action=action, wheres=data.wheres)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    results = Wheres_PUT([], [])
    for where in decoding.wheres:
        results.eclass.append(where.name)
        results.eabout.append(where.tags)
    return results


#
#
#

@dataclass
class Wheres_DATA_PATCH:
    wheres: List[Where]

@dataclass
class Wheres_PATCH:
    eclass: List[str]
    eabout: List[str]

@tag(['where'])
@blueprint.route('/api/config/v1/wheres', methods=['PATCH'])
@validate_request(Wheres_DATA_PATCH)
@validate_response(Wheres_PATCH, 200)
async def patch_wheres(data: Wheres_DATA_PATCH):
    action={"mode":"patch", "args":request.args}
    outgoing = Manage_DATA(action=action, wheres=data.wheres)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    results = Wheres_PATCH([], [])
    for where in decoding.wheres:
        results.eclass.append(where.name)
        results.eabout.append(where.tags)
    return results



#
# delete identified where(s)
#

@dataclass
class Wheres_DELETE:
    eclass: List[str]
    eabout: List[str]

@tag(['where'])
@blueprint.route('/api/config/v1/wheres/<csv_or_wild>', methods=['DELETE'])
@validate_response(Wheres_DELETE, 200)
async def delete_wheres(csv_or_wild):
    wheres = []
    for id in csv_or_wild.split(','):
        wheres.append(Where(id=id))
    action={"mode":"delete", "args":request.args}
    outgoing = Manage_DATA(action=action, wheres=wheres)
    incoming = await manage_post(outgoing)
    incoming = Manage(**incoming)
    results = Wheres_DELETE([], [])
    for where in incoming.wheres:
        results.eclass.append(where.name)
        results.eabout.append(where.tags)
    return results
