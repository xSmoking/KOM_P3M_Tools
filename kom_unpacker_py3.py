# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import struct
import os
import sys
import zlib
import ntpath


class Entry(object):
    def __init__(self, name, uncompressed_size, compressed_size, relative_offset):
        self.__name = name
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


def unpack(argv):
    if len(argv) == 0:
        sys.exit(2)

    file_name = argv[0]
    folder_name = ntpath.basename(file_name).split('.')[0]

    file_object = open(file_name, 'rb')
    data_file = file_object.read()
    offset = 0

    offset += 26  # skip version
    offset += 26  # skip padding

    entries_count = struct.unpack_from('<2I', data_file, offset)[0]

    offset += 8  # skip padding
    entries = []

    for i in range(entries_count):
        file_name = struct.unpack_from('<60s', data_file, offset)[0].decode()
        file_name.rstrip('\x00')

        offset += 60

        uncompressed_size, compressed_size, relative_offset = struct.unpack_from('<3I', data_file, offset)

        entry = Entry(file_name, uncompressed_size, compressed_size, relative_offset)
        entries.append(entry)

        offset += 12

    file_object.close()

    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

    for entry in entries:
        entry_file_data = data_file[offset + entry.relative_offset:offset + entry.relative_offset + entry.compressed_size]
        entry_file_data = zlib.decompress(entry_file_data)

        name = entry.name.split('.')
        extension = 'p3m' if 'p3m' in name[1] else 'xml'
        path = folder_name + '/' + name[0] + '.' + extension

        try:
            file_object = open(path, 'w+b')
            file_object.write(entry_file_data)
        finally:
            file_object.close()


if __name__ == "__main__":
    unpack(sys.argv[1:])
