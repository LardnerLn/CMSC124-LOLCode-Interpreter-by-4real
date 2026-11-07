# File Explorer panel
from tkinter import ttk

from rounded_panel import RoundedPanel

# this panel's own settings
TITLE = "File Explorer"
HEADER_COLOR = "#E88E1F"
TITLE_COLOR = "#2B2B2B"
BODY_COLOR = "#DFD6BB"
TEXT_COLOR = "#2B2B2B"
SELECT_COLOR = "#C9BE9C"
FONT = ("Helvetica", 8, "bold")


class FileExplorerPanel(RoundedPanel):
    def __init__(self, parent):
        super().__init__(parent, TITLE, HEADER_COLOR, title_color=TITLE_COLOR,
                         icon="📁", plus_button=True)

        style = ttk.Style()
        style.configure("Explorer.Treeview", background=BODY_COLOR,
                        fieldbackground=BODY_COLOR, foreground=TEXT_COLOR,
                        borderwidth=0, rowheight=20, font=FONT)
        style.map("Explorer.Treeview", background=[("selected", SELECT_COLOR)],
                  foreground=[("selected", TEXT_COLOR)])
        style.layout("Explorer.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        self.tree = ttk.Treeview(self.body, style="Explorer.Treeview", show="tree",
                                 selectmode="browse")
        self.tree.pack(fill="both", expand=True)

        
