# File Explorer panel. Edit only this file to change this panel.
import os
from tkinter import filedialog, ttk

from rounded_panel import RoundedPanel

# this panel's own settings
TITLE = "File Explorer"
HEADER_COLOR = "#E88E1F"
TITLE_COLOR = "#2B2B2B"
BODY_COLOR = "#DFD6BB"
TEXT_COLOR = "#2B2B2B"
SELECT_COLOR = "#C9BE9C"
FONT = ("Helvetica", 8, "bold")
FOLDER_ICON = "📁"
FILE_ICON = "📄"
SHOW_HIDDEN = False  # set True to also list files/folders starting with "."


class FileExplorerPanel(RoundedPanel):
    def __init__(self, parent):
        super().__init__(parent, TITLE, HEADER_COLOR, title_color=TITLE_COLOR,
                         icon=FOLDER_ICON, plus_button=True)

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

        self.root_dir = None     # currently opened directory
        self._paths = {}         # tree item id -> full path
        self._loaded = set()     # folder item ids whose contents are loaded

        # Plus button (drawn by RoundedPanel in the header): click + hover
        self.bind("<Button-1>", self._on_canvas_click, add="+")
        self.bind("<Motion>", self._on_canvas_motion, add="+")
        self.tree.bind("<<TreeviewOpen>>", self._on_folder_open)

    # plus button
    def _over_plus(self, event):
        bx, by = self.winfo_width() - 26, 4 + self.header_h / 2
        return abs(event.x - bx) <= 9 and abs(event.y - by) <= 9

    def _on_canvas_motion(self, event):
        self.configure(cursor="hand2" if self._over_plus(event) else "")

    def _on_canvas_click(self, event):
        if self._over_plus(event):
            self.choose_directory()

    # opening a directory
    def choose_directory(self):
        # Open the system file explorer and let the user pick a directory.
        path = filedialog.askdirectory(parent=self.winfo_toplevel(),
                                       title="Select a folder to open",
                                       mustexist=True)
        if path:  # empty string means the user cancelled
            self.open_directory(path)

    def open_directory(self, path):
        path = os.path.normpath(path)
        self.root_dir = path
        self._paths.clear()
        self._loaded.clear()
        self.tree.delete(*self.tree.get_children())

        name = os.path.basename(path) or path
        root = self.tree.insert("", "end", text=f"{FOLDER_ICON} {name}", open=True)
        self._paths[root] = path
        self._populate(root)

    def _populate(self, parent_iid):
        # Fill a folder node with its files and sub-folders (folders first).
        self.tree.delete(*self.tree.get_children(parent_iid))
        path = self._paths[parent_iid]
        try:
            entries = [e for e in os.scandir(path)
                       if SHOW_HIDDEN or not e.name.startswith(".")]
        except OSError:
            self.tree.insert(parent_iid, "end", text="(cannot open folder)")
            return
        entries.sort(key=lambda e: (not e.is_dir(), e.name.lower()))

        for entry in entries:
            if entry.is_dir():
                iid = self.tree.insert(parent_iid, "end",
                                       text=f"{FOLDER_ICON} {entry.name}")
                self._paths[iid] = entry.path
                self.tree.insert(iid, "end")  # dummy child so the arrow shows
            else:
                iid = self.tree.insert(parent_iid, "end",
                                       text=f"{FILE_ICON} {entry.name}")
                self._paths[iid] = entry.path
        self._loaded.add(parent_iid)

    def _on_folder_open(self, _event):
        iid = self.tree.focus()
        if iid in self._paths and iid not in self._loaded:
            self._populate(iid)

    # for later functionality
    def get_selected_path(self):
        # Full path of the selected file/folder, or None.
        sel = self.tree.selection()
        return self._paths.get(sel[0]) if sel else None