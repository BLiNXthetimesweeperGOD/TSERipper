#Level map decoder. Used in most games, but some games make random changes.
from libraries.formats.compression.LZB import *
from libraries.helpers import LE_Integer, inMemoryFileReader
from libraries.imageHelpers import *

#To-do: Figure out the unknown stuff using Didji Racing's debug symbols

def decodeLevelMaps(data, romName, sectionIndex):
    GBA = inMemoryFileReader(data)

    mapCount = LE_Integer(GBA.read(4))
    signature = GBA.read(4)
    unknown = GBA.read(4) #Not a pointer, might be flags or something

    for mapIndex in range(mapCount):
        mapOffset = LE_Integer(GBA.read(4))
        returnForNextMapOffset = GBA.tell()

        GBA.seek(mapOffset)

        layerCount = LE_Integer(GBA.read(2))
        flags = LE_Integer(GBA.read(2))

        GBA.seek(20, 1) #All of this is currently unknown

        for layerIndex in range(layerCount):
            paletteOffset = LE_Integer(GBA.read(4)) #LZB compressed usually

            GBA.seek(12, 1) #All of this is currently unknown

            paletteOrderTable = GBA.read(16)

            layerXSize, layerYSize = GBA.read(2)
            GBA.read(2) #Unknown

            tileDataOffset = LE_Integer(GBA.read(4)) #LZB compressed usually
            mapOffset      = LE_Integer(GBA.read(4)) #LZB compressed usually
            blockMapOffset = LE_Integer(GBA.read(4)) #LZB compressed usually

            returnForNextLayer = GBA.tell()

        GBA.restore(returnForNextMapOffset)

