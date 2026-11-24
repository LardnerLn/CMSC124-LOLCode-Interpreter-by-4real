# Console panel 
import threading
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

        self._input_event = threading.Event()  # Wait signal for input
        self._input_value = "" # Stores entered text
        self._input_start_index = None # Input start index (name of the "input_start" mark while waiting)
        self._unlocked = False # True while clear() is running, so it may delete everything

        self._install_edit_guard()  # Keeps the user from editing console output while typing input

        self.text.bind("<Return>", self._on_enter)  # Bind Enter key
        self.text.bind("<KP_Enter>", self._on_enter)  # Numpad Enter behaves the same

    def write(self, message):
        self.text.configure(state="normal")
        self.text.insert("end", message)
        self.text.see("end")
        self.text.configure(state="disabled")

    def clear(self):
        self._unlocked = True  # Clearing is allowed even while an input prompt is open
        try:
            self.text.configure(state="normal")
            self.text.delete("1.0", "end")
            self.text.configure(state="disabled")
        finally:
            self._unlocked = False

    def prompt_inline_input(self, prompt_text):
        self.text.configure(state="normal")
        if prompt_text: # Only insert prompt text if non-empty
            self.text.insert("end", prompt_text)

        # Everything before this mark is read-only; the user can only edit what comes after it
        self.text.mark_set("input_start", "end-1c")
        self.text.mark_gravity("input_start", "left")  # Typed text stays to the right of the mark
        self.text.mark_set("insert", "end-1c")  # Caret starts inside the input area
        self.text.see("end")
        self.text.focus_set()

        self._input_start_index = "input_start" # Mark prompt end
        self._input_event.clear() # Reset wait signal
        self._input_value = "" # Reset value

        self._input_event.wait() # Pause execution thread
        self.text.configure(state="disabled")
        return self._input_value

    def _on_enter(self, event):
        if self._input_start_index is not None:
            self._input_value = self.text.get(self._input_start_index, "end-1c")  # Read typed text
            self.text.mark_unset(self._input_start_index)
            self._input_start_index = None
            self.text.insert("end", "\n")
            self.text.see("end")
            self.text.configure(state="disabled")  # Lock the console again right away

            self._input_event.set()  # Resume execution thread
            return "break"           # Prevent extra newline
        return "break"

    # ---------------------------------------------------------------
    # Edit guard: while an input prompt is open, only the text after the
    # "input_start" mark may be changed. Every edit of the Text widget
    # (typing, Backspace, Delete, cut, paste, middle-click paste) goes
    # through here, so no single key or mouse binding can be missed.
    def _install_edit_guard(self):
        w = self.text
        self._orig_cmd = w._w + "_orig"
        w.tk.call("rename", w._w, self._orig_cmd)         # Move the real widget command aside
        w.tk.createcommand(w._w, self._guarded_command)   # Our function now answers to the widget's name

    def _guarded_command(self, operation, *args):
        redirected = False
        if operation in ("insert", "delete", "replace") and self._input_start_index is not None and not self._unlocked:
            try:
                new_args = self._guard_edit(operation, args)
            except tk.TclError:
                new_args = args 
            if new_args is None:
                return ""  # Edit touches read-only output: ignore it
            redirected = operation == "insert" and new_args[0] != args[0]
            args = new_args

        result = self.text.tk.call((self._orig_cmd, operation) + tuple(args))

        if redirected:  # Typed text was sent to the input area, so move the caret there too
            self.text.mark_set("insert", "end-1c")
            self.text.see("end")
        return result

    def _guard_edit(self, operation, args):
        # Returns the (possibly changed) arguments, or None to block the edit
        if not args:
            return args
        before_input = self.text.compare(args[0], "<", self._input_start_index)
        if not before_input:
            return args
        if operation == "insert":
            return ("end-1c",) + tuple(args[1:])  # Typed or pasted into old output: append to the input instead
        return None  # Deleting or replacing old output is never allowed