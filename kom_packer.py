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
from xml.dom.minidom import Document

def main(argv):
    if len(argv) < 2:
        sys.exit(2)
    
    try:
        options, arguments = getopt.getopt(argv, 'i:o:', ['in=', 'out='])
    except getopt.GetoptError:
        sys.exit(2)
    
    in_path = None
    out_path = None
    
    for option, argument in options:
        if option in ('i', '--in'):
            in_path = argument
        elif option in ('o', '--out'):
            out_path = argument
    
    if in_path is None or out_path is None:
        sys.exit(2)
    
    crc = Document()
    
    crc_file_info = crc.createElement("FileInfo")
    
    crc.appendChild(crc_file_info)
    
    crc_file_info_version = crc.createElement("Version")
    
    crc_file_info.appendChild(crc_file_info_version)
    
    crc_file_info_version_item = crc.createElement("Item")
    
    crc_file_info_version_item.setAttribute("Name", "V.0.2.")
    
    crc_file_info_version.appendChild(crc_file_info_version_item)
    
    crc_file_info_file = crc.createElement("File")
    
    crc_file_info.appendChild(crc_file_info_file)
    
    kom_file_entries = ''
    
    kom_compressed_file_data = ''
    
    if os.path.isdir(in_path) == True:
        for file_name in os.listdir(in_path):
            if file_name == 'crc.xml':
                continue
            
            file_path = os.path.join(in_path, file_name)
            
            if os.path.isfile(file_path):
                if len(file_name) > 60:
                    continue
                
                file_size = os.path.getsize(file_path)
                
                if file_size <= 0:
                    continue
                
                try:
                    file_object = open(file_path, 'rb')
                    
                    file_data = file_object.read()
                except IOError:
                    pass
                else:
                    try:
                        compressed_file_data = zlib.compress(file_data)
                    except zlib.error:
                        pass
                    else:
                        kom_file_entries += struct.pack('<60s3I', file_name, len(file_data), len(compressed_file_data), len(kom_compressed_file_data))
                        
                        kom_compressed_file_data += compressed_file_data
                        
                        file_data_crc32 = zlib.crc32(compressed_file_data) & 0xffffffffL # work around for issue 1202
                        
                        crc_file_info_file_item = crc.createElement("Item")
                        
                        crc_file_info_file_item.setAttribute("Name", file_name)
                        crc_file_info_file_item.setAttribute("Size", str(len(file_data)))
                        crc_file_info_file_item.setAttribute("Version", str(0))
                        crc_file_info_file_item.setAttribute("CheckSum", "%08x" % file_data_crc32)
                        
                        crc_file_info_file.appendChild(crc_file_info_file_item)
                finally:
                    if file_object is not None:
                        file_object.close()
                        
                        file_object = None
    
    if len(kom_file_entries) > 0 and len(kom_compressed_file_data) > 0:
        crc_file_data = crc.toprettyxml(indent="    ")
        
        try:
            crc_compressed_file_data = zlib.compress(crc_file_data)
        except zlib.error:
            sys.exit(2)
        else:
            kom_file_entries += struct.pack('<60s3I', "crc.xml", len(crc_file_data), len(crc_compressed_file_data), len(kom_compressed_file_data))
            
            kom_compressed_file_data += crc_compressed_file_data
        
        try:
            file_object = open(out_path, 'wb')
            
            kom_header = "KOG GC TEAM MASSFILE V.0.2."
            kom_header += struct.pack('<25x')
            kom_header += struct.pack('<2I', len(kom_file_entries) / 72, 1)
            
            file_object.write(kom_header)
            file_object.write(kom_file_entries)
            file_object.write(kom_compressed_file_data)
        finally:
            if file_object is not None:
                file_object.close()
                
                file_object = None


if __name__ == "__main__":
    main(sys.argv[1:])