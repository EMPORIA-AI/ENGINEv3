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

blueprint = Blueprint('brokers', __name__)

#
# the list of all named brokers
#

@dataclass
class Brokers_GET:
    brokers: List[Broker]

@tag(['broker'])
@blueprint.route('/api/config/v1/brokers', methods=['GET'])
@validate_response(Brokers_GET, 200)
async def get_brokers():
    """
    Get broker fields of all broker objects.  ?full=0 for basic information.
    """
    action = {"mode":"get", "args":request.args}
    outgoing = Manage_DATA(action=action, brokers=[Broker(id="*")])
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    return Brokers_GET(brokers=decoding.brokers)

#
# get identified broker or all when: id == '*'
#

@tag(['broker'])
@blueprint.route('/api/config/v1/brokers/<csv_or_wild>', methods=['GET'])
@validate_response(Brokers_GET, 200)
async def get_brokers_csv(csv_or_wild):
    """
    Get broker fields by id or name when wild.  ?full=0 for basic information.
    """
    brokers = []
    for id in csv_or_wild.split(','):
        brokers.append(Broker(id=id))
    action = {"mode":"get", "args":request.args}
    outgoing = Manage_DATA(action=action, brokers=brokers)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    return Brokers_GET(brokers=decoding.brokers)


#
# adds news broker, id can be anything as its overwritten with ULID
#

@dataclass
class Brokers_DATA_POST:
    brokers: List[Broker]

@dataclass
class Brokers_POST:
    obj_id: List[str]
    eclass: List[str]
    eabout: List[str]

@tag(['broker'])
@blueprint.route('/api/config/v1/brokers', methods=['POST'])
@validate_request(Brokers_DATA_POST)
@validate_response(Brokers_POST, 200)
async def post_brokers(data: Brokers_DATA_POST):
    action = {"mode":"post", "args":request.args}
    outgoing = Manage_DATA(action=action, brokers=data.brokers)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    results = Brokers_POST([], [], [])
    for broker in decoding.brokers:
        results.obj_id.append(broker.id)
        results.eclass.append(broker.name)
        results.eabout.append(broker.tags)
    return results


#
#
#

@dataclass
class Brokers_DATA_PUT:
    brokers: List[Broker]

@dataclass
class Brokers_PUT:
    eclass: List[str]
    eabout: List[str]

@tag(['broker'])
@blueprint.route('/api/config/v1/brokers', methods=['PUT'])
@validate_request(Brokers_DATA_PUT)
@validate_response(Brokers_PUT, 200)
async def put_brokers(data: Brokers_DATA_PUT):
    action={"mode":"put", "args":request.args}
    outgoing = Manage_DATA(action=action, brokers=data.brokers)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    results = Brokers_PUT([], [])
    for broker in decoding.brokers:
        results.eclass.append(broker.name)
        results.eabout.append(broker.tags)
    return results


#
#
#

@dataclass
class Brokers_DATA_PATCH:
    brokers: List[Broker]

@dataclass
class Brokers_PATCH:
    eclass: List[str]
    eabout: List[str]

@tag(['broker'])
@blueprint.route('/api/config/v1/brokers', methods=['PATCH'])
@validate_request(Brokers_DATA_PATCH)
@validate_response(Brokers_PATCH, 200)
async def patch_brokers(data: Brokers_DATA_PATCH):
    action={"mode":"patch", "args":request.args}
    outgoing = Manage_DATA(action=action, brokers=data.brokers)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    results = Brokers_PATCH([], [])
    for broker in decoding.brokers:
        results.eclass.append(broker.name)
        results.eabout.append(broker.tags)
    return results



#
# delete identified broker(s)
#

@dataclass
class Brokers_DELETE:
    eclass: List[str]
    eabout: List[str]

@tag(['broker'])
@blueprint.route('/api/config/v1/brokers/<csv_or_wild>', methods=['DELETE'])
@validate_response(Brokers_DELETE, 200)
async def delete_brokers(csv_or_wild):
    brokers = []
    for id in csv_or_wild.split(','):
        brokers.append(Broker(id=id))
    action={"mode":"delete", "args":request.args}
    outgoing = Manage_DATA(action=action, brokers=brokers)
    incoming = await manage_post(outgoing)
    incoming = Manage(**incoming)
    results = Brokers_DELETE([], [])
    for broker in incoming.brokers:
        results.eclass.append(broker.name)
        results.eabout.append(broker.tags)
    return results
