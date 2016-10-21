import sys
from util import *

f = open("test.bfres", "wb")

f.write("FRES")
write32be(f,0x03040002)
write32be(f,0xFFFF0010)
f.seek(0x10)#Size Later on @ 0xC
write32be(f,0x00001000)


f.close()
