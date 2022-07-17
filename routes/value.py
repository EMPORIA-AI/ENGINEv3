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

blueprint = Blueprint('values', __name__)

#
# the list of all named values
#

@dataclass
class Values_GET:
    values: List[Value]

@tag(['value'])
@blueprint.route('/api/config/v1/values', methods=['GET'])
@validate_response(Values_GET, 200)
async def get_values():
    """
    Get alter fields of all alter objects.  ?full=0 for basic information.
    """
    action = {"mode":"get", "args":request.args}
    outgoing = Manage_DATA(action=action, values=[Value(id="*")])
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    return Values_GET(values=decoding.values)

#
# get identified alter or all when: id == '*'
#

@tag(['value'])
@blueprint.route('/api/config/v1/values/<csv_or_wild>', methods=['GET'])
@validate_response(Values_GET, 200)
async def get_values_csv(csv_or_wild):
    """
    Get alter fields by id or name when wild.  ?full=0 for basic information.
    """
    values = []
    for id in csv_or_wild.split(','):
        values.append(Value(id=id))
    action = {"mode":"get", "args":request.args}
    outgoing = Manage_DATA(action=action, values=values)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    return Values_GET(values=decoding.values)


#
# adds news alter, id can be anything as its overwritten with ULID
#

@dataclass
class Values_DATA_POST:
    values: List[Value]

@dataclass
class Values_POST:
    obj_id: List[str]
    eclass: List[str]
    eabout: List[str]

@tag(['value'])
@blueprint.route('/api/config/v1/values', methods=['POST'])
@validate_request(Values_DATA_POST)
@validate_response(Values_POST, 200)
async def post_values(data: Values_DATA_POST):
    action = {"mode":"post", "args":request.args}
    outgoing = Manage_DATA(action=action, values=data.values)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    results = Values_POST([], [], [])
    for alter in decoding.values:
        results.obj_id.append(alter.id)
        results.eclass.append(alter.name)
        results.eabout.append(alter.tags)
    return results


#
#
#

@dataclass
class Values_DATA_PUT:
    values: List[Value]

@dataclass
class Values_PUT:
    eclass: List[str]
    eabout: List[str]

@tag(['value'])
@blueprint.route('/api/config/v1/values', methods=['PUT'])
@validate_request(Values_DATA_PUT)
@validate_response(Values_PUT, 200)
async def put_values(data: Values_DATA_PUT):
    action={"mode":"put", "args":request.args}
    outgoing = Manage_DATA(action=action, values=data.values)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    results = Values_PUT([], [])
    for alter in decoding.values:
        results.eclass.append(alter.name)
        results.eabout.append(alter.tags)
    return results


#
#
#

@dataclass
class Values_DATA_PATCH:
    values: List[Value]

@dataclass
class Values_PATCH:
    eclass: List[str]
    eabout: List[str]

@tag(['value'])
@blueprint.route('/api/config/v1/values', methods=['PATCH'])
@validate_request(Values_DATA_PATCH)
@validate_response(Values_PATCH, 200)
async def patch_values(data: Values_DATA_PATCH):
    action={"mode":"patch", "args":request.args}
    outgoing = Manage_DATA(action=action, values=data.values)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    results = Values_PATCH([], [])
    for alter in decoding.values:
        results.eclass.append(alter.name)
        results.eabout.append(alter.tags)
    return results



#
# delete identified alter(s)
#

@dataclass
class Values_DELETE:
    eclass: List[str]
    eabout: List[str]

@tag(['value'])
@blueprint.route('/api/config/v1/values/<csv_or_wild>', methods=['DELETE'])
@validate_response(Values_DELETE, 200)
async def delete_values(csv_or_wild):
    values = []
    for id in csv_or_wild.split(','):
        values.append(Value(id=id))
    action={"mode":"delete", "args":request.args}
    outgoing = Manage_DATA(action=action, values=values)
    incoming = await manage_post(outgoing)
    incoming = Manage(**incoming)
    results = Values_DELETE([], [])
    for alter in incoming.values:
        results.eclass.append(alter.name)
        results.eabout.append(alter.tags)
    return results
