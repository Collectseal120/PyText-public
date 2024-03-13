import json
import customtkinter
from tkinter import *
from tkinter import ttk
from tkinter.font import Font
from tkinter.filedialog import asksaveasfilename, askopenfilename, askdirectory
from ctkmessagebox import CTkMessagebox
import keyboard
import threading
from ctk_color_picker import AskColor
import time
import subprocess
import os
import re
import idlelib.colorizer as ic
import idlelib.percolator as ip
import darkdetect
import re


class Settings:
    def read(file, name):
        with open(file, 'r') as f:
            config = json.load(f)

        return config[name]
   

    def write(file, name, content):
        with open(file, 'r') as f:
            config = json.load(f)
            
        config[name] = content

        #write it back to the file
        with open(file, 'w') as f:
            json.dump(config, f)

class Lotfi(customtkinter.CTkEntry):
    def __init__(self, master=None, **kwargs):
        self.var = customtkinter.StringVar()
        customtkinter.CTkEntry.__init__(self, master, textvariable=self.var, **kwargs)
        self.old_value = ''
        self.var.trace('w', self.check)
        self.get, self.set = self.var.get, self.var.set

    def check(self, *args):
        if self.get().isdigit(): 
            # the current value is only digits; allow this
            self.old_value = self.get()
        else:
            # there's non-digit characters in the input; reject this 
            self.set(self.old_value)


class CustomText(Text):
    """
    Wrapper for the tkinter.Text widget with additional methods for
    highlighting and matching regular expressions.

    highlight_all(pattern, tag) - Highlights all matches of the pattern.
    highlight_pattern(pattern, tag) - Cleans all highlights and highlights all matches of the pattern.
    clean_highlights(tag) - Removes all highlights of the given tag.
    search_re(pattern) - Uses the python re library to match patterns.
    """
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        
        # sample tag
        self.tag_config("match", foreground="#ec5c27")

    def highlight(self, tag, start, end):  
        self.tag_add(tag, start, end)
    
    def highlight_all(self, pattern, tag):
        for match in self.search_re(pattern):
            self.highlight(tag, match[0], match[1])

    def clean_highlights(self, tag):
        self.tag_remove(tag, "1.0", END)

    def search_re(self, pattern):
        """
        Uses the python re library to match patterns.

        Arguments:
            pattern - The pattern to match.
        Return value:
            A list of tuples containing the start and end indices of the matches.
            e.g. [("0.4", "5.9"]
        """
        matches = []
        text = self.get("1.0", END).splitlines()
        for i, line in enumerate(text):
            for match in re.finditer(pattern, line):
                matches.append((f"{i + 1}.{match.start()}", f"{i + 1}.{match.end()}"))
        
        return matches

    def highlight_pattern(self, pattern, tag="match"):
        """
        Cleans all highlights and highlights all matches of the pattern.

        Arguments:
            pattern - The pattern to match.
            tag - The tag to use for the highlights.
        """
        #self.clean_highlights(tag)
        self.highlight_all(pattern, tag)

class TextWindow:
    unsaved = False
    file_path = ''
    close = False
    findActive = False


    

    def __init__(self, root, title, geometry, file):
        self.root = root
        self.root.title(title)
        self.root.geometry(geometry)

        customtkinter.set_appearance_mode(Settings.read(str('C:\\texteditor\\data.json'), 'mode'))

        customtkinter.set_default_color_theme(Settings.read(str('C:\\texteditor\\data.json'), 'color_theme'))


        self.entry = customtkinter.CTkEntry(master=self.root, placeholder_text="FontSize")
        self.entry.pack(padx=20, pady=5, anchor="w")
        my_menu = Menu(self.root)
        self.root.config(menu=my_menu)
        #add file menu
        keyboard.add_hotkey("ctrl+s", lambda: self.save_as(True))
        keyboard.add_hotkey("ctrl+o", lambda: self.open_file())

        keyboard.add_hotkey("ctrl+z", lambda: self.try_undo())
        keyboard.add_hotkey("ctrl+y", lambda: self.try_redo())
        keyboard.add_hotkey("ctrl+f", lambda: self.find())
        keyboard.add_hotkey("ctrl+b", lambda: threading.Thread(target=self.run, daemon=True).start())

        keyboard.add_hotkey("ctrl+v", lambda: threading.Thread(target=self.add_color_first_time, daemon=True).start())
        #keyboard.add_hotkey("ctrl+alt+8", lambda: self.auto_type(self.textbox, '[]', ))
        



        file_menu = Menu(my_menu, tearoff=False)
        my_menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New File       Ctrl+N", command=lambda:self.new_window("Untitled", "800x500", None))
        file_menu.add_command(label="Open File       Ctrl+O", command=lambda:self.open_file())
        file_menu.add_command(label="Save       Ctrl+S", command=lambda:self.save_as(True))
        file_menu.add_command(label="Save As", command=lambda:self.save_as(True))
        file_menu.add_command(label="Exit", command=lambda:self.close())

        edit_menu = Menu(my_menu, tearoff=False)
        my_menu.add_cascade(label="Edit", menu=edit_menu)

        edit_menu.add_command(label="Undo", command=lambda: self.try_undo())
        edit_menu.add_command(label="Redo", command=lambda: self.try_redo())
        edit_menu.add_command(label="Find", command=lambda: self.find())

        #add settings menu
        preference_menu = Menu(my_menu, tearoff=False)
        my_menu.add_cascade(label="Preferences", menu=preference_menu)
        #appareance menu
        appaearance_menu = Menu(preference_menu, tearoff=False)
        preference_menu.add_cascade(label="Select Color Scheme", menu=appaearance_menu)

        appaearance_menu.add_command(label="System", command=lambda: self.select_appaerance_mode("system"))
        appaearance_menu.add_command(label="Light", command=lambda: self.select_appaerance_mode("light"))
        appaearance_menu.add_command(label="Dark", command=lambda: self.select_appaerance_mode("dark"))

        #color theme menu
        color_menu = Menu(preference_menu, tearoff=False)
        preference_menu.add_cascade(label="Select Color Theme", menu=color_menu)

        color_menu.add_command(label="Blue", command=lambda: self.select_color_theme("blue"))
        color_menu.add_command(label="DarkBlue", command=lambda: self.select_color_theme("dark-blue"))
        color_menu.add_command(label="Green", command=lambda: self.select_color_theme("green"))


        custom_color = Menu(preference_menu, tearoff=False)
        color_menu.add_cascade(label="Custom", menu=custom_color)
        custom_color.add_command(label="Select Custom Color", command=lambda: self.select_color_theme("C:\\texteditor\\custom.json"))
        custom_color.add_command(label="Edit Custom Color", command=lambda: self.new_window("C:\\texteditor\\custom.json", "800x500", "C:\\texteditor\\custom.json"))

        tools_menu = Menu(my_menu, tearoff=False)
        my_menu.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Color Picker", command=self.ask_color)



        font=customtkinter.CTkFont(family='Calibri 11', size=14)



        #self.textbox = customtkinter.CTkTextbox(self.root, undo=True, xscrollcommand=False, wrap= NONE)
        self.textbox = CustomText(self.root, undo=True, wrap= NONE,bg="#414141", fg="#FFFFFF")
        self.textbox.tag_config('function', foreground="#88b3ff")
        
        self.yscroll = customtkinter.CTkScrollbar(self.textbox, width=15)
        self.yscroll.pack(side=RIGHT, fill=Y)
        self.yscroll.configure(command=self.textbox.yview)

        self.xscroll = customtkinter.CTkScrollbar(self.textbox, orientation="horizontal", height=15)
        self.xscroll.pack(side=BOTTOM, fill=X)
        self.xscroll.configure(command=self.textbox.xview)
        self.textbox["yscrollcommand"]=self.yscroll.set
        self.textbox["xscrollcommand"]=self.xscroll.set
        self.textbox.bind("<KeyRelease>", self.any_key)
        #self.textbox.bind("<KeyRelease>", lambda event: threading.Thread(target=self.color_f("blue", True), daemon=True).start())
        self.textbox.pack(pady=0, padx=15, fill="both", expand=True)
        self.textbox.configure(font=font)
        self.textbox.configure(insertbackground='white')
        self.textbox.bind("<Return>", lambda event: self.indent(event.widget))
        
        self.textbox.bind("<(>", lambda event: self.auto_type(event.widget,event.char, "()",None))
        self.textbox.bind("<)>", lambda event: self.auto_type(event.widget,event.char, None, ")"))
        self.textbox.bind("<KeyPress>", lambda event: self.auto_type(event.widget,event.char, '[]', None) if event.char == '[' else self.auto_type(event.widget,event.char, None,']' if event.char == ']' else None))
        self.textbox.bind("<\">", lambda event: self.auto_type(event.widget,event.char, "\"\"", "\""))
        self.textbox.bind("<\'>", lambda event: self.auto_type(event.widget,event.char, "\'\'", "\'"))

        self.textbox.bind("<Tab>", lambda event: self.auto_indent_key(event.widget, "add"))
        self.textbox.bind("<BackSpace>", lambda event: self.auto_indent_key(event.widget, "remove"))
        self.textbox.bind("<Button-3>", self.show_suggestions)
        self.textbox.bind("<Button-1>",lambda event: self.remove_error_line())



        self.textbox.config(insertofftime=0)

        #self.output_textbox = customtkinter.CTkTextbox(self.root, width=20)
        self.output_textbox = Text(self.root, width=20,height=10)
        self.output_textbox.pack(pady=0, padx=15, fill="x", expand=False, anchor="s")
        self.output_textbox.configure(font=font)

        cdg = ic.ColorDelegator()
        cdg.prog = re.compile(r'\b(?P<MYGROUP>tkinter)\b|' + ic.make_pat().pattern, re.S)
        cdg.idprog = re.compile(r'\s+(\w+)', re.S)

        cdg.tagdefs['MYGROUP'] = {'foreground': '#7F7F7F'}

        # These five lines are optional. If omitted, default colours are used.
        cdg.tagdefs['COMMENT'] = {'foreground': '#8c8c8c'}
        cdg.tagdefs['KEYWORD'] = {'foreground': '#d9aaff'}
        cdg.tagdefs['BUILTIN'] = {'foreground': '#88b3ff'} #6ce3ae
        cdg.tagdefs['STRING'] = {'foreground': '#87cb88'}
        cdg.tagdefs['DEFINITION'] = {'foreground': '#6ce3ae'}

        ip.Percolator(self.textbox).insertfilter(cdg)

        self.start_threads()
        if file != None:
            self.open_first_time(file)
        self.select_appaerance_mode(Settings.read(str('C:\\texteditor\\data.json'), 'mode'))
        self.root.protocol("WM_DELETE_WINDOW", lambda:self.prevent_close())
        self.root.mainloop()
        pass



    def any_key(self, event):
        threading.Thread(target=self.color_f("blue", True), daemon=True).start()
        self.remove_error_line()




    def indent(self, widget):
 
        index1 = widget.index("insert")
        index2 = "%s-%sc" % (index1, 1)
        prevIndex = widget.get(index2, index1)

        prevIndentLine = widget.index(index1 + "linestart")
        prevIndent = self.getIndex(prevIndentLine)
        amount = self.getIndex(index1)
        print(amount)
        test = ""
        test2 = ""
        for i in range(amount + 5):
            test = test + " "
        for i in range(amount):
            test2 = test2 + " "
        if prevIndex == ":":
            widget.insert(index1, "\n"+test)
            return "break"
        elif widget.get(index1+"linestart", index1+f"linestart + {amount}c") == test2:
            widget.insert(index1, "\n"+test2)
            return "break"

    def getIndex(self, index):
        print(index)
        indentAmount = 0
        
        while self.textbox.get(index+f"linestart + {indentAmount}c", index+f"linestart + {indentAmount + 5}c") == "     ":
            indentAmount += 5
        return indentAmount
        

    def highlight_text(self, args):
        print("test")
        self.textbox.clean_highlights("match")
        highlight = ["self.","." "0","1","2","3","4","5","6","7","8","9"]
        for word in highlight:
            self.textbox.highlight_pattern(rf"\b{word}\b")

    def open_file(self):
        if self.has_focus(self.root):
            path = askopenfilename(filetypes=[])
            print(path)
            if path != '':
                titlePath, titleFile = os.path.split(path)
                self.root.title(titleFile + " - " + path)
                with open(path, "r") as file:
                    text = file.read()
                    self.textbox.delete('1.0', END)
                    self.textbox.insert('1.0', text)
                    self.add_color_first_time()
                    self.file_path = path
                self.unsaved = False
                self.textbox.edit_modified(0)

    def save_as(self, check_focus):
        if check_focus == True:
            if self.has_focus(self.root):
                if self.file_path == '':
                    path = asksaveasfilename(filetypes=[])
                else:
                    path = self.file_path
                if path != '':
                    with open(path, "w") as file:
                        text = self.textbox.get('1.0', END)
                        file.write(text)
                        self.file_path = path
                    titlePath, titleFile = os.path.split(path)
                    self.root.title(titleFile + " - " + path)
                    self.unsaved = False
                    self.textbox.edit_modified(0)
        else:
            if self.file_path == '':
                path = asksaveasfilename(filetypes=[])
            else:
                path = self.file_path
            if path != '':
                with open(path, "w") as file:
                    text = self.textbox.get('1.0', END)
                    file.write(text)
                    self.file_path = path
                titlePath, titleFile = os.path.split(path)
                self.root.title(titleFile + " - " + path)
                self.unsaved = False
                self.textbox.edit_modified(0)

    def close(self):
        self.close = True
        #self.ut.join()
        #self.uf.join()
        self.root.destroy()

    def select_appaerance_mode(self, mode):
        Settings.write(f'C:\\texteditor\\data.json','mode',mode)
        customtkinter.set_appearance_mode(mode)
        if mode == "system":
            if darkdetect.isDark():
                mode = "dark"
            else:
                mode = "light"
        self.textbox.configure(insertbackground=Settings.read(f'modes\\{mode}.json', 'insertbackground'))
        self.textbox.configure(bg=Settings.read(f'modes\\{mode}.json', 'background'))
        self.textbox.configure(fg=Settings.read(f'modes\\{mode}.json', 'foreground'))
        self.output_textbox.configure(insertbackground=Settings.read(f'modes\\{mode}.json', 'insertbackground'))
        self.output_textbox.configure(bg=Settings.read(f'modes\\{mode}.json', 'background'))
        self.output_textbox.configure(fg=Settings.read(f'modes\\{mode}.json', 'foreground'))
        self.yscroll.configure(fg_color=Settings.read(f'modes\\{mode}.json', 'background'))
        self.xscroll.configure(fg_color=Settings.read(f'modes\\{mode}.json', 'background'))
    def select_color_theme(self, color):
        Settings.write('C:\\texteditor\\data.json','color_theme',color)
        customtkinter.set_default_color_theme(color)



        
    def new_window(self,title, size, file):
        print(file)
        if file == None:
            #subprocess.Popen([file, "main.pyw"])
            os.startfile("start.bat")
        else:
            subprocess.call(["start_file.bat", file], shell=True)
           # subprocess.Popen(["main.py", file]) #replace notepad.exe with the name of your executable
        #root = customtkinter.CTk()
        #TextWindow(root,title,size,file)
        #root.mainloop()


    def update_title(self):
        self.unsaved = False
        while True:
            if self.close == True:
                break
            if keyboard.read_key() != None or self.close == True:
                try:
                    if self.textbox.edit_modified():
                        if self.unsaved == False:
                            _title = self.root.title()
                            self.root.title("*"+_title+"*")
                            self.unsaved = True
                except:
                    pass

    def update_font(self):
        self._lastValue = Settings.read('C:\\texteditor\\data.json', 'fontSize')
        self.entry.insert('1', self._lastValue)
        self._font=customtkinter.CTkFont(family='Calibri 11', size=int(self._lastValue))
        self.textbox.configure(font=self._font)
        while True:
            if self.close == True:
                break
            
            if keyboard.read_key() != None or self.close == True:
                try:
                    if self.entry.get() != '':
                        if self.entry.get() != self._lastValue:
                            print(int(self.entry.get()))
                            _font=customtkinter.CTkFont(family='Calibri 11', size=int(self.entry.get()))
                            self.textbox.configure(font=_font)
                            self._lastValue = self.entry.get()
                            print(self._lastValue)
                            Settings.write('C:\\texteditor\\data.json', 'fontSize', self._lastValue)
                except:
                    pass
    def find(self):
        if self.has_focus(self.root):
            if self.findActive == False:
                self.findIndex = -1
                self.findActive = True
                self.find_frame = customtkinter.CTkFrame(self.root,width=1000,height=30)
                self.find_frame.pack(fill="x",anchor="n")
                self.find_button = customtkinter.CTkButton(self.find_frame,text="X",command=lambda: self.destroy_find(),width=20)
                self.find_button.grid(row=0,column=0,sticky="ew")
                self.find_entry = customtkinter.CTkEntry(self.find_frame, placeholder_text="Find?")
                self.find_entry.grid(row=0,column=1, padx=0)
                self.find_next = customtkinter.CTkButton(self.find_frame,text=">",command=lambda: self.find_itarate(1),width=20)
                self.find_next.grid(row=0, column=3)
                self.find_last = customtkinter.CTkButton(self.find_frame,text="<",command=lambda: self.find_itarate(-1),width=20)
                self.find_last.grid(row=0, column=2)

            

    def destroy_find(self):
        self.textbox.tag_remove('found', '1.0', END)
        self.find_button.destroy()
        self.find_entry.destroy()
        self.find_frame.destroy()
        self.findActive = False

        #self.find_text(text, 'red')
    def add_color(self):
        while 1:
            if keyboard.read_key() != None:
                try:
                    if self.findActive:
                        self.find_text(self.find_entry.get(), True)
                except:
                    pass

    def add_color_text(self):
        while True:          
            if keyboard.read_key() != None:
                try:
                    self.scan()
                    #self.add_color_to_text(["import ", " as ", "from ", "def ", " while", " if", " try", " except", " pass", "lambda", "with"], '#dcacff', 'imports')

                    #self.add_color_to_text(["!=", "=", "-", "+", "&", "@", "|", "%", " not", " or", " and"], '#ff6d62', 'conditions')
                    self.add_color_to_text(["self", " True", " None", " False"], '#ff4a38', 'DarkRed')
                    self.add_color_to_text(["IntVar", "str", "float", "bool"], '#5378cc', 'values')
                except:
                    pass
           
    def scan(self):
        start = "1.0"
        end = "end"
        mycount = IntVar(self.root)
        self.textbox.tag_remove("Blue", '1.0', END)
        self.textbox.tag_remove("Green", '1.0', END)
        self.textbox.tag_remove("grey", '1.0', END)
        self.textbox.tag_remove("lightgreen", '1.0', END)
        regex_patterns = [r"'.*'", r'#.*',r'".*"', r'\..*\(', r'♥', r'def.*\(']
 
        for pattern in regex_patterns:
            self.textbox.mark_set("start", start)
            self.textbox.mark_set("end", end)
 
            num = int(regex_patterns.index(pattern))
 
            while True:
                index = self.textbox.search(pattern, "start", "end", count=mycount, regexp = True)
 
                if index == "": break
                if (num == 5):
                    index = self.textbox.search(pattern, "start", "end", count=mycount, regexp = True)
                    self.textbox.tag_add("lightgreen", index, "%s+%sc" % (index, str(int(mycount.get()) - 1)))
                    self.textbox.tag_config("lightgreen", foreground="#68d598")
                elif (num == 4):
                    index = self.textbox.search(pattern, "start", "end", count=mycount, regexp = True)
                    self.textbox.tag_add("Blue", index, "%s+%sc" % (index, str(int(mycount.get()) - 1)))
                    self.textbox.tag_config("Blue", foreground="#5378cc")
                if (num == 3):
                    self.textbox.tag_add("Blue", index, "%s+%sc" % (index, str(int(mycount.get()) - 1)))
                    self.textbox.tag_config("Blue", foreground="#5378cc")                
                elif (num == 2):
                    self.textbox.tag_add("Green", index, "%s+%sc" % (index, mycount.get()))
                    self.textbox.tag_config("Green", foreground="#7dd97d")
                elif (num == 1):
                    self.textbox.tag_add("grey", index, index + " lineend")
                    self.textbox.tag_config("grey", foreground="#a7a7a7")
                elif (num == 0):
                    self.textbox.tag_add("Green", index, "%s+%sc" % (index, mycount.get()))
                    self.textbox.tag_config("Green", foreground="#7dd97d")
 
                self.textbox.mark_set("start", "%s+%sc" % (index, mycount.get()))





    def show_suggestions(self, event):
        # Create a custom context menu
        context_menu = Menu(self.textbox, tearoff=0)

        context_menu.add_command(label="Open Containing Folder", command=self.open_containinf_folder)

        # Display the context menu at the mouse position
        context_menu.post(event.x_root, event.y_root)




    def open_containinf_folder(self):
        projectPath, projectFile = os.path.split(self.file_path)
        os.startfile(projectPath)



                  

    def start_threads(self):
        self.ut = threading.Thread(target=lambda:self.update_title(), daemon=True)
        self.ut.start()  

        self.uf = threading.Thread(target=lambda:self.update_font(), daemon=True)
        self.uf.start()

        self.ad = threading.Thread(target=lambda:self.add_color(), daemon=True)
        self.ad.start()
    def prevent_close(self):
        if self.unsaved:
            msg = CTkMessagebox(title="Warning!", message="Do you wish to save the contents of this file?",icon="warning", option_1="Save", option_2="Dont Save", option_3="Cancel")
            responce = msg.get()

            if responce == "Cancel":
                pass
            elif responce == "Save":
                self.save_as(False)
                self.close()
            else:
                self.close()
        else:
            self.close()
    def try_undo(self):
        try: self.textbox.edit_undo()
        except:
            pass

    def try_redo(self):
        try: self.textbox.edit_redo()
        except:
            pass
        
    def open_first_time(self, _path):
        path = _path
        self.root.title(path)
        with open(path, "r") as file:
            text = file.read()
            self.textbox.delete('1.0', END)
            self.textbox.insert('1.0', text)
            self.file_path = path
        self.unsaved = False
        self.textbox.edit_modified(0)
        self.add_color_first_time()

    def has_focus(self, window):
        try: 
            return window.focus_displayof()
        except:
            return False

    def ask_color(self):
        pick_color = AskColor() # open the color picker
        color = pick_color.get() # get the color string
    def find_text(self, text, addColor):
        self.textbox.tag_remove('found', '1.0', END)
        s = text
        if s:
            idx = '1.0'
            self.findingList = []
            while 1:
                idx = self.textbox.search(s, idx, nocase=1, stopindex=END)
                print(idx)
                if not idx:
                    print("?")
                    break
                lastidx = '%s+%dc' % (idx, len(s))
                self.findingList.append(idx)
                if addColor == True:
                    self.textbox.tag_add('found', idx, lastidx)
                idx = lastidx
            self.textbox.tag_config('found', background="#ffd700")
        print(self.findingList)
    

    def find_itarate(self, value):
        self.findIndex += value
        print(self.findIndex)
        if self.findIndex > len(self.findingList) - 1:
            self.findIndex = 0
        elif self.findIndex <= 0:
            self.findIndex = len(self.findingList) - 1
        self.textbox.see(self.findingList[self.findIndex])

    def add_color_to_text(self, text, color, name):
        self.textbox.tag_remove(name, "1.0", END)
        i = 0
        while 1:
            if i >= len(text):
                break
            s = text[i]
            if s:
                idx = '1.0'
                while 1:
                    idx = self.textbox.search(s, idx, nocase=1, stopindex=END)
                        
                    if not idx:
                        break
                    lastidx = '%s+%dc' % (idx, len(s))
                    self.textbox.tag_add(name, idx, lastidx)
                    idx = lastidx
                self.textbox.tag_config(name, foreground=color)
            i += 1


    def auto_type(self, widget,char,key=None , skipkey=None):
        index1 = widget.index("insert")
        index2 = "%s+%sc" % (index1, 1)
        nextIndex = widget.get(index1, index2)
        if nextIndex == skipkey:
            widget.mark_set(INSERT, "%s+%sc" % (index1, 1))
            return "break"
        elif key != None:
            print(char)
            if char == '[':
                print("test")
                cursorPos = widget.index("insert")
                #cursorPos = self.textbox.index(CURRENT)
                widget.insert(cursorPos, "[]")
                cursorPos = "%s+%sc" % (cursorPos, 1)
                widget.mark_set(INSERT,cursorPos)
                return "break"
            else:
                cursorPos = widget.index("insert")
                print(key)
                #cursorPos = self.textbox.index(CURRENT)
                widget.insert(cursorPos, key)
                cursorPos = "%s+%sc" % (cursorPos, 1)
                widget.mark_set(INSERT,cursorPos)
                return "break"
    def auto_indent_key(self, widget, indent_type):
        index1 = widget.index("insert")
        index2 = "%s-%sc" % (index1, 5)
        if indent_type == "add":
            if self.textbox.tag_ranges("sel"):
                self.move_selection()
            else:
                widget.insert(index1, "     ")
            return "break"
        elif indent_type == "remove":
            #if there is a () delete it
            if widget.get("%s-%sc" % (index1, 1), index1) == "(":
                if widget.get(index1, "%s+%sc" % (index1, 1)) == ")":
                    widget.delete(index1, "%s+%sc" % (index1, 1))
            #if there is a "" delete it
            if widget.get("%s-%sc" % (index1, 1), index1) == "\"":
                if widget.get(index1, "%s+%sc" % (index1, 1)) == "\"":
                    widget.delete(index1, "%s+%sc" % (index1, 1))
            
            #if there is a '' delete it
            if widget.get("%s-%sc" % (index1, 1), index1) == "\'":
                if widget.get(index1, "%s+%sc" % (index1, 1)) == "\'":
                    widget.delete(index1, "%s+%sc" % (index1, 1))

            #if there is a [] delete it
            if widget.get("%s-%sc" % (index1, 1), index1) == "[":
                if widget.get(index1, "%s+%sc" % (index1, 1)) == "]":
                    widget.delete(index1, "%s+%sc" % (index1, 1))

            #self.color_f("blue", True)
            if widget.get(index2, index1) == "     ":
                widget.delete(index2, index1)
                return "break"

    def move_selection(self):
        if self.textbox.tag_ranges("sel"):
            sel_start = self.textbox.index("sel.first")
            sel_end = self.textbox.index("sel.last")
            selected_lines = self.textbox.get("sel.first linestart", "sel.last lineend").split("\n")
            indented_lines = [" " * 5 + line if line else line for line in selected_lines]
            indented_text = "\n".join(indented_lines)
            self.textbox.delete("sel.first", "sel.last")
            self.textbox.insert(sel_start, indented_text)
            new_start = sel_start
            new_end = f"{new_start}+{len(indented_text)}c"
            self.textbox.tag_remove("sel", "1.0", "end")
            self.textbox.tag_add("sel", new_start, new_end)
            self.textbox.mark_set("insert", new_end)
            return "break"

    def add_color_first_time(self):
        if self.has_focus(self.root):
            time.sleep(1)
            #self.textbox.tag_remove("function", "1.0", END)
            self.find_text(".", False)
            cursorPos = self.textbox.index("insert")
            cursorPos = cursorPos.split('.')[0]
            for i in self.findingList:
                temp = 0
            #while self.textbox.get(i, "%s+%sc" % (i, str(temp))) != "(":
                try:
                    index1 = "%s+%sc" % (i, 1)
                    index2 = "%s+%sc" % (i, 2)
                    while "(" not in self.textbox.get(index1, "%s+%sc" % (index2, temp)):
                        temp += 1
                        #print(self.textbox.get(index1, "%s+%sc" % (index2, temp)))
                        if temp > 30:
                            break
                        if "(" in self.textbox.get(index1, "%s+%sc" % (index2, temp)):
                            self.textbox.tag_add('function', index1, "%s+%sc" % (index2, temp - 1))
                        if "." in self.textbox.get(index1, "%s+%sc" % (index2, temp)) or "[" in self.textbox.get(index1, "%s+%sc" % (index2, temp)) or "\n" in self.textbox.get(index1, "%s+%sc" % (index2, temp)) or "=" in self.textbox.get(index1, "%s+%sc" % (index2, temp)) or " " in self.textbox.get(index1, "%s+%sc" % (index2, temp)):
                            break
                except:
                    #print(self.textbox.get(index1, "%s+%sc" % (index2, temp)))
                    #self.textbox.tag_remove("function", "1.0", END)
                    pass
            
        self.find_text(" ", False)
        cursorPos = self.textbox.index("insert")
        cursorPos = cursorPos.split('.')[0]
        for i in self.findingList:
            temp = 0
            #while self.textbox.get(i, "%s+%sc" % (i, str(temp))) != "(":
            try:
                index1 = "%s+%sc" % (i, 1)
                index2 = "%s+%sc" % (i, 2)
                while "(" not in self.textbox.get(index1, "%s+%sc" % (index2, temp)):
                    temp += 1
                    #print(self.textbox.get(index1, "%s+%sc" % (index2, temp)))
                    if temp > 30:
                        break
                    if "(" in self.textbox.get(index1, "%s+%sc" % (index2, temp)):
                        self.textbox.tag_add('function', index1, "%s+%sc" % (index2, temp - 1))
                    if "." in self.textbox.get(index1, "%s+%sc" % (index2, temp)) or "[" in self.textbox.get(index1, "%s+%sc" % (index2, temp)) or "\n" in self.textbox.get(index1, "%s+%sc" % (index2, temp)) or "=" in self.textbox.get(index1, "%s+%sc" % (index2, temp)) or " " in self.textbox.get(index1, "%s+%sc" % (index2, temp)):
                        break
            except:
                #print(self.textbox.get(index1, "%s+%sc" % (index2, temp)))
                #self.textbox.tag_remove("function", "1.0", END)      
                pass


    def color_f(self, color, check):
        self.find_text(".", False)
        cursorPos = self.textbox.index("insert")
        cursorPos = cursorPos.split('.')[0]
        for i in self.findingList:
            temp = 0
            if i.split('.')[0] == cursorPos: 
                #self.textbox.tag_remove("function", i+"linestart", i+"lineend")
            #while self.textbox.get(i, "%s+%sc" % (i, str(temp))) != "(":
                try:
                    index1 = "%s+%sc" % (i, 1)
                    index2 = "%s+%sc" % (i, 2)
                    while "(" not in self.textbox.get(index1, "%s+%sc" % (index2, temp)):
                        self.textbox.tag_remove("function", index1, "%s+%sc" % (index2, temp))
                        temp += 1
                        print(self.textbox.get(index1, "%s+%sc" % (index2, temp)))
                        if temp > 30:
                            break
                        if "(" in self.textbox.get(index1, "%s+%sc" % (index2, temp)):
                            self.textbox.tag_add('function', index1, "%s+%sc" % (index2, temp - 1))
                        if "." in self.textbox.get(index1, "%s+%sc" % (index2, temp)) or "[" in self.textbox.get(index1, "%s+%sc" % (index2, temp)) or "\n" in self.textbox.get(index1, "%s+%sc" % (index2, temp)) or "=" in self.textbox.get(index1, "%s+%sc" % (index2, temp)) or " " in self.textbox.get(index1, "%s+%sc" % (index2, temp)):
                            break
                except:
                    #print(self.textbox.get(index1, "%s+%sc" % (index2, temp)))
                    #self.textbox.tag_remove("function", "1.0", END)
                    pass
        
        self.find_text(" ", False)
        cursorPos = self.textbox.index("insert")
        cursorPos = cursorPos.split('.')[0]
        for i in self.findingList:
            temp = 0
            if i.split('.')[0] == cursorPos:
            #while self.textbox.get(i, "%s+%sc" % (i, str(temp))) != "(":
                try:
                    index1 = "%s+%sc" % (i, 1)
                    index2 = "%s+%sc" % (i, 2)
                    while "(" not in self.textbox.get(index1, "%s+%sc" % (index2, temp)):
                        temp += 1
                        #print(self.textbox.get(index1, "%s+%sc" % (index2, temp)))
                        if temp > 30:
                            break
                        if "(" in self.textbox.get(index1, "%s+%sc" % (index2, temp)):
                            self.textbox.tag_add('function', index1, "%s+%sc" % (index2, temp - 1))
                        if "." in self.textbox.get(index1, "%s+%sc" % (index2, temp)) or "[" in self.textbox.get(index1, "%s+%sc" % (index2, temp)) or "\n" in self.textbox.get(index1, "%s+%sc" % (index2, temp)) or "=" in self.textbox.get(index1, "%s+%sc" % (index2, temp)) or " " in self.textbox.get(index1, "%s+%sc" % (index2, temp)):
                            break
                except:
                    #print(self.textbox.get(index1, "%s+%sc" % (index2, temp)))
                    #self.textbox.tag_remove("function", "1.0", END)      
                    pass
        
    def show_error_line(self, rows):
        for row in rows:
            line = row[0]+".0"
            self.textbox.tag_config("error_line", background="red",  borderwidth=1, relief=SOLID)
            self.textbox.tag_add("error_line", line+"linestart", line+"+1line")



    def remove_error_line(self):
        index = self.textbox.index(INSERT)
        is_tag = self.tag_check("error_line", index)
        
        if is_tag:
            print("test")
            self.textbox.tag_remove("error_line", "1.0", END)


    def get_error_lines(self, text):
        s = text
        if s:
            idx = '1.0'
            self.error_list = []
            while 1:
                idx = self.output_textbox.search(s, idx, nocase=1, stopindex=END)
                print(idx)
                if not idx:
                    print("?")
                    break
                lastidx = '%s+%dc' % (idx, len(s)+2)
                string = self.output_textbox.get(idx, idx+"lineend")
                self.error_list.append(re.findall(r'\d+', string))
                idx = lastidx
            print(self.error_list)
            self.show_error_line(self.error_list)

    def tag_check(self, tag_name, line):
        # Get the line number where the cursor is located
        index = line
        line_number = int(index.split('.')[0])

        # Get the range of the current line
        line_start = f"{line_number}.0"
        line_end = f"{line_number + 1}.0"

        # Convert tag ranges to Text widget indexes
        tags_in_line = [self.textbox.index(tag_start) for tag_start in self.textbox.tag_ranges(tag_name)]

        # Check if any tags exist within the range
        tag_exists = any(line_start <= tag_start < line_end for tag_start in tags_in_line)

        # Print the result
        if tag_exists:
            return True
        else:
            return False


    def run(self):
        try:
            if self.has_focus(self.root):
                self.save_as(True)
                self.output_textbox.delete("1.0", END)
                originalPath = os.getcwd()
                projectPath, projectFile = os.path.split(self.file_path)
                print(projectPath)
                os.chdir(projectPath)
                command = ['python', '-u', self.file_path]
                self.output_textbox.delete("1.0", END)
                self.output_textbox.tag_remove('error', "1.0", END)
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
                os.chdir(originalPath)

                # Continuously read the output while the subprocess is running
                i = 0
                while process.poll() is None:
                    i += 1
                    output = process.stdout.readline()
                    # Process and use the output as desired
                    self.output_textbox.insert(str(i) + ".0", output)
                    self.output_textbox.yview_moveto(1.0)

                    # Check for error messages in the output
                    if "error" in output.lower():
                        # Handle the error as desired
                        self.output_textbox.insert("1.0", "An error occurred: " + output)
                        self.output_textbox.tag_add('error', "1.0", END)
                        self.output_textbox.tag_config('error', foreground='red')
                        self.get_error_lines("line ")

                # Check for any remaining output after the subprocess has finished
                output, _ = process.communicate()
                if output:
                    # Process and use the output as desired
                    print(output, end='')

        except Exception as e:
            # Handle the exception here
            print("An error occurred:", str(e))



            








