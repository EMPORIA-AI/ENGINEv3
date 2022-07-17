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

blueprint = Blueprint('genres', __name__)

#
# the list of all named genres
#

@dataclass
class Genres_GET:
    genres: List[Genre]

@tag(['genre'])
@blueprint.route('/api/config/v1/genres', methods=['GET'])
@validate_response(Genres_GET, 200)
async def get_genres():
    """
    Get genre fields of all genre objects.  ?full=0 for basic information.
    """
    action = {"mode":"get", "args":request.args}
    outgoing = Manage_DATA(action=action, genres=[Genre(id="*")])
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    return Genres_GET(genres=decoding.genres)

#
# get identified genre or all when: id == '*'
#

@tag(['genre'])
@blueprint.route('/api/config/v1/genres/<csv_or_wild>', methods=['GET'])
@validate_response(Genres_GET, 200)
async def get_genres_csv(csv_or_wild):
    """
    Get genre fields by id or name when wild.  ?full=0 for basic information.
    """
    genres = []
    for id in csv_or_wild.split(','):
        genres.append(Genre(id=id))
    action = {"mode":"get", "args":request.args}
    outgoing = Manage_DATA(action=action, genres=genres)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    return Genres_GET(genres=decoding.genres)


#
# adds news genre, id can be anything as its overwritten with ULID
#

@dataclass
class Genres_DATA_POST:
    genres: List[Genre]

@dataclass
class Genres_POST:
    obj_id: List[str]
    eclass: List[str]
    eabout: List[str]

@tag(['genre'])
@blueprint.route('/api/config/v1/genres', methods=['POST'])
@validate_request(Genres_DATA_POST)
@validate_response(Genres_POST, 200)
async def post_genres(data: Genres_DATA_POST):
    action = {"mode":"post", "args":request.args}
    outgoing = Manage_DATA(action=action, genres=data.genres)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    results = Genres_POST([], [], [])
    for genre in decoding.genres:
        results.obj_id.append(genre.id)
        results.eclass.append(genre.name)
        results.eabout.append(genre.tags)
    return results


#
#
#

@dataclass
class Genres_DATA_PUT:
    genres: List[Genre]

@dataclass
class Genres_PUT:
    eclass: List[str]
    eabout: List[str]

@tag(['genre'])
@blueprint.route('/api/config/v1/genres', methods=['PUT'])
@validate_request(Genres_DATA_PUT)
@validate_response(Genres_PUT, 200)
async def put_genres(data: Genres_DATA_PUT):
    action={"mode":"put", "args":request.args}
    outgoing = Manage_DATA(action=action, genres=data.genres)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    results = Genres_PUT([], [])
    for genre in decoding.genres:
        results.eclass.append(genre.name)
        results.eabout.append(genre.tags)
    return results


#
#
#

@dataclass
class Genres_DATA_PATCH:
    genres: List[Genre]

@dataclass
class Genres_PATCH:
    eclass: List[str]
    eabout: List[str]

@tag(['genre'])
@blueprint.route('/api/config/v1/genres', methods=['PATCH'])
@validate_request(Genres_DATA_PATCH)
@validate_response(Genres_PATCH, 200)
async def patch_genres(data: Genres_DATA_PATCH):
    action={"mode":"patch", "args":request.args}
    outgoing = Manage_DATA(action=action, genres=data.genres)
    incoming = await manage_post(outgoing)
    decoding = Manage(**incoming)
    results = Genres_PATCH([], [])
    for genre in decoding.genres:
        results.eclass.append(genre.name)
        results.eabout.append(genre.tags)
    return results



#
# delete identified genre(s)
#

@dataclass
class Genres_DELETE:
    eclass: List[str]
    eabout: List[str]

@tag(['genre'])
@blueprint.route('/api/config/v1/genres/<csv_or_wild>', methods=['DELETE'])
@validate_response(Genres_DELETE, 200)
async def delete_genres(csv_or_wild):
    genres = []
    for id in csv_or_wild.split(','):
        genres.append(Genre(id=id))
    action={"mode":"delete", "args":request.args}
    outgoing = Manage_DATA(action=action, genres=genres)
    incoming = await manage_post(outgoing)
    incoming = Manage(**incoming)
    results = Genres_DELETE([], [])
    for genre in incoming.genres:
        results.eclass.append(genre.name)
        results.eabout.append(genre.tags)
    return results
