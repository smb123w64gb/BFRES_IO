import sys
from util import *

class Header(object):
    def __init__(self):
        self.magic = "FRES"
        self.topVertion = 3
        self.botVertion = 4
        self.boneVertion = 4
        self.endian = 0xFEFF
        self.unk0 = 0x10
        self.alinement = 0x2000
        self.fileName = "Test"
    def write(self,file):
        file.write(self.magic)
        writeByte(file,self.topVertion)
        writeByte(file,self.botVertion)
        write16be(file,self.boneVertion)
        write16be(file,self.endian)
        write16be(file,self.unk0)
        file.seek(4,1)
        #add a bit for adding new stringPoiterEntry!
        file.seek(0x5C,1)
        
        
