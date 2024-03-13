from core import Settings, Lotfi, TextWindow
import customtkinter as ctk
import sys
import os
import ctypes
from ctypes import windll
from tkinterdnd2 import DND_FILES, TkinterDnD


root = TkinterDnD.Tk()   
try:
    title = str(sys.argv[1])
    path, file = os.path.split(title)
    newTitle = file + " - " + title
    TextWindow(root,newTitle , "800x500", sys.argv[1]) 
except:
    TextWindow(root, "Untitled", "800x500", None)
    


root.mainloop()