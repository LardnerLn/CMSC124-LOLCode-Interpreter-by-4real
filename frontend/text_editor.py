# Text Editor panel
import tkinter as tk

from rounded_panel import RoundedPanel

# this panel's own settings
TITLE = "Text Editor"
HEADER_COLOR = "#52A3A3"
TITLE_COLOR = "#1F3B3B"
BODY_COLOR = "#DFD6BB"
TEXT_COLOR = "#2B2B2B"
FONT = ("Courier", 11)


class TextEditorPanel(RoundedPanel):
    def __init__(self, parent):
        super().__init__(parent, TITLE, HEADER_COLOR, title_color=TITLE_COLOR)
        self.text = tk.Text(self.body, bg=BODY_COLOR, fg=TEXT_COLOR,
                            insertbackground=TEXT_COLOR, relief="flat", wrap="none",
                            font=FONT, undo=True, bd=0, padx=6, pady=4)
        self.text.pack(fill="both", expand=True)

    def get_code(self):
        return self.text.get("1.0", "end-1c")

    def set_code(self, code):
        self.text.delete("1.0", "end")
        self.text.insert("1.0", code)
