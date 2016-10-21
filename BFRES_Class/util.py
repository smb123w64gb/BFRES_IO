import struct,binascii
 
def readByte(file):
    return struct.unpack("B", file.read(1))[0]
 
def readu16be(file):
    return struct.unpack(">H", file.read(2))[0]
 
    
def readu32be(file):
    return struct.unpack(">I", file.read(4))[0]
 

def readfloatbe(file):
    return struct.unpack(">f", file.read(4))[0]
 

def updateDamit(file):
    file.seek(0,1)

def write32be(file,val):
    file.write(struct.pack(">I", val))
    updateDamit(file)
    
def write16be(file,val):
    file.write(struct.pack(">H", val))
    updateDamit(file)
def writeByte(file,val):
    file.write(struct.pack("B", val))
    updateDamit(file)
def writefloatbe(file,val):
    file.write(struct.pack(">f", val))
    updateDamit(file)
def writehalffloatbe(file,val):
    half = compress(val)
    file.write(struct.pack(">H", half))
    updateDamit(file)
    
def alline(file):
    currentPOS = file.tell()
    while(currentPOS % 0x10):
        file.seek(1,1)
        currentPOS = file.tell()
        
def fillIN(file):
    currentPOS = file.tell()
    while(currentPOS % 0x10):
        writeByte(file,0)
        currentPOS = file.tell()

   
def getString(file):
    result = ""
    tmpChar = file.read(1)
    while ord(tmpChar) != 0:
        result += tmpChar
        tmpChar =file.read(1)
    return result

def writeOffset(file,offset):
    cur = file.tell()
    file.seek(offset)
    write32be(file,cur - offset)
    file.seek(cur)

def writeOffData(file,offset,data):
    cur = file.tell()
    file.seek(offset)
    write32be(file,data)
    file.seek(cur)


def compress(float32):
        F16_EXPONENT_BITS = 0x1F
        F16_EXPONENT_SHIFT = 10
        F16_EXPONENT_BIAS = 15
        F16_MANTISSA_BITS = 0x3ff
        F16_MANTISSA_SHIFT =  (23 - F16_EXPONENT_SHIFT)
        F16_MAX_EXPONENT =  (F16_EXPONENT_BITS << F16_EXPONENT_SHIFT)

        a = struct.pack('>f',float32)
        b = binascii.hexlify(a)

        f32 = int(b,16)
        f16 = 0
        sign = (f32 >> 16) & 0x8000
        exponent = ((f32 >> 23) & 0xff) - 127
        mantissa = f32 & 0x007fffff

        if exponent == 128:
            f16 = sign | F16_MAX_EXPONENT
            if mantissa:
                f16 |= (mantissa & F16_MANTISSA_BITS)
        elif exponent > 15:
            f16 = sign | F16_MAX_EXPONENT
        elif exponent > -15:
            exponent += F16_EXPONENT_BIAS
            mantissa >>= F16_MANTISSA_SHIFT
            f16 = sign | exponent << F16_EXPONENT_SHIFT | mantissa
        else:
            f16 = sign
        return f16

def decompress(float16):
        s = ((float16 << 16) & 0x00000001)    # sign
        e = ((float16 & 0x00007C00) >> 10) - 16    # exponent
        f = (float16 & 0x000003ff)            # fraction

        eF = e + 127
        '''if e == 0:
            if f == 0:
                return int(s << 31)
            else:
                while not (f & 0x00000400):
                    f = f << 1
                    e -= 1
                e += 1
                f &= ~0x00000400
                #print(s,e,f)
        elif e == 31:
            if f == 0:
                return int((s << 31) | 0x7f800000)
            else:
                return int((s << 31) | 0x7f800000 | (f << 13))

        e = e + (127 -15)
        f = f << 13'''
        return ((f << 13) | (eF << 23)) | (s << 31)

def convert(s):
    str = struct.pack('I',s)
    f = struct.unpack('f',str)[0]
    return f

def readhalffloat(f):
	return convert(decompress(struct.unpack(">H", f.read(2))[0]))
