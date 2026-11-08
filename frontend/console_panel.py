# Console panel
import tkinter as tk

from rounded_panel import RoundedPanel

TITLE = "Console"
HEADER_COLOR = "#FF6B2C"
TITLE_COLOR = "#000000"
BODY_COLOR = "#DFD6BB"
TEXT_COLOR = "#2B2B2B"
FONT = ("Courier", 10)


class ConsolePanel(RoundedPanel):
    def __init__(self, parent):
        super().__init__(parent, TITLE, HEADER_COLOR, title_color=TITLE_COLOR,
                         title_size=13, header_h=36, height=210)
        self.text = tk.Text(self.body, bg=BODY_COLOR, fg=TEXT_COLOR, relief="flat",
                            font=FONT, state="disabled", bd=0, padx=6, pady=4)
        self.text.pack(fill="both", expand=True)

    def write(self, message):
        self.text.configure(state="normal")
        self.text.insert("end", message)
        self.text.configure(state="disabled")

    def clear(self):
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")
