import ndspy.rom

def NDS(ROM):
    files = {}
    rom = ndspy.rom.NintendoDSRom.fromFile(ROM)
    for fileID, fileData in enumerate(rom.files):
        files[str(rom.filenames[fileID])] = fileData
    return files
