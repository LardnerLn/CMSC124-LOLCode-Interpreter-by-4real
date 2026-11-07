# Execute/Run and Clear Output buttons. Edit only this file to change the buttons.
import tkinter as tk

from rounded_button import RoundedButton

BAR_BG = "#262626"
RUN_COLOR = "#E88E1F"
CLEAR_COLOR = "#DFD6BB"


class ButtonBar(tk.Frame):
    def __init__(self, parent, on_execute=None, on_clear=None):
        super().__init__(parent, bg=BAR_BG)
        RoundedButton(self, "Clear Output", CLEAR_COLOR, on_clear).pack(side="right")
        RoundedButton(self, "Execute/Run", RUN_COLOR, on_execute).pack(
            side="right", padx=(0, 14))
