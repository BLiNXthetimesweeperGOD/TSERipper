#"Music" data handler
from libraries.helpers import LE_Integer, inMemoryFileReader
import os
import wave

#The sources are MOD files, but converting to MOD is kind of annoying.
#I have to remove unused samples and alter the pattern data to do so.
from libraries.utilities.XMLib import *

#To-do: Add Space Invaders support
#To-do: Find out what's causing the offset desync for module 4 of Pitfall before the pattern order table

def saveWAV(data, sampleRate, filename):
    pcm = bytearray()
    for byte in data:
        if byte < 128:
            pcm.append(byte+127)
        else:
            pcm.append(byte-128)
            
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    with wave.open(filename, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(1)
        wav.setframerate(sampleRate)
        wav.writeframes(pcm)

def convertMUSC(data, romName):
    MUSC = inMemoryFileReader(data)
    magic = MUSC.read(4)
    moduleTableOffset = LE_Integer(MUSC.read(4)) #Tracker modules (music)
    sampleTableOffset = LE_Integer(MUSC.read(4)) #Instruments
    effectTableOffset = LE_Integer(MUSC.read(4)) #Sound effects

    MUSC.seek(moduleTableOffset)

    moduleCount = LE_Integer(MUSC.read(4))
    for module in range(moduleCount):
        moduleOffset  = LE_Integer(MUSC.read(4))
        returnForNextModule = MUSC.tell()

        #All variables that need to be pre-defined go here
        patternOrder = []
        patternRows = 64 #Always 64
        smallestJumpBetweenPatterns = 256
        lastPatternIndex = 0
        sampleID = 0

        #End of pre-defined variable section
        
        MUSC.seek(moduleTableOffset+moduleOffset)

        unknownVariables = MUSC.read(4)
        
        patternCount, unknown, channelCount, padding = MUSC.read(4)

        xm = xmWriter(name=f"Torus Module {module}", trackerName="Torus Games (TSE)", channelCount=channelCount)
        
        patternDataStart = moduleTableOffset+moduleOffset+MUSC.read(1)[0]

        MUSC.seek(-1, 1)

        startOfPatternOrderTable = MUSC.tell()

        #I need to go through this twice
        while MUSC.tellExact() != patternDataStart: 
            #Excellent variable name, I know
            patternDataOffsetRelativeToModuleHeader = MUSC.read(1)[0]
            patternIndex = MUSC.read(1)[0]
            if patternIndex != 0:
                lastPatternIndex = patternIndex
            if lastPatternIndex < smallestJumpBetweenPatterns and lastPatternIndex != 0:
                smallestJumpBetweenPatterns = lastPatternIndex
                
        MUSC.restore(startOfPatternOrderTable)
        while MUSC.tellExact() != patternDataStart: 
            patternDataOffsetRelativeToModuleHeader = MUSC.read(1)[0]
            patternOrder.append(MUSC.read(1)[0]//smallestJumpBetweenPatterns)

        for patternIndex in range(patternCount):
            pattern = xmPattern(patternRows, channelCount)

            for row in range(patternRows):
                for channel in range(channelCount):
                    effect = MUSC.read(1)[0] >> 4
                    sample, note, effectParameter = MUSC.read(3)

                    if note != 0:
                        pattern.rows[row][channel] = xmNote(note, sample, 0, effect, effectParameter)
                    else:
                        pattern.rows[row][channel] = xmNote(0, sample, 0, effect, effectParameter)
                        
            xm.addPattern(pattern)

        xm.setOrder(patternOrder)

        MUSC.seek(sampleTableOffset)

        unknown = MUSC.read(4)

        while True:
            unused = MUSC.read(1)
            sampleOffset     = LE_Integer(MUSC.read(3))+MUSC.tellExact()-0x1000003
            sampleLength     = LE_Integer(MUSC.read(2))*2 #It's in words for those wondering what the *2 is for
            samplePitch      = (MUSC.read(1)[0] & 0xF) << 4 #Finetune
            sampleVolume     = MUSC.read(1)[0]
            sampleLoopStart  = LE_Integer(MUSC.read(2))*2
            sampleLoopLength = LE_Integer(MUSC.read(2))*2
            
            returnForNextSample = MUSC.tell()
            
            MUSC.seek(sampleOffset)
            sampleData = MUSC.read(sampleLength)
            MUSC.restore(returnForNextSample)

            pcm = []

            for byte in sampleData:
                if byte < 128:
                    pcm.append(byte)
                else:
                    pcm.append(byte-256)

            if sampleOffset < 0:
                sampleOffset = 0

            instrument = xmInstrument(name=f'Instrument_{sampleID:02}')

            if sampleLoopLength > 1: 
                loopType = 1
            else:
                loopType = 0

            sample = xmSample(name=f"SAMPLE_{sampleID:02}",
                              pcm=pcm,
                              is16Bit=False,
                              volume=sampleVolume,
                              fineTune=samplePitch,
                              panning=128,
                              relativeNote=24,
                              loopType=loopType,
                              loopStart=sampleLoopStart,
                              loopLength=sampleLoopLength)
            
            instrument.samples.append(sample)

            xm.addInstrument(instrument)

            sampleID+=1

            if sampleID >= 256:
                break

        xm.save(os.getcwd()+f"/output/{romName}/music/Torus_{module:02}.xm")
            
        MUSC.restore(returnForNextModule)

    MUSC.seek(effectTableOffset)

    soundEffectCount = MUSC.read(1)[0]
    for soundIndex in range(soundEffectCount):
        unknown = MUSC.read(4)
        soundOffset = effectTableOffset+LE_Integer(MUSC.read(3))+MUSC.tell()[1]
        soundLength = LE_Integer(MUSC.read(3))*2
        sampleRateMode = LE_Integer(MUSC.read(2)) >> 4 #Just a guess
        sampleRate = 8000 #Just setting this for now

        returnForNextSound = MUSC.tell()

        MUSC.seek(soundOffset)
        soundData = MUSC.read(soundLength)
        
        MUSC.restore(returnForNextSound)

        saveWAV(soundData, sampleRate, os.getcwd()+f'/output/{romName}/sounds/Torus_{soundIndex:04}.wav')
        
        

