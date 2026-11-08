# RoundedButton: canvas-based rounded button.
import tkinter as tk

from helpers import BG, FONT, TEXT_DARK, round_rect


class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, bg_color, command=None, width=125, height=30):
        super().__init__(parent, width=width, height=height, bg=BG,
                         highlightthickness=0, cursor="hand2")
        self.command = command
        round_rect(self, 2, 2, width - 2, height - 2, 10, fill=bg_color,
                   outline="#000000", width=2)
        self.create_text(width / 2, height / 2, text=text, fill=TEXT_DARK,
                         font=(FONT, 9, "bold"))
        self.bind("<Button-1>", self._on_click)

    def _on_click(self, _event):
        if self.command:
            self.command()