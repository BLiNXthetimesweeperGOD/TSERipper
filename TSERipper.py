#Torus Games GBA/DS/Leapster/Didj (and maybe N-Gage) ripping tool
from libraries.helpers import *
from libraries.formats.DPAK import *
from libraries.formats.audio.MUSC import *
from libraries.formats.graphics.GBASprite import *
from libraries.formats.graphics.RLESprite import *

try:
    from libraries.formats.NDS import *
except:
    print("Run pip install ndspy in CMD for DS ROM support")

#Set the current working directory
#(because Python defaults to System32 now when scripts are ran directly for some reason)
scriptPath = os.path.dirname(os.path.abspath(__file__))
os.chdir(scriptPath)

files = dialog("files").paths

index = 0

for file in files:
    romName = os.path.basename(file).split(".")[0]
    if "gba" in file.lower() or "bin" in file.lower():
        sectionData = DPAK(file)
        if sectionData:
            for section in sectionData:
                #print(section[0:4])
                if section.startswith(b'MUSC'): #Music (GBA-exclusive, MOD-based)
                    convertMUSC(section, romName)
                if section.startswith(b'\x03\x00\x01\x00') or section.startswith(b'\x04\x00\x01\x00'):
                    decodeGBASprite(section, romName, index)
                if section.startswith(b'SPRT'):
                    if "numbers" in file.lower() or "zero" in file.lower() or "zro" in file.lower():
                        decodeRLESprite(section, romName, index, 0)
                    else:
                        decodeRLESprite(section, romName, index, 1)
                index+=1
                    
    if "nds" in file.lower():
        DSFiles = NDS(file)
        for entry in DSFiles:
            if "sprites" in entry:
                if DSFiles[entry].startswith(b'\x04\x00\x01\x00'):
                    decodeGBASprite(DSFiles[entry], romName, index)
            index+=1
    
    


