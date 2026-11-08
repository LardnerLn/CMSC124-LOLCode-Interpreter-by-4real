# RoundedPanel: the shared rounded frame (border + pill header + `body` frame).

import tkinter as tk

from helpers import BG, FONT, PANEL, TEXT_DARK, round_rect


class RoundedPanel(tk.Canvas):
    def __init__(self, parent, title, header_color, title_color=TEXT_DARK,
                 icon=None, plus_button=False, header_h=34, title_size=12, **kw):
        super().__init__(parent, bg=BG, highlightthickness=0, **kw)
        self.title = title
        self.header_color = header_color
        self.title_color = title_color
        self.icon = icon
        self.plus_button = plus_button
        self.header_h = header_h
        self.title_size = title_size

        self.body = tk.Frame(self, bg=PANEL)
        self._win = self.create_window(6, header_h + 8, anchor="nw", window=self.body)
        self.bind("<Configure>", self._redraw)

    def _redraw(self, e):
        w, h, hh = e.width, e.height, self.header_h
        self.delete("shape")
        round_rect(self, 2, 2, w - 2, h - 2, 14, fill=PANEL, outline="#000000",
                   width=2, tags="shape")
        round_rect(self, 4, 4, w - 4, 4 + hh, 12, fill=self.header_color,
                   outline=self.header_color, tags="shape")

        x = 14
        if self.icon:
            self.create_text(12, 4 + hh / 2, text=self.icon, anchor="w",
                             font=(FONT, 14), tags="shape")
            x = 40
        self.create_text(x, 4 + hh / 2, text=self.title, anchor="w",
                         fill=self.title_color, font=(FONT, self.title_size, "bold"),
                         tags="shape")

        if self.plus_button:
            bx, by = w - 26, 4 + hh / 2
            self.create_rectangle(bx - 7, by - 7, bx + 7, by + 7, outline="white",
                                  width=1, tags="shape")
            self.create_line(bx - 4, by, bx + 4, by, fill="white", tags="shape")
            self.create_line(bx, by - 4, bx, by + 4, fill="white", tags="shape")

        self.itemconfigure(self._win, width=max(w - 12, 1),
                           height=max(h - hh - 14, 1))