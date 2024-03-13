from core import Settings, Lotfi, TextWindow
import customtkinter
from tkinter import *
from tkinter import ttk
from tkinter.font import Font
from tkinter.filedialog import asksaveasfilename, askopenfilename, askdirectory
from CTkMessagebox import CTkMessagebox
import threading
import sys
import keyboard



keyboard.add_hotkey("ctrl+s", lambda: save_as())
keyboard.add_hotkey("ctrl+o", lambda: open_file())

customtkinter.set_appearance_mode(Settings.read('data.json', 'mode'))

customtkinter.set_default_color_theme(Settings.read('data.json', 'color_theme'))



root = customtkinter.CTk()
root.geometry("1400x700")
root.title("untitled")


file_path = ''

def new_window():
    test_root = customtkinter.CTk()
    TextWindow(test_root,"Color","300x500","custom.json")

def custom_color_window():
    color_edit_w = customtkinter.CTkToplevel()

def prevent_close():
    global unsaved
    if unsaved:
        msg = CTkMessagebox(title="Warning!", message="Do you wish to save the contents of this file?",icon="warning", option_1="Save", option_2="Dont Save", option_3="Cancel")
        responce = msg.get()

        if responce == "Cancel":
            pass
        elif responce == "Save":
            save_as()
            exit()
        else:
            exit()
    else:
        exit()


def select_appaerance_mode(mode):
    Settings.write('data.json','mode',mode)
    customtkinter.set_appearance_mode(mode)

def select_color_theme(color):
    Settings.write('data.json','color_theme',color)
    customtkinter.set_default_color_theme(color)

        



def close():
    sys.exit(0)

def set_file_path(path):
    global file_path
    file_path = path

def save_as():
    if has_focus(root):
        if file_path == '':
            path = asksaveasfilename(filetypes=[])
        else:
            path = file_path
        with open(path, "w") as file:
            text = textbox.get('1.0', END)
            file.write(text)
            set_file_path(path)
        root.title(path)
        global unsaved
        unsaved = False
        textbox.edit_modified(0)
    



def open_file():
    if has_focus(root):
        path = askopenfilename(filetypes=[])
        root.title(path)
        with open(path, "r") as file:
            text = file.read()
            textbox.delete('1.0', END)
            textbox.insert('1.0', text)
            set_file_path(path)
        global unsaved
        unsaved = False
        textbox.edit_modified(0)


def update_title():
    global unsaved
    unsaved = False
    while True:
        if keyboard.read_key() != None:
            if textbox.edit_modified():
                if unsaved == False:
                    _title = root.title()
                    root.title("*"+_title)
                    unsaved = True

def update_font():
    _lastValue = Settings.read('data.json', 'fontSize')
    entry.insert('1', _lastValue)
    _font=customtkinter.CTkFont(family='bold italic', size=int(entry.get()))
    textbox.configure(font=_font)
    while True:
        
        if keyboard.read_key() != None:
            if entry.get() != '':
                if entry.get() != _lastValue:
                    print(int(entry.get()))
                    _font=customtkinter.CTkFont(family='bold italic', size=int(entry.get()))
                    textbox.configure(font=_font)
                    _lastValue = entry.get()
                    print(_lastValue)
                    Settings.write('data.json', 'fontSize', _lastValue)
def has_focus(window):
        return window.focus_displayof()

entry = Lotfi(master=root, placeholder_text="FontSize")
entry.pack(padx=20, pady=5, anchor="w")

my_menu = Menu(root)
root.config(menu=my_menu)
#add file menu

file_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open       Ctrl+O", command=open_file)
file_menu.add_command(label="Save       Ctrl+S", command=save_as)
file_menu.add_command(label="Save As", command=save_as)
file_menu.add_command(label="Exit", command=close)

#add settings menu
preference_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="Preferences", menu=preference_menu)
#appareance menu
appaearance_menu = Menu(preference_menu, tearoff=False)
preference_menu.add_cascade(label="Select Color Scheme", menu=appaearance_menu)

appaearance_menu.add_command(label="System", command=lambda: select_appaerance_mode("system"))
appaearance_menu.add_command(label="Light", command=lambda: select_appaerance_mode("light"))
appaearance_menu.add_command(label="Dark", command=lambda: select_appaerance_mode("dark"))

#color theme menu
color_menu = Menu(preference_menu, tearoff=False)
preference_menu.add_cascade(label="Select Color Theme", menu=color_menu)

color_menu.add_command(label="Blue", command=lambda: select_color_theme("blue"))
color_menu.add_command(label="DarkBlue", command=lambda: select_color_theme("dark-blue"))
color_menu.add_command(label="Green", command=lambda: select_color_theme("green"))


custom_color = Menu(preference_menu, tearoff=False)
color_menu.add_cascade(label="Custom", menu=custom_color)
custom_color.add_command(label="Select Custom Color", command=lambda: select_color_theme("custom.json"))
custom_color.add_command(label="Edit Custom Color", command=lambda: new_window())



font=customtkinter.CTkFont(family='bold italic', size=14)
#global textbox
textbox = customtkinter.CTkTextbox(root)
textbox.pack(pady=10, padx=30, fill="both", expand=True)
textbox.configure(font=font)



ut = threading.Thread(target=update_title, daemon=True)
ut.start()

uf = threading.Thread(target=update_font, daemon=True)
uf.start()

root.protocol("WM_DELETE_WINDOW", prevent_close)
root.mainloop()









