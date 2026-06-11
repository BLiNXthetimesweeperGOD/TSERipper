#Sprite format reader (GBA format, also used in a few Leapster games)
import os
from libraries.helpers import LE_Integer, inMemoryFileReader
from libraries.imageHelpers import *

def checkTileStart(GBA, tileDataStart): #Putting this here since it's guesswork (seems to work every time though!)
    saved = GBA.tell()
    GBA.seek(tileDataStart)
    trueTileDataOffset = tileDataStart+(LE_Integer(GBA.read(4))*4)+4
    GBA.restore(saved)
    return trueTileDataOffset

def decodeGBASprites(data, romName, sectionIndex):
    GBA = inMemoryFileReader(data)
    
    magic              = GBA.read(4)
    entryCount         = LE_Integer(GBA.read(2))
    paletteTableOffset = LE_Integer(GBA.read(2))
    tileDataStart      = LE_Integer(GBA.read(2))
    unknown            = LE_Integer(GBA.read(2))

    colorPalettes = getPalettes(GBA, paletteTableOffset)

    trueTileDataStart = checkTileStart(GBA, tileDataStart)

    for entry in range(entryCount): #Sprite offsets
        spriteOffset = LE_Integer(GBA.read(4))

        savedReturnForNextSprite = GBA.tell() #Expect lots of this

        try:
            if spriteOffset != 0:

                GBA.seek(spriteOffset)

                animationCount      = LE_Integer(GBA.read(2))
                basePaletteIDOffset = LE_Integer(GBA.read(2))
                GBA.read(4)

                returnForAnimations = GBA.tell()
                GBA.seek(spriteOffset+basePaletteIDOffset)
                
                basePaletteID = LE_Integer(GBA.read(2))
                
                GBA.restore(returnForAnimations)

                for animation in range(animationCount):
                    animationOffset = LE_Integer(GBA.read(4))
                    
                    savedReturnForNextAnimation = GBA.tell()

                    GBA.seek(spriteOffset+animationOffset)
                    frameCount, unknown = GBA.read(2)
                    playbackSpeed = LE_Integer(GBA.read(2))

                    for frame in range(frameCount):
                        frameOffset = LE_Integer(GBA.read(4))
                        GBA.read(2) #This is padding, it's always 0 (I checked)

                        savedReturnForNextFrame = GBA.tell()

                        GBA.seek(spriteOffset+animationOffset+frameOffset)
                        
                        chunkCount = LE_Integer(GBA.read(2))
                        unknown1 = LE_Integer(GBA.read(2)) #Unknown, often 0 or 1. Sometimes 2.
                        
                        unknownX, unknownY = GBA.read(2) #Seems to be related to sprite size? Canvas size, maybe?
                        alignX, alignY = GBA.read(2)
                        XSize, YSize = GBA.read(2)

                        #print(unknownX, unknownY, alignX, alignY, XSize, YSize)
                        #input()
                        
                        spriteImage = imageBuilder(XSize*8, YSize*8)
                        GBA.read(2) #Unknown - always 04? Bits per pixel maybe?
                        
                        for chunk in range(chunkCount):
                            startOfChunk = GBA.tell()[0]+GBA.tell()[1] #Possibly needed later (?)
                            
                            chunkAlignX, chunkAlignY = GBA.read(2)
                            #print(chunkAlignX, chunkAlignY)
                            chunkShape = getSizeInTiles(GBA.read(1)[0])
                            if chunkShape == None:
                                break
                            chunkPalette = GBA.read(1)[0]

                            if chunkPalette > 0xF:
                                chunkPalette = chunkPalette & 0xF
                                GBA.read(1)[0]
                            chunkPalette = chunkPalette & 0xF
                            
                            nextChunkOffset = GBA.read(1)[0]
                            GBA.read(1) #Unknown, usually 0x00, 0x08, 0x10, 0x20 or 0xCC
                            
                            chunkImage = imageBuilder(chunkShape[0]*8, chunkShape[1]*8)
                            
                            for y in range(chunkShape[1]):
                                for x in range(chunkShape[0]):
                                    tile = decodeTile(readTile(GBA, trueTileDataStart, LE_Integer(GBA.read(2))), colorPalettes[basePaletteID+chunkPalette])
                                    chunkImage.placeBlock(tile.image, x*8, y*8)

                            spriteImage.placeBlock(chunkImage.image, chunkAlignX, chunkAlignY)

                            GBA.seek(startOfChunk+nextChunkOffset)
                            
                        if chunkShape != None:
                            spriteImage.save(os.getcwd()+f"/output/{romName}/sprites/GBA/{sectionIndex:06}/{entry:04}/{animation:02}_{frame:02}.png")
                        GBA.restore(savedReturnForNextFrame)
                        
                    GBA.restore(savedReturnForNextAnimation)
        except:
            ""
            #print(hex(GBA.tell()[0]))
        GBA.restore(savedReturnForNextSprite)


