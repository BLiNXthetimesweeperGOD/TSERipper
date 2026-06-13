from libraries.helpers import LE_Integer
import os
try:
    from PIL import Image
except:
    input("Error! PIL isn't installed. You can install it with 'pip install pillow'.")
    
#I made a class for PIL so I can stick to 1 coding style across the main scripts
class imageBuilder:
    def __init__(self, width, height):
        self.image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        self.width = width
        self.height = height
        self.center = (width // 2, height // 2)

    def setPixels(self, pixels): #Mainly used for tiles and bitmap-style stuff
        for y in range(self.height):
            for x in range(self.width):
                try:
                    self.image.putpixel((x, y), pixels[y * self.width + x])
                except:
                    break

    def drawPixel(self, pixel, xLocation, yLocation): #Used by the RLE formats
        self.image.putpixel((xLocation, yLocation), pixel)

    def horizontalFlip(self):
        self.image = self.image.transpose(method=Image.FLIP_LEFT_RIGHT)

    def verticalFlip(self):
        self.image = self.image.transpose(method=Image.FLIP_TOP_BOTTOM)

    def placeBlock(self, block, x, y): #Place a tile or a chunk
        self.image.paste(block, (x, y, x+block.width, y+block.height))

    def save(self, path): #Save the image
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        self.image.save(path)

#Tile functions
def readTile(reader, base, ID): #Used in multiple cases, not just GBA formats
    colorIndices = []
    
    saved = reader.tell()
    reader.seek(base+(ID*32))
    
    tileData = reader.read(32)
    
    reader.restore(saved)

    for byte in tileData:
        colorIndices.append(byte & 0xF)        #Index 1
        colorIndices.append((byte >> 4) & 0xF) #Index 2

    return colorIndices

def decodeTile(tile, colors): #Takes raw tile, outputs PIL image object
    decoded = []
    for index in tile:
        decoded.append(colors[index])

    image = imageBuilder(8, 8)
    image.setPixels(decoded)
    
    return image

def getSizeInTiles(size): #Used for the sprite format's chunks
    size = size  & 0xF
    sizeTable = {
        0:  (1, 1),
        1:  (2, 2),
        2:  (4, 4),
        3:  (8, 8),
        4:  (2, 1),
        5:  (4, 1),
        6:  (4, 2),
        7:  (8, 4),
        8:  (1, 2),
        9:  (1, 4),
        10: (2, 4),
        11: (4, 8),
        12: (0, 0), #The last few values are still set in the code but they're 0
        13: (0, 0),
        14: (0, 0),
        15: (0, 0)
    }
    return sizeTable.get(size)

#Raw size table for comparison:
"""
08 08 1x1
10 10 2x2
20 20 4x4
40 40 8x8
10 08 2x1
20 08 4x1
20 10 4x2
40 20 8x4
08 10 1x2
08 20 1x4
10 20 2x4
20 40 4x8
00 00 unused
00 00 unused
00 00 unused
00 00 unused
"""

#Color functions
def decodeBGR555(color):
    blue = (color >> 10) & 0b11111
    green= (color >>  5) & 0b11111
    red  = color & 0b11111

    red  = (red    << 3) | (red   >> 2)
    green= (green  << 3) | (green >> 2)
    blue = (blue   << 3) | (blue  >> 2)
    
    return (red, green, blue, 255)

def decodeXBGR4444(color): #The Leapster formats use this one
    red   = color         & 0xF
    green = (color >> 4)  & 0xF
    blue  = (color >> 8)  & 0xF

    red   = (red   << 4)
    green = (green << 4)
    blue  = (blue  << 4)

    return (blue, green, red, 255)

def getPalettes(GBA, offset):
    colorPalettes = []
    
    saved = GBA.tell()
    GBA.seek(offset)
    
    paletteCount = LE_Integer(GBA.read(4))
    for paletteEntry in range(paletteCount):
        palette = []
        for colorEntry in range(16):
            palette.append(decodeBGR555(LE_Integer(GBA.read(2))))
        colorPalettes.append(palette)
    GBA.restore(saved)
    
    return colorPalettes
