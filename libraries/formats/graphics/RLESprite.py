#Sprite format reader (RLE, pretty much exclusive to LeapFrog games)
import os
from libraries.helpers import LE_Integer, inMemoryFileReader, bitReader
from libraries.imageHelpers import *

def decompressOld(data, palettes, width, height): #Counting on Zero format
    image = imageBuilder(width, height)
    paletteIndex = 0
    x = 0
    y = 0
    
    decompressor = bitReader(data)

    try:
        for pixels in range(width*height):
            command = decompressor.readBits(3)
            
            if command <= 3: #Skip forward
                x+=(command << 5) | decompressor.readBits(5)
            elif command == 4: #Set palette index
                paletteIndex = decompressor.readBits(5) & 0xF
            elif command == 5: #Draw pixels
                length = decompressor.readBits(5)

                for pixelIndex in range(length):
                    pixelData = palettes[paletteIndex][decompressor.readBits(4)]

                    if x + pixelIndex < width and y < height:
                        image.drawPixel(pixelData, x+pixelIndex, y)
                        
                x+=length
            elif command == 6: #Go to next row
                decompressor.readBits(1)
                y+=1
                x=0
            elif command == 7: #Reset to left edge
                decompressor.readBits(1)
                x=0
    except: #It reached the end of the file, so decoding is basically done for this entry
        return image
    return image

def decompressNew(data, palettes, width, height): #NASCAR, Cars and Didji Racing format
    image = imageBuilder(width, height)
    paletteIndex = 0
    x = 0
    y = 0
    
    decompressor = bitReader(data)
    try:
        for pixels in range(width*height):
            command = decompressor.readBits(3)
            
            if command <= 1:   #Skip forward
                x+=((command << 5) | decompressor.readBits(5)) + 1
            elif command == 2 or command == 3:
                length = (((command & 1) << 5) | decompressor.readBits(5)) + 1

                for pixelIndex in range(length):
                    pixelData = palettes[paletteIndex][decompressor.readBits(4)]

                    if x + pixelIndex < width and y < height:
                        image.drawPixel(pixelData, x+pixelIndex, y)
                        
                x+=length
            elif command == 4: #Set palette index
                paletteIndex = decompressor.readBits(5) & 0xF
            elif command == 5: #Fill with single color NEEDS TESTING
                length   = decompressor.readBits(5) + 4
                pixelData= palettes[paletteIndex][decompressor.readBits(4)]

                for pixelIndex in range(length):
                    if x + pixelIndex < width and y < height:
                        image.drawPixel(pixelData, x+pixelIndex, y)
                x+=length
            elif command == 6: #Go to next row
                decompressor.readBits(1)
                y+=1
                x=0
            elif command == 7: #Reset to left edge
                decompressor.readBits(1)
                x=0
    except: #It reached the end of the file, so decoding is basically done for this entry
        return image

    return image

def decodeRLESprite(data, romName, sectionIndex, mode):
    RLE = inMemoryFileReader(data)

    magic = RLE.read(4)
    unknown = RLE.read(4)
    entryCount = LE_Integer(RLE.read(4))

    for entry in range(entryCount):
        spriteOffset = LE_Integer(RLE.read(4))
        
        returnForNextSprite = RLE.tell()

        RLE.seek(spriteOffset)
        
        unused             = RLE.read(4) #Never accessed by the games
        
        paletteOffset      = LE_Integer(RLE.read(4))+spriteOffset
        spriteHeaderOffset = LE_Integer(RLE.read(4))+spriteOffset

        RLE.seek(paletteOffset)

        palettes = []

        for palette in range(16):
            colors = []
            for color in range(16):
                colors.append(decodeXBGR4444(LE_Integer(RLE.read(2))))
            palettes.append(colors)

        RLE.seek(spriteHeaderOffset)
        
        frameIndex = 0
        while True: #There's no frame count, so brute forcing is required
            spriteWidth, spriteHeight, spriteAlignX, spriteAlignY = RLE.read(4)
            unknown = RLE.read(4)
            spriteDataOffset = LE_Integer(RLE.read(4))+spriteOffset
            endCheck = RLE.read(1)[0]
            if endCheck == 0:
                break
            else:
                RLE.seek(-1, 1)

            returnForNextFrame = RLE.tell()

            RLE.seek(spriteDataOffset)
            data = RLE.read()
            
            RLE.restore(returnForNextFrame)

            if mode == 0:
                decompressed = decompressOld(data, palettes, spriteWidth, spriteHeight)
            else:
                decompressed = decompressNew(data, palettes, spriteWidth*8, spriteHeight*8)

            try:
                decompressed.save(os.getcwd()+f"/output/{romName}/sprites/{sectionIndex:06}_{entry:04}_{frameIndex:02}.png")
            except:
                "Tried to save garbage data" #Only seems to happen when the code hits invalid data
            frameIndex+=1
            
        RLE.restore(returnForNextSprite)
