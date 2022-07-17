#!/usr/bin/env python3
# -*- encoding: utf-8
# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 12020 - 12022 HE, Emporia.AI Pte Ltd

__banner__ = """













""" # __banner__

import os, os.path, io, glob, json, copy, hashlib, bisect

from common import *

from ulid import ULID

from pydantic.json import pydantic_encoder

def parseLine(line):
    (left, sep, right) = line.partition(b'\t')
    key = json.loads( left.decode('utf8') )
    value = json.loads( right.decode('utf8') )
    return ( key, value )

def parseKey(line):
    (left, sep, right) = line.partition(b'\t')
    key = json.loads( left.decode('utf8') )
    return key

def parseValue(line):
    (left, sep, right) = line.partition(b'\t')
    value = json.loads( right.decode('utf8') )
    return value


#
# pip install pysos
# SPDX-License-Identifier: Apache-2.0
# https://github.com/dagnelies/pysos/blob/master/LICENSE
#

class pysos_Dict(dict):
    START_FLAG = b'# FILE-DICT v1\n'

    def __init__(self, path, **kw):
        self.path = path
        self.version = str(ULID())[:-2] + '0Z'

        for k, v in kw.items():
            self.__dict__[k] = v

        if os.path.exists(path):
            file = io.open(path, 'r+b')
        else:
            file = io.open(path, 'w+b')
            file.write( self.START_FLAG )
            file.flush()

        self._file = file
        self._offsets = {}   # the (size, offset) of the lines, where size is in bytes, including the trailing \n
        self._free_lines = []
        self._observers = []

        offset = 0
        while True:
            line = file.readline()
            if line == b'': # end of file
                break

            # ignore empty lines
            if line == b'\n':
                offset += len(line)
                continue

            if line.startswith(b'#'):   # skip comments but add to free list
                if len(line) > 5:
                    self._free_lines.append( (len(line), offset) )
            else:
                # let's parse the value as well to be sure the data is ok
                key = parseKey(line)
                self._offsets[key] = offset

            offset += len(line)

        self._free_lines.sort()

    def _freeLine(self, offset):
        self._file.seek(offset)
        self._file.write(b'#')
        self._file.flush()

        line = self._file.readline()
        size = len(line) + 1   # one character was written beforehand

        if size > 5:
            bisect.insort(self._free_lines, (len(line)+1, offset) )

    def _findLine(self, size):
        index = bisect.bisect( self._free_lines, (size,0) )
        if index >= len( self._free_lines ):
            return None
        else:
            return self._free_lines.pop(index)

    def _isWorthIt(self, size):
        # determines if it's worth to add the free line to the list
        # we don't want to clutter this list with a large amount of tiny gaps
        return (size > 5 + len(self._free_lines))

    def __getitem__(self, key):
        offset = self._offsets[key]
        self._file.seek(offset)
        line = self._file.readline()
        value = parseValue(line)
        return value

    def __setitem__(self, key, value):

        self.version = str(ULID())[:-2] + '0Z'

        # trigger observers
        if self._observers:
            old_value = self[key] if key in self else None
            for callback in self._observers:
                callback(key, value, old_value)

        if key in self._offsets:
            # to be removed once the new value has been written
            old_offset = self._offsets[key]
        else:
            old_offset = None

        lhs = json.dumps(key,ensure_ascii=False)
        rhs = json.dumps(value,ensure_ascii=False,default=pydantic_encoder)


        line = f"{lhs}\t{rhs}\n"
        line = line.encode('UTF-8')
        size = len(line)

        found = self._findLine(size)

        if found:
            # great, we can recycle a commented line
            (place, offset) = found
            self._file.seek(offset)
            diff = place - size
            # if diff is 0, we'll override the line perfectly:        XXXX\n -> YYYY\n
            # if diff is 1, we'll leave an empty line after:          XXXX\n -> YYY\n\n
            # if diff is > 1, we'll need to comment out the rest:     XXXX\n -> Y\n#X\n (diff == 3)
            if diff > 1:
                line += b'#'
                if diff > 5:
                    # it's worth to reuse that space
                    bisect.insort(self._free_lines, (diff, offset + size) )

        else:
            # go to end of file
            self._file.seek(0, os.SEEK_END)
            offset = self._file.tell()

        # if it's a really big line, it won't be written at once on the disk
        # so until it's done, let's consider it a comment
        self._file.write(b'#' + line[1:])
        if line[-1] == 35:
            # if it ends with a "comment" (bytes to recycle),
            # let's be clean and avoid cutting unicode chars in the middle
            while self._file.peek(1)[0] & 0x80 == 0x80: # it's a continuation byte
                self._file.write(b'.')
        self._file.flush()
        # now that everything has been written...
        self._file.seek(offset)
        self._file.write(line[0:1])
        self._file.flush()

        # and now remove the previous entry
        if old_offset:
            self._freeLine(old_offset)

        self._offsets[key] = offset

    def touch(self):
        self.version = str(ULID())[:-2] + '0Z'

    def __delitem__(self, key):

        self.version = str(ULID())[:-2] + '0Z'

        # trigger observers
        if self._observers:
            old_value = self[key]
            for callback in self._observers:
                callback(key, None, old_value)

        offset = self._offsets[key]
        self._freeLine(offset)
        del self._offsets[key]


    def __contains__(self, key):
        return (key in self._offsets)

    def observe(self, callback):
        self._observers.append(callback)


    def keys(self):
        return self._offsets.keys()

    def clear(self):

        self.version = str(ULID())[:-2] + '0Z'

        keys = []
        for key in self.keys():
            keys.append(key)

        for key in keys:
            del self[key]

        #self._file.truncate(0)
        #self._file.flush()
        #self._offsets = {}
        #self._free_lines = []

    def items(self):
        offset = 0
        while True:
            # if somethig was read/written while iterating, the stream might be positioned elsewhere
            if self._file.tell() != offset:
                self._file.seek(offset) #put it back on track

            line = self._file.readline()
            if line == b'': # end of file
                break

            offset += len(line)
            # ignore empty and commented lines
            if line == b'\n' or line[0] == 35:
                continue
            yield parseLine(line)

    def __iter__(self):
        return self.keys()

    def values(self):
        for item in self.items():
            yield item[1]

    def __len__(self):
        return len(self._offsets)

    def size(self):
        self._file.size()

    def close(self):
        self._file.close()

#
# Storage is used for objects that are not releated to configuration and therefore
# not promoted through staging, running.
#

class Storage:

    def __init__(self, datapath="./db", **kw):
        self.datapath = datapath
        self.testmode = False
        self.verified = None

        #
        # values is where the global state of the engine(s) lives
        #

        self.tables = ['things']

        os.makedirs(datapath, exist_ok=True)

        def factory(*args, **kwargs):
            return Thing(*args, **kwargs)
        self.things = pysos_Dict(self.datapath + '/things.txt', factory=factory)

    def get_version(self):
        version = []
        for tname in self.tables:
            version.append(getattr(self, tname).version)
        return hashlib.sha256("-".join(version).encode("utf-8")).hexdigest()

    def id_exists(self, id):
        exists = False
        if id in persist.things: exists = True
        return exists


class Persist:

    def __init__(self, datapath="./db", **kw):
        self.datapath = datapath
        self.testmode = False
        self.verified = None

        #
        # values is where the global state of the engine(s) lives
        #

        self.tables = ['values', 'alters', 'genres', 'spaces', 'wheres', 'brokers', 'keepers']

        os.makedirs(datapath, exist_ok=True)

        def factory(*args, **kwargs):
            return Value(*args, **kwargs)
        self.values = pysos_Dict(self.datapath + '/values.txt', factory=factory)

        def factory(*args, **kwargs):
            return Alter(*args, **kwargs)
        self.alters = pysos_Dict(self.datapath + '/alters.txt', factory=factory)

        def factory(*args, **kwargs):
            return Genre(*args, **kwargs)
        self.genres = pysos_Dict(self.datapath + '/genres.txt', factory=factory)

        def factory(*args, **kwargs):
            return Space(*args, **kwargs)
        self.spaces = pysos_Dict(self.datapath + '/spaces.txt', factory=factory)

        def factory(*args, **kwargs):
            return Where(*args, **kwargs)
        self.wheres = pysos_Dict(self.datapath + '/wheres.txt', factory=factory)

        def factory(*args, **kwargs):
            return Broker(*args, **kwargs)
        self.brokers = pysos_Dict(self.datapath + '/brokers.txt', factory=factory)

        def factory(*args, **kwargs):
            return Keeper(*args, **kwargs)
        self.keepers = pysos_Dict(self.datapath + '/keepers.txt', factory=factory)

        self.version = self.get_version()

    def get_version(self):
        version = []
        for tname in self.tables:
            version.append(getattr(self, tname).version)
        return hashlib.sha256("-".join(version).encode("utf-8")).hexdigest()

    def id_exists(self, id):
        exists = False
        if id in persist.values: exists = True
        if id in persist.wheres: exists = True
        if id in persist.genres: exists = True
        if id in persist.spaces: exists = True
        if id in persist.alters: exists = True
        if id in persist.brokers: exists = True
        if id in persist.keepers: exists = True
        return exists

    def touch(self):
        self.values.touch()

    def verify(self):
        results = []

        # for each table, use the factory to instaniate all objects
        # and call the verify function to validate relationships
        for tname in self.tables:
            table = getattr(self, tname)
            if not table.factory: continue

            names = {}
            for record in table.values():
                object = table.factory(**record)
                results.extend(object.verify(self))

                if 'name' in object:
                    if object.name.lower() in names:
                        results.append([self, "name is not unique"])
                    names[object.name.lower()] = True




        self.verified = None if len(results) else self.get_version()

        return results

    def clone(self, rhs, require_verification=True):

        if require_verification:
            assert rhs.verified

        for tname in self.tables:
            table = getattr(self, tname)
            table.clear()
            table_rhs = getattr(rhs, tname)
            for record in table_rhs.values():
                table[record["id"]] = copy.copy(record)
            table.version = table_rhs.version

        self.version = self.get_version()


storage = Storage()

persist = Persist()
persist.verify()

# TODO: Keeps all the backups, prefix the files with ULID
persist_backups = Persist(datapath="./db_backups")
persist_backups.clone(persist)

persist_staging = Persist(datapath="./db_staging")
persist_staging.clone(persist)

assert persist_staging.version == persist.version
assert persist_staging.alters.version == persist.alters.version

persist_running = Persist(datapath="./db_running")
persist_running.clone(persist_staging, require_verification=False)

assert persist_running.version == persist_staging.version
assert persist_running.alters.version == persist_staging.alters.version



