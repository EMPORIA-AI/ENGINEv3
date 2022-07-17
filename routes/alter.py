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

blueprint = Blueprint('alters', __name__)

#
# the list of all named alters
#

@dataclass
class Alters_GET:
    alters: List[Alter]

@tag(['alter'])
@blueprint.route('/api/config/v1/alters', methods=['GET'])
@validate_response(Alters_GET, 200)
async def get_alters():
    """
    Get alter fields of all alter objects.  ?full=0 for basic information.
    """
    action = {"mode":"get", "args":request.args}
    outgoing = Manage_DATA(action=action, alters=[Alter(id="*")])
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    return Alters_GET(alters=decoding.alters)

#
# get identified alter or all when: id == '*'
#

@tag(['alter'])
@blueprint.route('/api/config/v1/alters/<csv_or_wild>', methods=['GET'])
@validate_response(Alters_GET, 200)
async def get_alters_csv(csv_or_wild):
    """
    Get alter fields by id or name when wild.  ?full=0 for basic information.
    """
    alters = []
    for id in csv_or_wild.split(','):
        alters.append(Alter(id=id))
    action = {"mode":"get", "args":request.args}
    outgoing = Manage_DATA(action=action, alters=alters)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    return Alters_GET(alters=decoding.alters)


#
# adds news alter, id can be anything as its overwritten with ULID
#

@dataclass
class Alters_DATA_POST:
    alters: List[Alter]

@dataclass
class Alters_POST:
    obj_id: List[str]
    eclass: List[str]
    eabout: List[str]

@tag(['alter'])
@blueprint.route('/api/config/v1/alters', methods=['POST'])
@validate_request(Alters_DATA_POST)
@validate_response(Alters_POST, 200)
async def post_alters(data: Alters_DATA_POST):
    action = {"mode":"post", "args":request.args}
    outgoing = Manage_DATA(action=action, alters=data.alters)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    results = Alters_POST([], [], [])
    for alter in decoding.alters:
        results.obj_id.append(alter.id)
        results.eclass.append(alter.name)
        results.eabout.append(alter.tags)
    return results


#
#
#

@dataclass
class Alters_DATA_PUT:
    alters: List[Alter]

@dataclass
class Alters_PUT:
    eclass: List[str]
    eabout: List[str]

@tag(['alter'])
@blueprint.route('/api/config/v1/alters', methods=['PUT'])
@validate_request(Alters_DATA_PUT)
@validate_response(Alters_PUT, 200)
async def put_alters(data: Alters_DATA_PUT):
    action={"mode":"put", "args":request.args}
    outgoing = Manage_DATA(action=action, alters=data.alters)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    results = Alters_PUT([], [])
    for alter in decoding.alters:
        results.eclass.append(alter.name)
        results.eabout.append(alter.tags)
    return results


#
#
#

@dataclass
class Alters_DATA_PATCH:
    alters: List[Alter]

@dataclass
class Alters_PATCH:
    eclass: List[str]
    eabout: List[str]

@tag(['alter'])
@blueprint.route('/api/config/v1/alters', methods=['PATCH'])
@validate_request(Alters_DATA_PATCH)
@validate_response(Alters_PATCH, 200)
async def patch_alters(data: Alters_DATA_PATCH):
    action={"mode":"patch", "args":request.args}
    outgoing = Manage_DATA(action=action, alters=data.alters)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    results = Alters_PATCH([], [])
    for alter in decoding.alters:
        results.eclass.append(alter.name)
        results.eabout.append(alter.tags)
    return results



#
# delete identified alter(s)
#

@dataclass
class Alters_DELETE:
    eclass: List[str]
    eabout: List[str]

@tag(['alter'])
@blueprint.route('/api/config/v1/alters/<csv_or_wild>', methods=['DELETE'])
@validate_response(Alters_DELETE, 200)
async def delete_alters(csv_or_wild):
    alters = []
    for id in csv_or_wild.split(','):
        alters.append(Alter(id=id))
    action={"mode":"delete", "args":request.args}
    outgoing = Manage_DATA(action=action, alters=alters)
    incoming = await manage_post(outgoing)
    incoming = Manage(**incoming)
    results = Alters_DELETE([], [])
    for alter in incoming.alters:
        results.eclass.append(alter.name)
        results.eabout.append(alter.tags)
    return results
