# File Explorer panel. Edit only this file to change this panel.
import os
import tkinter as tk
from tkinter import PhotoImage, messagebox, simpledialog, ttk

from rounded_panel import RoundedPanel

# this panel's own settings
TITLE = "File Explorer"
HEADER_COLOR = "#E88E1F"
TITLE_COLOR = "#2B2B2B"
BODY_COLOR = "#DFD6BB"
TEXT_COLOR = "#2B2B2B"
SELECT_COLOR = "#C9BE9C"
FONT = ("Helvetica", 8, "bold")
MENU_FONT = ("Helvetica", 12, "bold")
SHOW_HIDDEN = False  # set True to also list files/folders starting with "."
DEFAULT_NEW_NAME = "untitled.lol"
DEFAULT_EXTENSION = ".lol"
FALLBACK_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _list_folder(path):
    # Sub-folders first, then files (hidden ones skipped unless SHOW_HIDDEN). Raises OSError.
    entries = [e for e in os.scandir(path)
               if SHOW_HIDDEN or not e.name.startswith(".")]
    entries.sort(key=lambda e: (not e.is_dir(), e.name.lower()))
    return entries


class _OpenDialog(tk.Toplevel):
    # Small "Open" window: click a file OR a folder, then press Open.
    # A folder never has to be entered just to pick it; double-click a folder to look inside it.
    def __init__(self, parent, start_dir, folder_icon, file_icon):
        super().__init__(parent)
        self.title("Open a file or folder")
        self.transient(parent)
        self.minsize(320, 240)
        self.geometry(f"420x380+{parent.winfo_rootx() + 60}+{parent.winfo_rooty() + 60}")

        self.result = None        # (full path, is_folder) once the user presses Open
        self._folder_icon = folder_icon
        self._file_icon = file_icon
        self._items = {}          # tree item id -> (full path, is_folder)
        self._current = None      # folder currently listed

        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=(8, 4))
        ttk.Button(top, text="Up", width=4, command=self._go_up).pack(side="left")
        self._path_var = tk.StringVar()
        ttk.Entry(top, textvariable=self._path_var, state="readonly").pack(
            side="left", fill="x", expand=True, padx=(6, 0))

        middle = ttk.Frame(self)
        middle.pack(fill="both", expand=True, padx=8, pady=4)
        scroll = ttk.Scrollbar(middle, orient="vertical")
        self.tree = ttk.Treeview(middle, style="Explorer.Treeview", show="tree",
                                 selectmode="browse", yscrollcommand=scroll.set)
        scroll.config(command=self.tree.yview)
        scroll.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        bottom = ttk.Frame(self)
        bottom.pack(fill="x", padx=8, pady=(4, 8))
        ttk.Button(bottom, text="Cancel", command=self._cancel).pack(side="right")
        ttk.Button(bottom, text="Open", command=self._open_selected).pack(side="right", padx=(0, 6))
        ttk.Label(bottom, text="Select a file or folder, then press Open").pack(side="left")

        self.tree.bind("<Double-1>", self._on_double_click)
        self.bind("<Return>", lambda _e: self._open_selected())
        self.bind("<Escape>", lambda _e: self._cancel())
        self.protocol("WM_DELETE_WINDOW", self._cancel)

        self._show_folder(start_dir)

    def show(self):
        # Run the window until it is closed. Returns (path, is_folder), or None if cancelled.
        self.wait_visibility()
        self.grab_set()
        self.tree.focus_set()
        self.wait_window(self)
        return self.result

    def _show_folder(self, path):
        path = os.path.abspath(path)
        try:
            entries = _list_folder(path)
        except OSError as err:
            messagebox.showerror("Cannot open folder", str(err), parent=self)
            return
        self._current = path
        self._path_var.set(path)
        self.tree.delete(*self.tree.get_children())
        self._items.clear()
        for entry in entries:
            is_folder = entry.is_dir()
            iid = self.tree.insert("", "end", text=f" {entry.name}",
                                   image=self._folder_icon if is_folder else self._file_icon)
            self._items[iid] = (entry.path, is_folder)

    def _go_up(self):
        parent = os.path.dirname(self._current)
        if parent and parent != self._current:
            self._show_folder(parent)

    def _selected(self):
        sel = self.tree.selection()
        return self._items.get(sel[0]) if sel else None

    def _open_selected(self):
        # Whatever is selected is opened as it is; with nothing selected, the folder being listed.
        self._finish(self._selected() or (self._current, True))

    def _on_double_click(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        path, is_folder = self._items[iid]
        if is_folder:
            self._show_folder(path)      # look inside the folder
        else:
            self._finish((path, False))  # double-clicking a file opens it
        return "break"

    def _cancel(self):
        self._finish(None)

    def _finish(self, result):
        self.result = result
        self.grab_release()
        self.destroy()


class FileExplorerPanel(RoundedPanel):
    def __init__(self, parent):
        folder_icon = PhotoImage(master=parent, width=18, height=16)
        folder_icon.put("#E4C516", to=(1, 5, 17, 15))
        folder_icon.put("#E4C516", to=(2, 2, 9, 7))
        file_icon = PhotoImage(master=parent, width=16, height=16)
        file_icon.put("#D5E8E5", to=(3, 1, 13, 15))
        super().__init__(parent, TITLE, HEADER_COLOR, title_color=TITLE_COLOR,
                        plus_button=True)
        self.folder_icon = folder_icon
        self.file_icon = file_icon

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
        self.on_file_chosen = None  # set by the main window: called with a picked file's path,
                                    # returns True if the file was opened in the editor

        # Dropdown shown when the plus button is clicked: Open / New
        self.plus_menu = tk.Menu(self, tearoff=0, bg=BODY_COLOR, fg=TEXT_COLOR,
                                 activebackground=SELECT_COLOR, activeforeground=TEXT_COLOR,
                                 font=MENU_FONT, bd=0, relief="flat")
        self.plus_menu.add_command(label="Open", command=self.choose_path)
        self.plus_menu.add_command(label="New", command=self._on_new)

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
            self._show_plus_menu()

    def _show_plus_menu(self):
        # Drop the menu down just below the plus button.
        x = self.winfo_rootx() + self.winfo_width() - 26 - 9
        y = self.winfo_rooty() + 4 + int(self.header_h / 2) + 9
        try:
            self.plus_menu.tk_popup(x, y)
        finally:
            self.plus_menu.grab_release()

    def _on_new(self):
        # Create an empty file in the opened folder (or the project folder if none is open),
        # load it into the editor, and show it in the tree.
        parent = self.winfo_toplevel()
        folder = self.root_dir if self.root_dir and os.path.isdir(self.root_dir) else FALLBACK_DIR

        name = DEFAULT_NEW_NAME
        while True:
            name = simpledialog.askstring("New file", f"File name (created in {folder}):",
                                          initialvalue=name, parent=parent)
            if name is None:  # cancelled
                return
            name = name.strip()
            if not name or name in (".", "..") or any(c in name for c in ("/", "\\")):
                messagebox.showerror("Invalid name",
                                     "Enter a file name only (no slashes).", parent=parent)
                name = DEFAULT_NEW_NAME
                continue
            if not os.path.splitext(name)[1]:
                name += DEFAULT_EXTENSION
            path = os.path.join(folder, name)
            if os.path.exists(path):
                messagebox.showerror("File exists",
                                     f"'{name}' already exists in this folder.", parent=parent)
                continue
            break

        try:
            open(path, "x", encoding="utf-8").close()  # "x" never overwrites an existing file
        except OSError as err:
            messagebox.showerror("Cannot create file", str(err), parent=parent)
            return

        if self.on_file_chosen is not None and not self.on_file_chosen(path):
            try:
                os.remove(path)  # editor did not open it (e.g. unsaved-changes prompt cancelled)
            except OSError:
                pass
            return

        self.open_directory(folder)
        self._select_path(path)

    # opening a file or a directory
    def choose_path(self):
        # Let the user pick a file or a folder: select it, then press Open.
        start = self.root_dir if self.root_dir and os.path.isdir(self.root_dir) \
            else os.path.expanduser("~")
        picked = _OpenDialog(self.winfo_toplevel(), start,
                             self.folder_icon, self.file_icon).show()
        if not picked:  # cancelled
            return
        path, is_folder = picked
        if is_folder:
            self.open_directory(path)
            return
        if self.on_file_chosen is not None and not self.on_file_chosen(path):
            return  # the editor did not open it (cancelled or error): leave the tree alone
        self.open_directory(os.path.dirname(path))  # show the picked file's folder
        self._select_path(path)

    def _select_path(self, path):
        # Highlight the tree item for this file, if it is listed.
        target = os.path.normcase(os.path.normpath(path))
        for iid, item_path in self._paths.items():
            if os.path.normcase(os.path.normpath(item_path)) == target:
                self.tree.selection_set(iid)
                self.tree.see(iid)
                return

    def open_directory(self, path):
        path = os.path.normpath(path)
        self.root_dir = path
        self._paths.clear()
        self._loaded.clear()
        self.tree.delete(*self.tree.get_children())

        name = os.path.basename(path) or path
        root = self.tree.insert("", "end", text=f" {name}", image=self.folder_icon, open=True)
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
                                       text=f" {entry.name}", image=self.folder_icon)
                self._paths[iid] = entry.path
                self.tree.insert(iid, "end")  # dummy child so the arrow shows
            else:
                iid = self.tree.insert(parent_iid, "end",
                                       text=f" {entry.name}", image=self.file_icon)
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