#Level map decoder. Used in most games, but some games make random changes.
from libraries.formats.compression.LZB import *
from libraries.helpers import LE_Integer, inMemoryFileReader
from libraries.imageHelpers import *

#To-do: Figure out the unknown stuff using MAME's debugger
#Also figure out LZW compression - it was removed really early on
def getAndDecompressData(GBA, offset):
    GBA.seek(offset)
    data = GBA.read()
    if data.startswith(b'ZB'):
        decompressor = LZBDecompressor()
        data = decompressor.TSE_UnpackLzb(data)
    elif data.startswith(b'ZW'): #Not implemented yet - needs to be researched
        #My best guess is that it's a word-based version of LZB
        #Interestingly, blank LZW blocks appear in the Leapster games.
        #The LZW function is just this in them:
        
        #Unpack_Lzw:
        #    mov_s      r0,0x0
        #    j_s        blink

        #They literally just return 0 when detected by Unpack_AnyType.
        #Nothing else. As such, the *much* easier to reverse engineer
        #Leapster games are useless here.
        return None
    return data

def decodeBlockMap(blockMapData, tiles, palettes, paletteOrderTable):
    blocks = []
    blockReader = inMemoryFileReader(blockMapData)
    for blockIndex in range(len(blockMapData)//32):
        blockImage = imageBuilder(32, 32)
        for y in range(4):
            for x in range(4):
                tileInfo = LE_Integer(blockReader.read(2))

                paletteIndex = (paletteOrderTable[tileInfo >> 12])

                horizontalFlip = (tileInfo >> 10) & 1
                verticalFlip   = (tileInfo >> 11) & 1

                tileIndex = tileInfo & 0b1111111111

                tile = decodeTile(tiles[tileIndex], palettes[paletteIndex])

                if horizontalFlip:
                    tile.horizontalFlip()
                if verticalFlip:
                    tile.verticalFlip()

                blockImage.placeBlock(tile.image, x*8, y*8)

                #Revert the flips
                if horizontalFlip:
                    tile.horizontalFlip()
                if verticalFlip:
                    tile.verticalFlip()

        blocks.append(blockImage)
    return blocks

def decodeLevelMap(levelMapData, blocks, width, height):
    mapReader = inMemoryFileReader(levelMapData)
    levelImage = imageBuilder(width*32, height*32)
    for y in range(height):
        for x in range(width):
            mapInfo = LE_Integer(mapReader.read(2))

            horizontalFlip = (mapInfo >> 14) & 1
            verticalFlip   = (mapInfo >> 15) & 1

            blockID = mapInfo & 0b1111111111
            if blockID in range(len(blocks)):
                block = blocks[blockID]

                if horizontalFlip:
                    block.horizontalFlip()
                if verticalFlip:
                    block.verticalFlip()

                levelImage.placeBlock(block.image, x*32, y*32)

                #Revert the flips
                if horizontalFlip:
                    block.horizontalFlip()
                if verticalFlip:
                    block.verticalFlip()
                
    return levelImage   
    
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
            if layerIndex == 0:
                paletteOffset = LE_Integer(GBA.read(4)) #LZB compressed usually
            else:
                GBA.read(4)

            GBA.seek(12, 1) #All of this is currently unknown

            paletteOrderTable = GBA.read(16)
                
            layerXSize, layerYSize = GBA.read(2)
            
            GBA.read(2) #Unknown

            tileDataOffset = LE_Integer(GBA.read(4)) #LZB compressed usually
            mapOffset      = LE_Integer(GBA.read(4)) #LZB compressed usually
            blockMapOffset = LE_Integer(GBA.read(4)) #LZB compressed usually

            returnForNextLayer = GBA.tell()

            paletteData  = getAndDecompressData(GBA, paletteOffset)
            tileData     = getAndDecompressData(GBA, tileDataOffset)
            mapData      = getAndDecompressData(GBA, mapOffset)
            blockMapData = getAndDecompressData(GBA, blockMapOffset)

            tiles = []
            palettes = []

            try:
                if tileData != None and tileData != b'':
                    paletteReader = inMemoryFileReader(paletteData)
                    tileReader = inMemoryFileReader(tileData)
                    for palette in range(16):
                        colors = []
                        for color in range(16):
                            colors.append(decodeBGR555(LE_Integer(paletteReader.read(2))))
                        palettes.append(colors)

                    for tileIndex in range(len(tileData)//32):
                        tiles.append(readTile(tileReader, 0, tileIndex))
                        
                    blocks = decodeBlockMap(blockMapData, tiles, palettes, paletteOrderTable)
                    level  = decodeLevelMap(mapData, blocks, layerXSize, layerYSize)

                    level.save(os.getcwd()+f"/output/{romName}/maps/{sectionIndex:06}/{mapIndex:03}_{layerIndex}.png")
            except:
                print(f"Layer {layerIndex} of map {mapIndex} from section {sectionIndex} failed to convert.")
            GBA.restore(returnForNextLayer)

            

        GBA.restore(returnForNextMapOffset)

