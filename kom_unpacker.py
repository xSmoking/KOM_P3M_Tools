#!/usr/bin/python

# Copyright (c) 2009-2012 AJ
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import getopt
import os
import struct
import sys
import zlib


class Entry(object):
    def __init__(self, name, uncompressed_size, compressed_size, relative_offset):
        self.__name = name[0:name.find('\0')]
        self.__uncompressed_size = uncompressed_size
        self.__compressed_size = compressed_size
        self.__relative_offset = relative_offset
    
    def get_name(self):
        return self.__name
    
    def get_uncompressed_size(self):
        return self.__uncompressed_size
    
    def get_compressed_size(self):
        return self.__compressed_size
    
    def get_relative_offset(self):
        return self.__relative_offset
    
    name = property(get_name)
    
    uncompressed_size = property(get_uncompressed_size)
    
    compressed_size = property(get_compressed_size)
    
    relative_offset = property(get_relative_offset)


def main(argv):
    if len(argv) < 1:
        sys.exit(2)
    
    try:
        options, arguments = getopt.getopt(argv, 'vf:', ['verbose', 'file='])
    except getopt.GetoptError:
        sys.exit(2)
    
    verbose = False
    file_name = None
    
    for option, argument in options:
        if option in ('v', '--verbose'):
            verbose = True
        elif option in ('f', '--file'):
            file_name = argument
    
    if file_name is None:
        file_name = argv[0]
    
    if os.path.isfile(file_name) == False:
        sys.exit(2)
    
    file_object = None
    file_data = None
    
    try:
        file_object = open(file_name, 'rb')
        
        if file_object is not None:
            file_data = file_object.read()
    finally:
        if file_object is not None:
            file_object.close()

            file_object = None
    
    offset = 0
    
    version = struct.unpack_from('<26s26x', file_data, offset)[0]
    
    offset += 52
    
    entry_count = struct.unpack_from('<I4x', file_data, offset)[0]
    
    offset += 8
    
    entries = []
    
    for x in xrange(entry_count):
        entry = Entry(*struct.unpack_from('<60s3I', file_data, offset))
        
        entries.append(entry)
        
        offset += 72

    for entry in entries:
        entry_file_data = file_data[offset + entry.relative_offset:offset + entry.relative_offset + entry.compressed_size]
        
        entry_file_data = zlib.decompress(entry_file_data)
        
        try:
            file_object = open(entry.name, 'wb')
            
            if file_object is not None:
                file_object.write(entry_file_data)
        finally:
            if file_object is not None:
                file_object.close()
                
                file_object = None


if __name__ == "__main__":
    main(sys.argv[1:])