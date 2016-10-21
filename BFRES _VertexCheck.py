import sys
import struct
import array

class Float16Compressor:
    def __init__(self):
        self.temp = 0

    def compress(self,float32):
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
    def decompress(self,h):
        s = int((h >> 15) & 0x00000001)    # sign
        e = int((h >> 10) & 0x0000001f)    # exponent
        f = int(h & 0x000003ff)            # fraction

        if e == 0:
           if f == 0:
              return int(s << 31)
           else:
              while not (f & 0x00000400):
                 f <<= 1
                 e -= 1
              e += 1
              f &= ~0x00000400
        elif e == 31:
           if f == 0:
              return int((s << 31) | 0x7f800000)
           else:
              return int((s << 31) | 0x7f800000 | (f << 13))

        e = e + (127 -15)
        f = f << 13

        return int((s << 31) | (e << 23) | f)

def readByte(file):
    return struct.unpack("B", file.read(1))[0]
 
def readu16be(file):
    return struct.unpack(">H", file.read(2))[0]
 
def readu16le(file):
    return struct.unpack("<H", file.read(2))[0]

def readu32be(file):
    return struct.unpack(">I", file.read(4))[0]
 
def readu32le(file):
    return struct.unpack("<I", file.read(4))[0]
 
def readfloatbe(file):
    return struct.unpack(">f", file.read(4))[0]
 
def readfloatle(file):
    return struct.unpack("<f", file.read(4))[0]

def readhalffloatbe(file):
    v = readu16be(file)
    #print(hex(h))
    fcomp = Float16Compressor()
    x = fcomp.decompress(v)
    str = struct.pack('I',x)
    f = struct.unpack('f',str)[0]
    return float(f)

def ReadOffset(file):
    offset = file.tell()
    return (offset + readu32be(file))

def getString(file):
    result = ""
    tmpChar = file.read(1)
    while ord(tmpChar) != 0:
        result += tmpChar
        tmpChar =file.read(1)
    return result

class fmdlh:
    def __init__(self,file):
        self.fmdl = file.read(4)
        self.fnameOff = ReadOffset(file)
        self.eofString = ReadOffset(file)
        self.fsklOff = ReadOffset(file)
        self.fvtxArrOff = ReadOffset(file)
        self.fshpIndx = ReadOffset(file)
        self.fmatIndx = ReadOffset(file)
        self.paramOff = ReadOffset(file)
        self.fvtxCount = readu16be(file)
        self.fshpCount = readu16be(file)
        self.fmatCount = readu16be(file)
        self.paramCount = readu16be(file)
class fvtxh:
    def __init__(self,file):
        self.fmdl = file.read(4)
        self.attCount = readByte(file)
        self.buffCount = readByte(file)
        self.sectIndx = readu16be(file)
        self.vertCount = readu32be(file)
        self.u1 = readu16be(file)
        self.u2 = readu16be(file)
        self.attArrOff = ReadOffset(file)
        self.attIndxOff = ReadOffset(file)
        self.buffArrOff = ReadOffset(file)
        self.padding = readu32be(file)
class fmath:
    def __init__(self,file):
        self.fmat = file.read(4)
        self.matOff = ReadOffset(file)
        self.u1 = readu32be(file)
        self.sectIndx = readu16be(file)
        self.rendParamCount = readu16be(file)
        self.texSelCount = readByte(file)
        self.texAttSelCount = readByte(file)
        self.matParamCount = readu16be(file)
        self.matParamSize = readu32be(file)
        self.u2 = readu32be(file)
        self.rendParamIndx = ReadOffset(file)
        self.unkMatOff = ReadOffset(file)
        self.shadeOff = ReadOffset(file)
        self.texSelOff = ReadOffset(file)
        self.texAttSelOff = ReadOffset(file)
        self.texAttIndxOff = ReadOffset(file)
        self.matParamArrOff = ReadOffset(file)
        self.matParamIndxOff = ReadOffset(file)
        self.matParamOff = ReadOffset(file)
        self.shadParamIndxOff = ReadOffset(file)

class fsklh:
    def __init__(self,file):
        self.fskl = file.read(4)
        self.u1 = readu16be(file)
        self.fsklType = readu16be(file)
        self.boneArrCount = readu16be(file)
        self.invIndxArrCount = readu16be(file)
        self.exIndxCount = readu16be(file)
        self.u3 = readu16be(file)
        self.boneIndxOff = ReadOffset(file)
        self.boneArrOff = ReadOffset(file)
        self.invIndxArrOff = ReadOffset(file)
        self.invMatrArrOff = ReadOffset(file)
        self.padding = readu32be(file)

class fshph:
    def __init__(self,file):
        self.fshp = file.read(4)
        self.polyNameOff = ReadOffset(file)
        self.u1 = readu32be(file)
        self.fvtxIndx = readu16be(file)
        self.fmatIndx = readu16be(file)
        self.fsklIndx = readu16be(file)
        self.sectIndx = readu16be(file)
        self.fsklIndxArrCount = readu16be(file)
        self.matrFlag = readByte(file)
        self.lodMdlCount = readByte(file)
        self.visGrpCount = readu32be(file)
        self.u3 = readfloatbe(file)
        self.fvtxOff = ReadOffset(file)
        self.lodMdlOff = ReadOffset(file)
        self.fsklIndxArrOff = ReadOffset(file)
        self.u4 = readu32be(file)
        self.visGrpNodeOff = ReadOffset(file)
        self.visGrpRangeOff = ReadOffset(file)
        self.visGrpIndxOff = ReadOffset(file)
        self.u5 = readu32be(file)

class attdata:
    def __init__(self,attName,buffIndx,buffOff,vertType):
        self.attName = attName
        self.buffIndx = buffIndx
        self.buffOff = buffOff
        self.vertType = vertType
class buffData:
    def __init__(self,buffSize,strideSize,dataOffset):
        self.buffSize = buffSize
        self.strideSize = strideSize
        self.dataOffset = dataOffset

f = open(sys.argv[1], "rb")

AllVerts = []

f.seek(5)
verNum = readByte(f)
print(verNum)
f.seek(26,1)
FileOffset = ReadOffset(f)
f.seek(FileOffset)
BlockSize = readu32be(f)
FMDLTotal = readu32be(f)
print(FMDLTotal)
f.seek(0x10,1)

for mdl in range(FMDLTotal):
    f.seek(12,1)
    FMDLOffset = ReadOffset(f)
    NextFMDL = f.tell()
    f.seek(FMDLOffset)

    GroupArray = []
    FMDLArr = []
    FVTXArr = []
    FSKLArr = []
    FMATArr = []
    FMATNameArr = []
    FSHPArr = []
    VTXAttr = []
	
    BoneArray = []
    BoneFixArray = []
    invIndxArr = []
    invMatrArr = []
    Node_Array = []

    #F_Model Header
    fmdl_info = fmdlh(f)
    FMDLArr.append(fmdl_info)
    #F_Vertex Header
    f.seek(fmdl_info.fvtxArrOff)
    print(fmdl_info.fvtxArrOff)
    for vtx in range(fmdl_info.fvtxCount):FVTXArr.append(fvtxh(f))
    f.seek(fmdl_info.fmatIndx)
    f.seek(24,1)
    #F_Material Header
    for mat in range(fmdl_info.fmatCount):
        f.seek(8,1)
        FMATNameOffset = ReadOffset(f)
        Rtn = f.tell()
        f.seek(FMATNameOffset)

        FMATNameArr.append(getString(f))
        f.seek(Rtn)

        FMATOffset = ReadOffset(f)
        Rtn = f.tell()

        f.seek(FMATOffset)
        FMATArr.append(fmath(f))
        f.seek(Rtn)
    #F_Skeleton Header
    f.seek(fmdl_info.fsklOff)
    fskl_info = fsklh(f)
    FSKLArr.append(fskl_info)

    #Node Setup
    f.seek(fskl_info.invIndxArrOff)
    for nodes in range(fskl_info.invIndxArrCount + fskl_info.exIndxCount):Node_Array.append(readu16be(f))

    #F_Shape Header
    f.seek(fmdl_info.fshpIndx + 24)
    for shp in range(fmdl_info.fshpCount):
        f.seek(12,1)
        print(hex(f.tell()))
        FSHPOffset = ReadOffset(f)
        Rtn = f.tell()

        f.seek(FSHPOffset)
        
        FSHPArr.append(fshph(f))
        f.seek(Rtn)

    #Mesh Building

    for m in range(len(FSHPArr)):
        Vert_Array = []
        Normal_Array = []
        UV_Array = []
        UV2_Array = []
        UV3_Array = []
        UV4_Array = []
        UV5_Array = []
        Face_Array = []
        Color_Array = []
        AttrArr = []
        BuffArr = []
        W1_array = []
        B1_array = []
        Weight_array = []

        f.seek(FSHPArr[m].polyNameOff)
        print(FSHPArr[m].polyNameOff)
        MeshName = getString(f)
        print(MeshName)

        f.seek(FVTXArr[FSHPArr[m].fvtxIndx].attArrOff)

        for att in range(FVTXArr[FSHPArr[m].fvtxIndx].attCount):
            AttTypeOff = ReadOffset(f)
            Rtn1 = f.tell()
            f.seek(AttTypeOff)
            AttType = getString(f)
            f.seek(Rtn1)
            buffIndx = readByte(f)
            skip = readByte(f)
            buffOff = readu16be(f)
            vertType = readu32be(f)
            AttrArr.append(attdata(AttType,buffIndx,buffOff,vertType))

        f.seek(FVTXArr[FSHPArr[m].fvtxIndx].buffArrOff)
        for buf in range(FVTXArr[FSHPArr[m].fvtxIndx].buffCount):
            f.seek(4,1)
            BufferSize = readu32be(f)
            f.seek(4,1)
            StrideSize = readu16be(f)
            f.seek(6,1)
            DataOffset = ReadOffset(f)
            BuffArr.append(buffData(BufferSize,StrideSize,DataOffset))

        if(len(BuffArr) > 1):
            for attr in range(len(AttrArr)):
                f.seek(((BuffArr[AttrArr[attr].buffIndx].dataOffset) + (AttrArr[attr].buffOff)))
                for v in range(FVTXArr[FSHPArr[m].fvtxIndx].vertCount):
                    #print("Vertexs:%i" % (FVTXArr[FSHPArr[m].fvtxIndx].vertCount))
                    VertStart = f.tell()
                    #Vertex Info
                    if(AttrArr[attr].attName == "_p0"):
                        if(AttrArr[attr].vertType == 2063):
                            #f.seek(VertStart,1)
                            vx = readhalffloatbe(f)
                            vy = readhalffloatbe(f)
                            vz = readhalffloatbe(f)
                            vw = readhalffloatbe(f)
                        elif(AttrArr[attr].vertType == 2065):
                            vx = readfloatbe(f)
                            vy = readfloatbe(f)
                            vz = readfloatbe(f)
                            vw = readfloatbe(f)
                        else:print("Unk Vertex attr:%s" % hex(AttrArr[attr].vertType))
                        f.seek(VertStart)
                        Vert_Array.append([vx,vy,vz])
                    #Color Info
                    if(AttrArr[attr].attName == "_c0"):
                        colorR = 255
                        colorG = 255
                        colorB = 255
                        if(AttrArr[attr].vertType == 2063):
                            colorR = readhalffloatbe(f) * 255
                            colorG = readhalffloatbe(f) * 255
                            colorB = readhalffloatbe(f) * 255
                            colorA = readhalffloatbe(f) * 255
                        elif(AttrArr[attr].vertType == 10):
                            colorR = readByte(f)
                            colorG = readByte(f)
                            colorB = readByte(f)
                            colorA = readByte(f)
                        else:print("Unk Color attr:%s" % hex(AttrArr[attr].vertType))
                        Color_Array.append([colorR,colorG,colorB])
                        f.seek(VertStart)
                    #UV Info
                    if(AttrArr[attr].attName == "_u0"):
                        tu = 0
                        tv = 0
                        if(AttrArr[attr].vertType == 4):
                            tu = float(readByte(f))/255
                            tv = float(readByte(f))/255
                        elif(AttrArr[attr].vertType == 7):
                            tu = (float(readu16be(f))/65535)
                            tv = ((float(readu16be(f))/65535)*-1) + 1
                        elif(AttrArr[attr].vertType == 519):
                            tu = (float(readu16be(f))/32767)
                            tv = ((float(readu16be(f))/32767)*-1) + 1
                        elif(AttrArr[attr].vertType == 2056):
                            tu = readhalffloatbe(f)
                            tv = readhalffloatbe(f) * -1
                        elif(AttrArr[attr].vertType == 2061):
                            tu = readfloatbe(f)
                            tv = (readfloatbe(f) * -1) + 1
                        else:print("Unk UV attr:%s" % hex(AttrArr[attr].vertType))
                        UV_Array.append([tu,tv])
                        f.seek(VertStart)
                    f.seek(BuffArr[AttrArr[attr].buffIndx].strideSize,1)
        else:
            f.seek(BuffArr[0].dataOffset)
            for v in range(FVTXArr[FSHPArr[m].fvtxIndx].vertCount):
                
                VertStart = f.tell()
                for attr in range(len(AttrArr)):
                    #Vertex Info
                    if(AttrArr[attr].attName == "_p0"):
                        f.seek(AttrArr[attr].buffOff, 1)
                        if(AttrArr[attr].vertType == 2063):
                            vx = readhalffloatbe(f)
                            vy = readhalffloatbe(f)
                            vz = readhalffloatbe(f)
                        elif(AttrArr[attr].vertType == 2065):
                            vx = readfloatbe(f)
                            vy = readfloatbe(f)
                            vz = readfloatbe(f)
                        else:print("Unk Vertex attr:%s" % hex(AttrArr[attr].vertType))
                        f.seek(VertStart)
                        Vert_Array.append([vx,vy,vz])
                    #Color Info
                    if(AttrArr[attr].attName == "_c0"):
                        colorR = 255
                        colorG = 255
                        colorB = 255
                        f.seek(AttrArr[attr].buffOff, 1)
                        if(AttrArr[attr].vertType == 2063):
                            colorR = readhalffloatbe(f) * 255
                            colorG = readhalffloatbe(f) * 255
                            colorB = readhalffloatbe(f) * 255
                            colorA = readhalffloatbe(f) * 255
                        elif(AttrArr[attr].vertType == 10):
                            colorR = readByte(f)
                            colorG = readByte(f)
                            colorB = readByte(f)
                            colorA = readByte(f)
                        else:print("Unk Color attr:%s" % hex(AttrArr[attr].vertType))
                        Color_Array.append([colorR,colorG,colorB])
                        f.seek(VertStart)
                    #UV Info
                    if(AttrArr[attr].attName == "_u0"):
                        tu = 0
                        tv = 0
                        f.seek(AttrArr[attr].buffOff, 1)
                        if(AttrArr[attr].vertType == 4):
                            tu = float(readByte(f))/255
                            tv = float(readByte(f))/255
                        elif(AttrArr[attr].vertType == 7):
                            tu = (float(readu16be(f))/65535)
                            tv = ((float(readu16be(f))/65535)*-1) + 1
                        elif(AttrArr[attr].vertType == 519):
                            tu = (float(readu16be(f))/32767)
                            tv = ((float(readu16be(f))/32767)*-1) + 1
                        elif(AttrArr[attr].vertType == 2056):
                            tu = readhalffloatbe(f)
                            tv = readhalffloatbe(f) * -1
                        elif(AttrArr[attr].vertType == 2061):
                            tu = readfloatbe(f)
                            tv = (readfloatbe(f) * -1) + 1
                        else:print("Unk UV attr:%s" % hex(AttrArr[attr].vertType))
                        UV_Array.append([tu,tv])
                        f.seek(VertStart)
                f.seek(BuffArr[0].strideSize,1)
        AllVerts.append(Vert_Array)
    f.seek(NextFMDL)
print(len(Vert_Array))
for Poly in AllVerts:
    for cords in Poly:
        print("X:%.2f,Y:%.2f,Z:%.2f" % (cords[0],cords[1],cords[2]))
f.close()
