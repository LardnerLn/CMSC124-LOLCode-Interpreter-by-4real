# Text Editor panel. Edit only this file to change this panel.
import os
import tkinter as tk
import types
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont

from rounded_panel import RoundedPanel

# this panel's own settings
TITLE = "Text Editor"
HEADER_COLOR = "#52A3A3"
TITLE_COLOR = "#1F3B3B"
TITLE_FONT = ("Helvetica", 12, "bold")
BODY_COLOR = "#DFD6BB"
TEXT_COLOR = "#2B2B2B"
GUTTER_COLOR = "#D3C9AB"
GUTTER_TEXT_COLOR = "#8A8366"
SELECT_COLOR = "#C9BE9C"
FONT = ("Courier", 11)
TAB_SPACES = 4
DEFAULT_EXTENSION = ".lol"


class TextEditorPanel(RoundedPanel):
    def __init__(self, parent):
        super().__init__(parent, TITLE, HEADER_COLOR, title_color=TITLE_COLOR,
                         title_size=TITLE_FONT[1])

        self.current_path = None   # file currently open in the editor, or None
        self._dirty = False        # True when there are unsaved changes
        self._last_line_count = 0

        # line number gutter on the left
        self.gutter = tk.Text(self.body, width=4, bg=GUTTER_COLOR, fg=GUTTER_TEXT_COLOR,
                              relief="flat", bd=0, font=FONT, padx=6, pady=4,
                              state="disabled", takefocus=0, cursor="arrow",
                              wrap="none")
        self.gutter.pack(side="left", fill="y")
        self.gutter.tag_configure("right", justify="right")

        # vertical scrollbar on the right
        self.scrollbar = ttk.Scrollbar(self.body, orient="vertical", command=self._yview)
        self.scrollbar.pack(side="right", fill="y")

        # the editor itself
        self.text = tk.Text(self.body, bg=BODY_COLOR, fg=TEXT_COLOR,
                            insertbackground=TEXT_COLOR, selectbackground=SELECT_COLOR,
                            selectforeground=TEXT_COLOR, relief="flat", wrap="none",
                            font=FONT, undo=True, bd=0, padx=6, pady=4,
                            yscrollcommand=self._on_text_scroll)
        self.text.pack(side="left", fill="both", expand=True)
        self.text.configure(tabs=self._tab_width())

        self.text.bind("<<Modified>>", self._on_modified)
        self.text.bind("<Tab>", self._insert_tab)
        self.text.bind("<Control-s>", self._on_ctrl_s)
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>", "<Button-1>", "<B1-Motion>"):
            self.gutter.bind(seq, lambda e: "break")

        # keep the header fitted to the panel width when the window is resized
        self.bind("<Configure>", lambda e: self._refresh_header(), add="+")

        self._update_line_numbers()

    # header shows the path of the open file
    def _update_header(self):
        self._header_text = self.current_path or TITLE
        self._refresh_header()

    def _refresh_header(self):
        width = self.winfo_width()
        text = getattr(self, "_header_text", TITLE)
        if width > 60:
            text = self._fit_text(text, width - 30)
        if text != self.title:
            self.title = text
            self._redraw(types.SimpleNamespace(width=width, height=self.winfo_height()))

    @staticmethod
    def _fit_text(text, max_px):
        # Shorten from the left with an ellipsis so the end of the path stays visible.
        font = tkfont.Font(font=TITLE_FONT)
        if font.measure(text) <= max_px:
            return text
        while len(text) > 1 and font.measure("…" + text) > max_px:
            text = text[1:]
        return "…" + text

    # scrolling and line numbers
    def _yview(self, *args):
        self.text.yview(*args)
        self.gutter.yview(*args)

    def _on_text_scroll(self, first, last):
        self.scrollbar.set(first, last)
        self.gutter.yview_moveto(first)

    def _update_line_numbers(self):
        count = int(self.text.index("end-1c").split(".")[0])
        if count == self._last_line_count:
            return
        self._last_line_count = count
        self.gutter.configure(state="normal")
        self.gutter.delete("1.0", "end")
        self.gutter.insert("1.0", "\n".join(str(n) for n in range(1, count + 1)), "right")
        self.gutter.configure(state="disabled")
        self.gutter.yview_moveto(self.text.yview()[0])

    def _on_modified(self, _event):
        if self.text.edit_modified():
            self._dirty = True
            self._update_line_numbers()
            self.text.edit_modified(False)

    # typing helpers
    def _tab_width(self):
        # pixel width of one tab stop, so a tab looks like TAB_SPACES spaces
        font = tkfont.Font(font=FONT)
        return font.measure(" " * TAB_SPACES)

    def _insert_tab(self, _event):
        self.text.insert("insert", " " * TAB_SPACES)
        return "break"

    def _on_ctrl_s(self, _event):
        self.save_file()
        return "break"

    # reading and replacing the code
    def get_code(self):
        return self.text.get("1.0", "end-1c")

    def set_code(self, code):
        # Replace everything in the editor; this counts as a clean, unchanged state.
        self.text.delete("1.0", "end")
        self.text.insert("1.0", code)
        self.text.edit_reset()
        self.text.edit_modified(False)
        self.text.mark_set("insert", "1.0")
        self.text.yview_moveto(0)
        self._dirty = False
        self._update_line_numbers()

    def is_modified(self):
        return self._dirty

    # opening and saving files
    def open_file(self, path):
        # Load a file into the editor. Returns True on success.
        if not self._confirm_discard():
            return False
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                code = f.read()
        except OSError as err:
            messagebox.showerror("Cannot open file", str(err),
                                 parent=self.winfo_toplevel())
            return False
        self.set_code(code)
        self.current_path = path
        self._update_header()
        return True

    def save_file(self):
        # Save to the current file, or ask for a name if there is none yet.
        if self.current_path is None:
            return self.save_file_as()
        return self._write(self.current_path)

    def save_file_as(self):
        path = filedialog.asksaveasfilename(parent=self.winfo_toplevel(),
                                            title="Save file as",
                                            defaultextension=DEFAULT_EXTENSION,
                                            filetypes=[("LOLCode files", "*.lol"),
                                                       ("All files", "*.*")])
        if not path:  # cancelled
            return False
        if self._write(path):
            self.current_path = path
            self._update_header()
            return True
        return False

    def _write(self, path):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.get_code())
        except OSError as err:
            messagebox.showerror("Cannot save file", str(err),
                                 parent=self.winfo_toplevel())
            return False
        self._dirty = False
        return True

    def _confirm_discard(self):
        # If there are unsaved changes, ask what to do. Returns False to cancel.
        if not self._dirty:
            return True
        name = os.path.basename(self.current_path) if self.current_path else "untitled"
        answer = messagebox.askyesnocancel("Unsaved changes",
                                           f"Save changes to {name}?",
                                           parent=self.winfo_toplevel())
        if answer is None:
            return False
        if answer:
            return self.save_file()
        return True