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

blueprint = Blueprint('spaces', __name__)

#
# the list of all named spaces
#

@dataclass
class Spaces_GET:
    spaces: List[Space]

@tag(['space'])
@blueprint.route('/api/config/v1/spaces', methods=['GET'])
@validate_response(Spaces_GET, 200)
async def get_spaces():
    """
    Get space fields of all space objects.  ?full=0 for basic information.
    """
    action = {"mode":"get", "args":request.args}
    outgoing = Manage_DATA(action=action, spaces=[Space(id="*")])
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    return Spaces_GET(spaces=decoding.spaces)

#
# get identified space or all when: id == '*'
#

@tag(['space'])
@blueprint.route('/api/config/v1/spaces/<csv_or_wild>', methods=['GET'])
@validate_response(Spaces_GET, 200)
async def get_spaces_csv(csv_or_wild):
    """
    Get space fields by id or name when wild.  ?full=0 for basic information.
    """
    spaces = []
    for id in csv_or_wild.split(','):
        spaces.append(Space(id=id))
    action = {"mode":"get", "args":request.args}
    outgoing = Manage_DATA(action=action, spaces=spaces)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    return Spaces_GET(spaces=decoding.spaces)


#
# adds news space, id can be anything as its overwritten with ULID
#

@dataclass
class Spaces_DATA_POST:
    spaces: List[Space]

@dataclass
class Spaces_POST:
    obj_id: List[str]
    eclass: List[str]
    eabout: List[str]

@tag(['space'])
@blueprint.route('/api/config/v1/spaces', methods=['POST'])
@validate_request(Spaces_DATA_POST)
@validate_response(Spaces_POST, 200)
async def post_spaces(data: Spaces_DATA_POST):
    action = {"mode":"post", "args":request.args}
    outgoing = Manage_DATA(action=action, spaces=data.spaces)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    results = Spaces_POST([], [], [])
    for space in decoding.spaces:
        results.obj_id.append(space.id)
        results.eclass.append(space.name)
        results.eabout.append(space.tags)
    return results


#
#
#

@dataclass
class Spaces_DATA_PUT:
    spaces: List[Space]

@dataclass
class Spaces_PUT:
    eclass: List[str]
    eabout: List[str]

@tag(['space'])
@blueprint.route('/api/config/v1/spaces', methods=['PUT'])
@validate_request(Spaces_DATA_PUT)
@validate_response(Spaces_PUT, 200)
async def put_spaces(data: Spaces_DATA_PUT):
    action={"mode":"put", "args":request.args}
    outgoing = Manage_DATA(action=action, spaces=data.spaces)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    results = Spaces_PUT([], [])
    for space in decoding.spaces:
        results.eclass.append(space.name)
        results.eabout.append(space.tags)
    return results


#
#
#

@dataclass
class Spaces_DATA_PATCH:
    spaces: List[Space]

@dataclass
class Spaces_PATCH:
    eclass: List[str]
    eabout: List[str]

@tag(['space'])
@blueprint.route('/api/config/v1/spaces', methods=['PATCH'])
@validate_request(Spaces_DATA_PATCH)
@validate_response(Spaces_PATCH, 200)
async def patch_spaces(data: Spaces_DATA_PATCH):
    action={"mode":"patch", "args":request.args}
    outgoing = Manage_DATA(action=action, spaces=data.spaces)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    results = Spaces_PATCH([], [])
    for space in decoding.spaces:
        results.eclass.append(space.name)
        results.eabout.append(space.tags)
    return results



#
# delete identified space(s)
#

@dataclass
class Spaces_DELETE:
    eclass: List[str]
    eabout: List[str]

@tag(['space'])
@blueprint.route('/api/config/v1/spaces/<csv_or_wild>', methods=['DELETE'])
@validate_response(Spaces_DELETE, 200)
async def delete_spaces(csv_or_wild):
    spaces = []
    for id in csv_or_wild.split(','):
        spaces.append(Space(id=id))
    action={"mode":"delete", "args":request.args}
    outgoing = Manage_DATA(action=action, spaces=spaces)
    incoming = await manage_post(outgoing)
    incoming = Manage(**incoming)
    results = Spaces_DELETE([], [])
    for space in incoming.spaces:
        results.eclass.append(space.name)
        results.eabout.append(space.tags)
    return results
