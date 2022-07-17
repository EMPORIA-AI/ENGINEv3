#!/usr/bin/env python3
# -*- encoding: utf-8
# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 12020 - 12022 HE, Emporia.AI Pte Ltd

__banner__ = """













""" # __banner__

import globals

from quart import Blueprint, abort
from quart_schema import validate_request, validate_response

from routes import *
from common import *
from objects.auth import *
from objects.engine import *

blueprint = Blueprint('engine', __name__)

@blueprint.route("/api/engine/v1/0.SETUP", methods=["POST"])
@validate_request(Setup_DATA)
@validate_response(Setup, 200)
async def engine_SETUP(data: Setup_DATA) -> Setup:
    """

Traders call this API to signal they want to join the next round.

The server responds with a token and the time they should sleep
before calling the next stage with the offer details.

    """
    #try:

    # lookup by name if id is not a primary key
    if not data.space_id in globals.engines:
        for id in persist_running.spaces.keys():
            space = persist_running.spaces[id]
            if space["name"].lower() == data.space_id.lower():
                data.space_id = id
                break

    if not data.space_id in globals.engines: abort(403)
    return await globals.engines[data.space_id].route_SETUP(data=data)
    #except:
    #    abort(400)


@blueprint.route("/api/engine/v1/1.ENTER", methods=["POST"])
@validate_request(Enter_DATA)
@validate_response(Enter, 200)
async def engine_ENTER(data: Enter_DATA) -> Enter:
    """

Traders call this API to signal they want to join the next round.

The server responds with a token and the time they should sleep
before calling the next stage with the offer details.

    """
    #try:
    if not data.handle in globals.handles: abort(403)
    space_id = globals.handles[data.handle]
    if not space_id in globals.engines: abort(403)
    return await globals.engines[space_id].route_ENTER(data=data)
    #except:
    #    abort(400)



@blueprint.route("/api/engine/v1/2.OFFER", methods=["POST"])
@validate_request(Offer_DATA)
@validate_response(Offer, 200)
async def engine_OFFER(data: Offer_DATA) -> Offer:
    """

Offers contain cubed4th programs that act on behalf of account holders
to buy and sell items on the exchange.  These offers are binding and are
executed in a very specific then random order.  You cannot sell things you
dont own and you cannot make bids with more funds than you have on record
with your broker.

A single POST may contain thousands of buys/sells where the account holder
has been given permission to act on behalf of clients.

The reply again contains a sleep time that the client must wait before
calling the final API to leave the round and download the results.

    """
    #try:
    if not data.handle in globals.handles: abort(403)
    space_id = globals.handles[data.handle]
    if not space_id in globals.engines: abort(403)
    return await globals.engines[space_id].route_OFFER(data=data)
    #except:
    #    abort(400)



@blueprint.route("/api/engine/v1/3.THINK", methods=["POST"])
@validate_request(Think_DATA)
@validate_response(Think, 200)
async def engine_THINK(data: Think_DATA) -> Think:
    """

    """
    #try:
    if not data.handle in globals.handles: abort(403)
    space_id = globals.handles[data.handle]
    if not space_id in globals.engines: abort(403)
    return await globals.engines[space_id].route_THINK(data=data)
    #except:
    #    abort(400)



@blueprint.route("/api/engine/v1/4.LEAVE", methods=["POST"])
@validate_request(Leave_DATA)
@validate_response(Leave, 200)
async def engine_LEAVE(data: Leave_DATA) -> Leave:
    """

After the matching engine has run, the results are made available for
download over various systems.  As the size of the emporia increases it
the size of the completed round is expected to be significant.

This request also contains details of how the programs performed and
the contents of the virtual "screen" that may contain information
useful to the customer.

    """
    #try:
    if not data.handle in globals.handles: abort(403)
    space_id = globals.handles[data.handle]
    if not space_id in globals.engines: abort(403)
    return await globals.engines[space_id].route_LEAVE(data=data)
    #except:
    #    abort(400)

