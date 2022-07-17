#!/usr/bin/env python3
# -*- encoding: utf-8
# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 12020 - 12022 HE, Emporia.AI Pte Ltd

__banner__ = """













""" # __banner__

def auth_core_required(func):

    @wraps(func)
    async def wrapper(*args, **kwargs):
        auth = request.authorization
        if (
            auth is not None and
            auth.type == "basic" and
            # auth.username == current_app.config["BASIC_AUTH_USERNAME"] and
            auth.username == "FOO" and
            # compare_digest(auth.password, current_app.config["BASIC_AUTH_PASSWORD"])
            compare_digest(auth.password, "barBAZ!")
        ):
            return await func(*args, **kwargs)
        else:
            abort(401)

    return wrapper

