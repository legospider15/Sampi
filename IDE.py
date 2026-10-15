import json
import os
import sys
import platform
import tkinter as tk
from threading import Thread
from tkinter import filedialog, ttk

import sampi

from pathlib import Path

def resource_path(relative_path):
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent

    return base_path / relative_path

KEYWORDS = sampi.lexer.KEYWORDS.keys()

PREMADE = {
    "true",
    "false",
    "none",
    "say",
    "ask",
    "abs",
    "sgn",
    "min",
    "max",
    "random",
    "len",
    "word",
    "number"
    }

DATA_TYPES = ("NUMBER", "STRING", "COMMENT")

curr_file_name = "Untitled"
curr_file_path = None

is_mac = platform.system() == "Darwin"
ui_modifier = "Command-" if is_mac else "Ctrl+"
bind_modifier = "Command" if is_mac else "Control"

def set_theme(theme):
    with open(resource_path("IDE data/themes.json"), "r", encoding="utf-8") as file:
        text = json.load(file)

    text_colors = text[f"{theme}_TEXT"]
    for name, color in text_colors.items():
        text_box.tag_configure(name, foreground=color)
    base_text_color = text_colors["OTHER"]
    text_box.config(bg=text[f"{theme}_BACKGROUND"], insertbackground=base_text_color, fg=base_text_color)
    output_box.config(bg=text[f"{theme}_BACKGROUND"], insertbackground=base_text_color, fg=base_text_color)

#=============================================================
# files
#=============================================================

def open_file(event=None):
    global curr_file_name, curr_file_path
    file_path = filedialog.askopenfilename(
        initialdir=".",
        title="Select a File",
        filetypes=[("Sampi files", "*.sampi"), ("Text files", "*.txt")]
    )

    if file_path:
        curr_file_path = file_path
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            text_box.delete("1.0", "end")
            text_box.insert("1.0", content)
            file_name = os.path.basename(file_path)

            name, extension = os.path.splitext(file_name)
            curr_file_name = name + extension
    highlight_code()

def save_file_as(event=None):
    global curr_file_name, curr_file_path
    file_path = filedialog.asksaveasfilename(
        title="Save File",
        filetypes=[("Sampi file", "*.sampi"), ("Text file", "*.txt")],
        defaultextension=".sampi",
        confirmoverwrite=True,
        initialfile=curr_file_name
    )

    if file_path:
        curr_file_path = file_path
        with open(file_path, "w", encoding="utf-8") as file:
            content = text_box.get("1.0", "end-1c")
            file.write(content)
            curr_file_name = os.path.basename(file_path)

def save_file(event=None):
    global curr_file_name, curr_file_path
    if curr_file_path:
        with open(curr_file_path, "w", encoding="utf-8") as file:
            file.write(text_box.get("1.0", "end-1c"))
    else:
        save_file_as()

def new_file(event=None):
    global curr_file_name, curr_file_path
    text_box.delete("1.0", "end")
    curr_file_name = "Untitled"
    curr_file_path = None

#=============================================================
# misc.
#=============================================================

def run(event=None):
    code = text_box.get("1.0", tk.END)

    def run_vm():
        try:
            sampi.vm_run(code)
        except Exception as e:
            error = f"{type(e).__name__}: {e}\n"
            redirector.write(error, "ERROR")
        print()

    Thread(target=run_vm, daemon=True).start()

def highlight_code():
    for tag in text_box.tag_names():
        text_box.tag_remove(tag, "1.0", "end")

    code = text_box.get("1.0", tk.END)
    tokens = sampi.lexer.lex_highlight(code)

    position = "1.0"

    for type_, value in tokens:
        start = text_box.search(value, position, stopindex="end")

        if not start:
            continue

        end = f"{start}+{len(value)}c"

        if value in KEYWORDS:
            text_box.tag_add("KEYWORD", start, end)
        elif value in PREMADE:
            text_box.tag_add("PREMADE", start, end)
        elif type_ in DATA_TYPES:
            text_box.tag_add(type_, start, end)
        elif type_ == "UNKNOWN":
            text_box.tag_add("ERROR", start, end)
        else:
            text_box.tag_add("OTHER", start, end)

        position = end

def text_changed(event):
    widget = event.widget

    if widget.edit_modified():
        highlight_code()

        text_box.edit_modified(False)

def make_auto_closer(char):
    def closure(event):
        maching_char = {'"': '"', "(": ")", "[": "]", "{": "}"}
        cursor_pos = text_box.index("insert")

        text_box.insert(cursor_pos, maching_char[char])
        text_box.insert(cursor_pos, char)

        text_box.mark_set("insert", f"{cursor_pos} + 1c")

        return "break"
    return closure

def handle_tab(event):
    text_box.insert("insert", "    ")
    return "break"

import queue

class Redirector:
    def __init__(self, text_widget, root):
        self.text_widget = text_widget
        self.root = root

        self.input_queue = queue.Queue()
        self.waiting_for_input = False
        self.input_start = "1.0"

        self.text_widget.config(state="disabled")
        self.text_widget.bind("<KeyPress>", self.on_keypress)

    # Redirect stdout / stderr
    def write(self, string, tag=None):
        if string:
            self.root.after(0, self._write, string, tag)

    def _write(self, string, tag=None):
        widget = self.text_widget
        widget.config(state="normal")

        # Insert output before the user's input.
        widget.insert(self.input_start, string, tag or ())

        # Advance the boundary past the inserted output.
        self.input_start = widget.index(
            f"{self.input_start}+{len(string)}c"
        )

        widget.see(tk.END)
        widget.config(state="disabled")

    def flush(self):
        pass

    # Redirect stdin
    def readline(self):
        self.root.after(0, self._start_input)
        return self.input_queue.get()

    def _start_input(self):
        widget = self.text_widget
        self.waiting_for_input = True
        widget.config(state="normal")

        # Input begins at the current end of the output.
        self.input_start = widget.index("end-1c")
        widget.mark_set("insert", tk.END)
        widget.focus_set()

    def on_keypress(self, event):
        widget = self.text_widget

        if not self.waiting_for_input:
            return "break"

        boundary = self.input_start

        if event.keysym == "Return":
            widget = self.text_widget
        
            # Capture only the user's input.
            value = widget.get(self.input_start, "end-1c")
        
            # Append the newline without moving existing text.
            widget.insert(tk.END, "\n")
        
            # Update the boundary to the new end.
            self.input_start = widget.index("end-1c")
        
            widget.config(state="disabled")
            self.waiting_for_input = False
        
            self.input_queue.put(value + "\n")
            return "break"

        # Protect output from Backspace and Delete.
        if event.keysym == "BackSpace":
            if widget.compare("insert", "<=", boundary):
                return "break"

        elif event.keysym == "Delete":
            if widget.compare("insert", "<", boundary):
                return "break"

        # Keep typing after the output boundary.
        elif event.char and event.char.isprintable():
            if widget.compare("insert", "<", boundary):
                widget.mark_set("insert", tk.END)

        return None

root = tk.Tk()
root.geometry("900x600")
root.title("Sampi IDE")
icon = tk.PhotoImage(file=resource_path("IDE data/sampi logo.png"))
root.iconphoto(False, icon)

root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

pane = tk.PanedWindow(root, orient=tk.VERTICAL, sashwidth=10)
pane.grid(row=0, column=0, sticky="nsew")

root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

text_box = tk.Text(
    pane,
    wrap="none",
    font=("Menlo", 14)
    )

#=============================================================
# auto type
#=============================================================

for char in ['"', "(", "[", "{"]:
    binding_function = make_auto_closer(char)
    text_box.bind(char, binding_function)

text_box.bind("<Tab>", handle_tab)

pane.add(text_box, stretch="always")

text_box.bind("<<Modified>>", text_changed)

output_box = tk.Text(pane, state="disabled", font=("Menlo", 14))
pane.add(output_box, stretch="always")
output_box.tag_configure("ERROR", foreground="#FF0000")
text_box.tag_configure("ERROR", foreground="#FF0000")

redirector = Redirector(output_box, root)
sys.stdout = redirector
sys.stdin = redirector

run_btn = ttk.Button(root, text="Run", command=run)
run_btn.grid(row=2, column=0)

menubar = tk.Menu(root)

#=============================================================
# file menu
#=============================================================

file_menu = tk.Menu(menubar, tearoff=0)
for name, command in [("Open", open_file), ("Save", save_file), ("New", new_file), ("Run", run)]:
    file_menu.add_command(
        label=name,
        accelerator=f"{ui_modifier}{name[0]}",
        command=command
        )

    root.bind_all(f"<{bind_modifier}-{name[0].lower()}>", command)

file_menu.add_command(label="Save as", accelerator=f"Shift+{ui_modifier}S", command=save_file_as)
root.bind_all(f"<Shift-{bind_modifier}-s>", save_file_as)

file_menu.add_separator()
file_menu.add_command(label="Exit", accelerator=f"{ui_modifier}E", command=lambda event=None: os._exit(0))
root.bind_all(f"<{bind_modifier}-e>", lambda event=None: os._exit(0))

root.protocol("WM_DELETE_WINDOW", lambda event=None: os._exit(0))

menubar.add_cascade(label="File", menu=file_menu)

#=============================================================
# themes menu
#=============================================================

set_theme("NIGHT")

theme_var = tk.StringVar(value="NIGHT")

theme_menu = tk.Menu(menubar, tearoff=0)

for theme in ("NIGHT", "DAY", "ECLIPSE"):
    theme_menu.add_radiobutton(
        label=theme.lower().capitalize(),
        variable=theme_var,
        value=theme,
        command=lambda t=theme: set_theme(t)
        )

menubar.add_cascade(label="Theme", menu=theme_menu)

root.config(menu=menubar)

root.mainloop()
