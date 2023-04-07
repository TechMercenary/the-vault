import tkinter as tk
import tkinter.ttk as ttk

# TODO: Deprecare this class and use the one from templates_view.py
class CustomTopLvel(tk.Toplevel):
    """A custom toplevel window."""

    def __init__(
        self, 
        parent: tk.Toplevel | tk.Tk,
        title: str,
        resizable: bool = False,
    ):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        self.transient(parent)
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(column=0, padx=3, pady=3, ipadx=3, ipady=3, row=0)
        self.resizable(resizable, resizable)
        self.focus()

        self.bind('<Escape>', self.destroy)


    def destroy(self, event=None):
        super().destroy()
        self.parent.focus()


