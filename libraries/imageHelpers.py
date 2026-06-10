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
                self.image.putpixel((x, y), pixels[y * self.width + x])

    def horizontalFlip(): #To-do (needed for level map rips)
        ""

    def verticalFlip(): #To-do (needed for level map rips)
        ""

    def placeBlock(self, block, x, y): #Place a tile or a chunk
        self.image.paste(block, (x, y))

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
        
    }
    return sizeTable.get(size)

#Color functions
def decodeBGR555(color):
    blue = (color >> 10) & 0b11111
    green= (color >>  5) & 0b11111
    red  = color & 0b11111

    red  = (red    << 3) | (red   >> 2)
    green= (green  << 3) | (green >> 2)
    blue = (blue   << 3) | (blue  >> 2)
    
    return (red, green, blue, 255)

def decodeBGRX4444(color): #The Leapster formats use this one
    red   = color >> 4    & 0xF
    green = (color >> 8)  & 0xF
    blue  = (color >> 12) & 0xF

    red   = (red   << 4) | red
    green = (green << 4) | green
    blue  = (blue  << 4) | blue

    return (red, green, blue, 255)

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
