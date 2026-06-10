import struct
import math
import os

class xmNote:
    def __init__(self, note=0, instrument=0, volume=0, effectType=0, effectParam=0):
        self.note       = note
        self.instrument = instrument
        self.volume     = volume
        self.effectType = effectType
        self.effectParam = effectParam

class xmEnvelopePoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class xmSample:
    def __init__(self, name="", pcm=None, is16Bit=False, volume=64, fineTune=0,
                 panning=128, relativeNote=0, loopType=0, loopStart=0, loopLength=0):
        self.name         = name
        self.pcm          = list(pcm or [])
        self.is16Bit      = is16Bit
        self.volume       = volume
        self.fineTune     = fineTune
        self.panning      = panning
        self.relativeNote = relativeNote
        self.loopType     = loopType
        self.loopStart    = loopStart
        self.loopLength   = loopLength

class xmInstrument:
    def __init__(self, name=""):
        self.name          = name
        self.samples       = []
        self.sampleForNote = [0] * 96
        
        self.volumePoints       = []
        self.panningPoints      = []
        self.numVolumePoints    = 0
        self.numPanningPoints   = 0
        self.volumeSustain      = 0
        self.volumeLoopStart    = 0
        self.volumeLoopEnd      = 0
        self.panningSustain     = 0
        self.panningLoopStart   = 0
        self.panningLoopEnd     = 0
        self.volumeType         = 0
        self.panningType        = 0

        self.vibratoType  = 0
        self.vibratoSweep = 0
        self.vibratoDepth = 0
        self.vibratoRate  = 0

        self.volumeFadeout = 0

class xmPattern:
    def __init__(self, rowCount, channelCount):
        self.rowCount    = rowCount
        self.channelCount = channelCount
        self.rows       = [[xmNote() for _ in range(channelCount)] for _ in range(rowCount)]

class xmWriter:
    def __init__(self, name="Untitled", trackerName="FastTracker 2 compatible",
                 channelCount=4, defaultTempo=6, defaultBpm=125, linearFrequencyTable=True):
        self.name            = name
        self.trackerName     = trackerName
        self.channelCount     = channelCount
        self.defaultTempo    = defaultTempo
        self.defaultBpm      = defaultBpm
        self.linearFrequencyTable = linearFrequencyTable

        self.songLength      = 1
        self.restartPosition = 0
        self.order           = [0] * 256
        self.patterns        = []
        self.instruments     = []

    def setOrder(self, order):
        if len(order) > 256:
            print("Order length must be 256 or less.")
            return
        self.songLength = len(order)
        self.order[:len(order)] = order
        for i in range(len(order), 256):
            self.order[i] = 0

    def addPattern(self, pattern):
        if pattern.rowCount < 1 or pattern.rowCount > 256:
            print("Pattern row count must be between 1 and 256.")
            return
        self.patterns.append(pattern)

    def addInstrument(self, instrument):
        if len(instrument.samples) > 128:
            print("Instruments can't have more than 128 samples.")
            return
        self.instruments.append(instrument)

    def save(self, filename):
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        with open(filename, "wb") as f:
            f.write(self._packHeader())
            for pattern in self.patterns:
                f.write(self._packPattern(pattern))
            for instrument in self.instruments:
                f.write(self._packInstrument(instrument))

    def _packHeader(self):
        out = bytearray()
        out += b"Extended Module: "
        out += self._padAscii(self.name, 20)
        out += b"\x1A"
        out += self._padAscii(self.trackerName, 20)
        out += struct.pack("<BB", 0x04, 0x01)
        out += struct.pack("<I", 276)

        flags = 1 if self.linearFrequencyTable else 0
        out += struct.pack(
            "<HHHHHHHH",
            self.songLength,
            self.restartPosition,
            self.channelCount,
            len(self.patterns),
            len(self.instruments),
            flags,
            self.defaultTempo,
            self.defaultBpm,
        )
        out += bytes(self.order)
        return bytes(out)

    def _packPattern(self, pattern):
        packed = bytearray()
        for row in range(pattern.rowCount):
            for ch in range(self.channelCount):
                note = pattern.rows[row][ch]
                packed.append(note.note)
                packed.append(note.instrument)
                packed.append(note.volume)
                packed.append(note.effectType)
                packed.append(note.effectParam)

        patternHeader = struct.pack("<I", 9)
        patternHeader += struct.pack("<BHH", 0, pattern.rowCount, len(packed))
        return patternHeader + packed

    def _packInstrument(self, instrument):
        hdr = bytearray()
        hdr += self._padAscii(instrument.name, 22)
        hdr += struct.pack("<B", 0)
        hdr += struct.pack("<H", len(instrument.samples))

        extra = bytearray()
        if len(instrument.samples) > 0:
            extra += struct.pack("<I", 0)
            extra += bytes(instrument.sampleForNote[:96])

            for points in [instrument.volumePoints, instrument.panningPoints]:
                for i in range(12):
                    if i < len(points):
                        extra += struct.pack("<HH", points[i].x, points[i].y)
                    else:
                        extra += struct.pack("<HH", 0, 0)

            extra += struct.pack("<B", min(len(instrument.volumePoints), 12))
            extra += struct.pack("<B", min(len(instrument.panningPoints), 12))
            extra += struct.pack("<B", instrument.volumeSustain)
            extra += struct.pack("<B", instrument.volumeLoopStart)
            extra += struct.pack("<B", instrument.volumeLoopEnd)
            extra += struct.pack("<B", instrument.panningSustain)
            extra += struct.pack("<B", instrument.panningLoopStart)
            extra += struct.pack("<B", instrument.panningLoopEnd)
            extra += struct.pack("<B", instrument.volumeType)
            extra += struct.pack("<B", instrument.panningType)
            extra += struct.pack("<B", instrument.vibratoType)
            extra += struct.pack("<B", instrument.vibratoSweep)
            extra += struct.pack("<B", instrument.vibratoDepth)
            extra += struct.pack("<B", instrument.vibratoRate)
            extra += struct.pack("<H", instrument.volumeFadeout)
            extra += struct.pack("<H", 0)

            struct.pack_into("<I", extra, 0, len(extra))

        instrumentBody = bytes(hdr + extra)
        out = bytearray()
        out += struct.pack("<I", len(instrumentBody) + 4)
        out += instrumentBody

        for sample in instrument.samples:
            out += self._packSampleHeader(sample)
        for sample in instrument.samples:
            out += self._packSampleData(sample)

        return bytes(out)

    def _packSampleHeader(self, sample):
        loopBits = sample.loopType & 0x03
        typeBits  = (int(sample.is16Bit) << 4) | loopBits
        return struct.pack(
            "<IIIBBBBbB22s",
            len(sample.pcm),
            sample.loopStart,
            sample.loopLength,
            sample.volume,
            sample.fineTune,
            typeBits,
            sample.panning,
            sample.relativeNote,
            0,
            self._padAscii(sample.name, 22),
        )

    def _packSampleData(self, sample):
        out  = bytearray()
        prev = 0
        if sample.is16Bit:
            for val in sample.pcm:
                out += struct.pack("<h", val - prev)
                prev = val
        else:
            for val in sample.pcm:
                delta = max(-128, min(val - prev, 127))
                out += struct.pack("<b", delta)
                prev += delta
        return bytes(out)

    def _padAscii(self, s, size):
        b = (s or "").encode("ascii", errors="ignore")
        return b[:size].ljust(size, b"\x00")
