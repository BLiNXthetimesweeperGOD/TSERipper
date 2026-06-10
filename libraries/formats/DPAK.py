#DPAK is the container format used by most Torus GBA/Leapster/Didj games
from libraries.helpers import LE_Integer, findData

def DPAK(rom):
    wasFound, DPAKStart = findData(rom, b'DPAK')
    
    if wasFound:
        with open(rom, "rb") as cart:
            chunkData = []
            cart.seek(DPAKStart+4)
            entries = LE_Integer(cart.read(2))
            signature = cart.read(10)
            for entry in range(entries):
                chunkType   = LE_Integer(cart.read(4))
                chunkOffset = LE_Integer(cart.read(4))
                chunkSize   = LE_Integer(cart.read(4))
                chunkFlags  = LE_Integer(cart.read(4)) #Always 0, never used

                returnOffset = cart.tell()

                cart.seek(chunkOffset+DPAKStart)
                data = cart.read(chunkSize)
                
                chunkData.append(data)
                cart.seek(returnOffset)
                
        return chunkData
    return None
