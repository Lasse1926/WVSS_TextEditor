import tkinter as tk
from tkinter import filedialog, messagebox
import os


class TextEditor(tk.Tk):

    def __init__(self):
        super().__init__()
        self._filepath = None
        self._is_modified = False
        self.title("Untitled - TextEditor")
        self.geometry("900x650")
        self.minsize(400, 300)
        self._build_status_bar()
        self._build_editor_area()
        self._build_menu()
        self._bind_shortcuts()
        self.protocol("WM_DELETE_WINDOW", self.exit_app)
        self.text.focus_set()

    # ── Layout ────────────────────────────────────────────────────────────

    def _build_editor_area(self):
        editor_frame = tk.Frame(self)
        editor_frame.pack(fill="both", expand=True)

        self.vsb = tk.Scrollbar(editor_frame, orient="vertical")
        self.vsb.pack(side="right", fill="y")

        self.hsb = tk.Scrollbar(editor_frame, orient="horizontal")
        self.hsb.pack(side="bottom", fill="x")

        self.ln_text = tk.Text(
            editor_frame, width=4, padx=4, takefocus=0,
            state="disabled", cursor="arrow",
            bg="#f0f0f0", fg="#888888",
            font=("Consolas", 11), wrap="none",
        )
        self.ln_text.pack(side="left", fill="y")
        self.ln_text.bind("<MouseWheel>", lambda e: self.text.yview_scroll(
            int(-1 * (e.delta / 120)), "units"))

        self.text = tk.Text(
            editor_frame, wrap="none", undo=True,
            autoseparators=True, maxundo=-1,
            font=("Consolas", 11), padx=4, pady=2,
            insertwidth=2,
            yscrollcommand=self._on_yscroll,
            xscrollcommand=self.hsb.set,
        )
        self.text.pack(fill="both", expand=True)
        self.hsb.config(command=self.text.xview)
        self.vsb.config(command=self._scroll_both)

        self.text.bind("<<Modified>>", self._modified_callback)
        self.text.bind("<KeyRelease>", self._update_status_bar)
        self.text.bind("<ButtonRelease-1>", self._update_status_bar)
        self._update_line_numbers()

    def _build_status_bar(self):
        self.status_var = tk.StringVar(value="Ln 1, Col 1  |  Untitled")
        bar = tk.Label(self, textvariable=self.status_var,
                       anchor="w", relief="sunken", bd=1, padx=4)
        bar.pack(side="bottom", fill="x")

    def _build_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New",        accelerator="Ctrl+N",
                              command=self.new_file)
        file_menu.add_command(label="Open...",    accelerator="Ctrl+O",
                              command=self.open_file)
        file_menu.add_command(label="Save",       accelerator="Ctrl+S",
                              command=self.save_file)
        file_menu.add_command(label="Save As...", accelerator="Ctrl+Shift+S",
                              command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo",       accelerator="Ctrl+Z",
                              command=self.edit_undo)
        edit_menu.add_command(label="Redo",       accelerator="Ctrl+Y",
                              command=self.edit_redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut",        accelerator="Ctrl+X",
                              command=self.edit_cut)
        edit_menu.add_command(label="Copy",       accelerator="Ctrl+C",
                              command=self.edit_copy)
        edit_menu.add_command(label="Paste",      accelerator="Ctrl+V",
                              command=self.edit_paste)
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", accelerator="Ctrl+A",
                              command=self.edit_select_all)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

    def _bind_shortcuts(self):
        self.bind("<Control-n>", self.new_file)
        self.bind("<Control-s>", self.save_file)
        self.bind("<Control-S>", self.save_file_as)
        self.bind("<Control-y>", self.edit_redo)
        # Bound on self.text so we can return "break" to suppress the
        # Text widget's built-in Ctrl+O handler (inserts a newline)
        self.text.bind("<Control-o>", self.open_file)
        self.text.bind("<Control-a>", self.edit_select_all)

    # ── Scroll helpers ────────────────────────────────────────────────────

    def _on_yscroll(self, first, last):
        self.vsb.set(first, last)
        self.ln_text.yview_moveto(first)

    def _scroll_both(self, *args):
        self.text.yview(*args)
        self.ln_text.yview(*args)

    # ── State helpers ─────────────────────────────────────────────────────

    def _set_title(self):
        name = os.path.basename(self._filepath) if self._filepath else "Untitled"
        prefix = "* " if self._is_modified else ""
        self.title(f"{prefix}{name} - TextEditor")

    def _modified_callback(self, event=None):
        # <<Modified>> fires twice: once when dirty becomes True,
        # and once when we reset it below — the guard stops the second firing.
        if not self.text.edit_modified():
            return
        self._is_modified = True
        self.text.edit_modified(False)
        self._set_title()
        self._update_line_numbers()

    def _update_status_bar(self, event=None):
        row, col = self.text.index(tk.INSERT).split(".")
        name = os.path.basename(self._filepath) if self._filepath else "Untitled"
        self.status_var.set(f"Ln {row}, Col {int(col) + 1}  |  {name}")

    def _update_line_numbers(self, event=None):
        self.ln_text.config(state="normal")
        self.ln_text.delete("1.0", "end")
        total = int(self.text.index("end-1c").split(".")[0])
        self.ln_text.insert("1.0", "\n".join(str(i) for i in range(1, total + 1)))
        self.ln_text.config(state="disabled")

    # ── Save guard ────────────────────────────────────────────────────────

    def _ask_save_if_dirty(self) -> bool:
        if not self._is_modified:
            return True
        name = os.path.basename(self._filepath) if self._filepath else "Untitled"
        answer = messagebox.askyesnocancel(
            "Unsaved Changes",
            f'"{name}" has unsaved changes.\nDo you want to save before continuing?',
        )
        if answer is True:
            return self.save_file()
        if answer is False:
            return True   # discard and proceed
        return False      # Cancel — abort

    def _write_file(self, path: str) -> bool:
        try:
            # 'end-1c' strips the phantom trailing newline tkinter appends internally
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.text.get("1.0", "end-1c"))
        except OSError as e:
            messagebox.showerror("Error", f"Could not save file:\n{e}")
            return False
        self.text.edit_modified(False)
        self._is_modified = False
        self._set_title()
        self._update_status_bar()
        return True

    # ── File menu actions ─────────────────────────────────────────────────

    def new_file(self, event=None):
        if not self._ask_save_if_dirty():
            return
        self.text.delete("1.0", "end")
        self.text.edit_reset()
        self.text.edit_modified(False)
        self._filepath = None
        self._is_modified = False
        self._set_title()
        self._update_status_bar()
        self._update_line_numbers()

    def open_file(self, event=None):

        if not self._ask_save_if_dirty():
            return "unsaved File"
        path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return "Path Error"
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            messagebox.showerror("Error", f"Could not open file:\n{e}")
            return "Error"
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.text.edit_reset()
        self.text.edit_modified(False)
        self._filepath = path
        self._is_modified = False
        self._set_title()
        self._update_status_bar()
        self._update_line_numbers()
        return "break"

    def save_file(self, event=None) -> bool:
        if self._filepath is None:
            return self.save_file_as()
        return self._write_file(self._filepath)

    def save_file_as(self, event=None) -> bool:
        path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=os.path.basename(self._filepath) if self._filepath else "Untitled.txt",
        )
        if not path:
            return False
        self._filepath = path
        return self._write_file(path)

    def exit_app(self, event=None):
        if self._ask_save_if_dirty():
            self.destroy()

    # ── Edit menu actions ─────────────────────────────────────────────────

    def edit_undo(self, event=None):
        try:
            self.text.edit_undo()
        except tk.TclError:
            pass

    def edit_redo(self, event=None):
        try:
            self.text.edit_redo()
        except tk.TclError:
            pass

    def edit_cut(self, event=None):
        self.text.event_generate("<<Cut>>")

    def edit_copy(self, event=None):
        self.text.event_generate("<<Copy>>")

    def edit_paste(self, event=None):
        self.text.event_generate("<<Paste>>")

    def edit_select_all(self, event=None):
        self.text.tag_add("sel", "1.0", "end")
        self.text.mark_set(tk.INSERT, "end")
        return "break"

    # ── Help ──────────────────────────────────────────────────────────────

    def show_about(self):
        messagebox.showinfo(
            "About TextEditor",
            "TextEditor v1.0\n\n"
            "A simple text editor built with Python and tkinter.\n\n"
            "Keyboard Shortcuts:\n"
            "  Ctrl+N          New\n"
            "  Ctrl+O          Open\n"
            "  Ctrl+S          Save\n"
            "  Ctrl+Shift+S    Save As\n"
            "  Ctrl+Z          Undo\n"
            "  Ctrl+Y          Redo\n"
            "  Ctrl+X/C/V      Cut / Copy / Paste\n"
            "  Ctrl+A          Select All",
        )


if __name__ == "__main__":
    app = TextEditor()
    app.mainloop()
