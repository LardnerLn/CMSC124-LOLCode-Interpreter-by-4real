# Symbol Table panel
from tkinter import ttk

from rounded_panel import RoundedPanel

# this panel's own settings
TITLE = "Symbol Table"
HEADER_COLOR = "#E88E1F"
TITLE_COLOR = "#2B2B2B"
BODY_COLOR = "#DFD6BB"
TEXT_COLOR = "#2B2B2B"
SELECT_COLOR = "#C9BE9C"
FONT = ("Helvetica", 8, "bold")
COLUMNS = ("identifier", "value")
HEADINGS = ("Identifier", "Value")
SHOW_HEADINGS = False  # set True to show column headings


class SymbolTablePanel(RoundedPanel):
    def __init__(self, parent):
        super().__init__(parent, TITLE, HEADER_COLOR, title_color=TITLE_COLOR)

        style = ttk.Style()
        style.configure("Symbols.Treeview", background=BODY_COLOR,
                        fieldbackground=BODY_COLOR, foreground=TEXT_COLOR,
                        borderwidth=0, rowheight=20, font=FONT)
        style.configure("Symbols.Treeview.Heading", background=HEADER_COLOR,
                        foreground=TEXT_COLOR, font=("Helvetica", 9, "bold"))
        style.map("Symbols.Treeview", background=[("selected", SELECT_COLOR)],
                  foreground=[("selected", TEXT_COLOR)])
        style.layout("Symbols.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        self.table = ttk.Treeview(self.body, style="Symbols.Treeview",
                                  columns=COLUMNS,
                                  show="headings" if SHOW_HEADINGS else "")
        for col, text in zip(COLUMNS, HEADINGS):
            self.table.heading(col, text=text)
            self.table.column(col, anchor="w", width=100)
        self.table.pack(fill="both", expand=True)

    def clear(self):
        self.table.delete(*self.table.get_children())

    def add_row(self, identifier, value):
        self.table.insert("", "end", values=(identifier, value))
