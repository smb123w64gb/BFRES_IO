import sys
import struct
import array
import math


def readu32be(file):
    return struct.unpack(">I", file.read(4))[0]
 
def ReadOffset(file):
    offset = file.tell()
    return (offset + readu32be(file))

def getString(file):
    result = ""
    strLen = readu32be(file)
    offset = file.tell()
    if(strLen<4):
        padd = 4 - strLen
    else:
        padd = 4 - (strLen - int(strLen/4)*4)
    for x in range(strLen):
        result += file.read(1).decode("ASCII")
    f.seek(padd,1)
    return [offset,result]

def findString(offset,curOffset,array):
    for id in array:
        if id[0] == offset:
            print("%s:%s" %(hex(f.tell()).replace("L",""),id[1]))

StringOffsets = []

f = open(sys.argv[1], "rb")


f.seek(0x18)
StringArrayLen = readu32be(f)
StringOffset = ReadOffset(f)
f.seek(StringOffset)
while f.tell() - StringOffset < StringArrayLen:
    StringOffsets.append(getString(f))
f.seek(0)
while f.tell() < StringOffset:
    findString(ReadOffset(f),f.tell(),StringOffsets)



f.close()
