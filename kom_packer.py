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
from os import listdir
from os.path import isfile, join
import sys
import zlib
import ntpath


def pack(argv):
    if len(argv) == 0:
        sys.exit(2)

    input_folder = argv[0]
    output_file = argv[1]

    file_object = open(output_file, 'wb')

    file_object.write("KOG GC TEAM MASSFILE V.0.2".encode("ascii"))
    file_object.write(struct.pack('<26x'))

    files = [f for f in listdir(input_folder) if isfile(join(input_folder, f))]

    entries_count = [len(files), 1]
    #file_object.write(struct.pack("I"*2, entries_count[0], entries_count[1]))
    file_object.write(struct.pack("<2I", entries_count[0], entries_count[1]))

    for i in files:
        print(i)


if __name__ == "__main__":
    pack(sys.argv[1:])
