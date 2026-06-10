#For the file dialogs
import tkinter as tk
from tkinter import filedialog

import os
    
class inMemoryFileReader:
    def __init__(self, data, baseOffset=0):
        self.dataStream = data

        #Where our current base is in the file - start and seek relative to here
        self.baseOffset = baseOffset
        self.currentOffset = 0
        
    def read(self, size):
        data = self.dataStream[self.baseOffset+self.currentOffset:self.baseOffset+self.currentOffset+size]
        self.currentOffset+=size
        return data

    def seek(self, offset, seekType=0): #Move or update baseOffset
        if seekType == 0:   #Relative to file start (update base, reset current)
            self.baseOffset = offset
            self.currentOffset = 0
        elif seekType == 1: #Relative to current position
            self.currentOffset += offset
        elif seekType == 2: #Relative to base
            self.currentOffset = self.baseOffset+offset
        else:
            print("Invalid option, please enter 0, 1 or 2.")

    def tell(self):
        return [self.baseOffset, self.currentOffset]

    def tellExact(self):
        return self.baseOffset+self.currentOffset

    def restore(self, offsets): #Return to a saved point
        self.baseOffset = offsets[0]
        self.currentOffset = offsets[1]

def LE_Integer(data, mode=0, length=0):
    if mode == 0:
        value = 0
        index = 0
        for byte in data:
            value |= (byte << (8 * index))
            index+=1
    else: #For packing bytes, used in the XM converter
        value = bytearray()
        for byte in range(length):
            value.append((data>>(8*byte))&0xFF)
    return value

class dialog:
    def __init__(self, mode):
        self.root = tk.Tk()
        self.root.withdraw()
        self.paths = ""
        if mode.lower() == "file":
            self.file()
        elif mode.lower() == "files":
            self.files()
        elif mode.lower() == "folder":
            self.folder()
        else:
            print("You entered an invalid mode. Please enter one of the following:\nfile\nfiles\nfolder")

    def file(self):
        self.paths = filedialog.askopenfilename()
        self.root.destroy()
    
    def files(self):
        self.paths = filedialog.askopenfilenames()
        self.root.destroy()

    def folder(self):
        self.paths = filedialog.askdirectory()
        self.root.destroy()

def findData(path, string):
    with open(path, 'rb') as file:
        content = file.read()
        offset = content.find(string)
        return string in content, offset
