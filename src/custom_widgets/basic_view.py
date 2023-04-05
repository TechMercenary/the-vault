from functools import partial
from utils import center_window
from database.sqlite_handler import get_session
from database.models import Currency
from tkinter import messagebox
from sqlalchemy import func
from custom_widgets.table import CustomTable
from custom_widgets.toplevel import CustomTopLvel
from custom_widgets.key_value_combobox import KeyValueCombobox
from custom_widgets.timestamp_entry import TimestampEntry
import tkinter as tk
import tkinter.ttk as ttk
from config import logger


class BasicView(CustomTopLvel):
    def __init__(self, parent: tk.Toplevel | tk.Tk, title: str):
        super().__init__(parent, title=title)

        self._input_variables = {}
        self._input_widgets = {}
        self._input_rows = 0

        self.input_frame = ttk.Frame(self.main_frame, padding=10)
        self.input_frame.grid(column=0, row=0)

        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.grid(column=0, row=2, sticky="ew")
        self.buttons_frame.grid_anchor("center")

        self._add_buttons()
        self.bind("<Return>", self.btn_accept)

    def get_input(self, key: str) -> str:
        return self._input_variables[key].get()
    
    def set_input(self, key: str, value: str) -> None:
        self._input_variables[key].set(value)

    def get_input_widget(self, key: str) -> tk.Widget:
        return self._input_widgets[key]
    
    def set_bindings(self, key: str, bindings: dict) -> None:
        """Set bindings to the input widget.
            :param key: The key of the input.
            :param bindings: A dictionary with the bindings. {'event': function}
        """
        for event, func in bindings.items():
            self._input_widgets[key].bind(event, func)


    def center(self):
        center_window(window=self, context_window=self.parent)

    def _add_buttons(self) -> None:
        ttk.Button(self.buttons_frame, text='Aceptar', command=self.btn_accept).grid(column=0, row=2)
        ttk.Frame(self.buttons_frame, width=50).grid(column=1, row=2) # spacer
        ttk.Button(self.buttons_frame, text='Cancelar', command=self.destroy).grid(column=2, row=2)

    def btn_accept(self, event=None):
        raise NotImplementedError

    def add_input(
                self,
                key: str,
                widget_type: str,
                text: str = None,
                width: int = None,
                is_readonly: bool = False,
                cbox_values: dict = None,
                cbox_func_update: callable = None,
                cbox_enable_empty_option: bool = False,
                dt_format="YYYY-MM-DD HH:MM:SS",
                dt_default_now: bool = False
            ) -> None:
        """
            Add an input to the view.
                :param key: The key of the input.
                :param text: The text to display.
                :param widget_type: The type of input. ('entry', 'combobox', etc.)
        """
        
        text = text or key.replace("_",' ').title()
        self._input_variables[key] = tk.StringVar()

        ttk.Label(self.input_frame, text=text).grid(column=0, row=self._input_rows, padx=5, pady=3, sticky="w")
        if widget_type == "combobox":
            widget = KeyValueCombobox(
                self.input_frame,
                func_update=cbox_func_update,
                values=cbox_values,
                cbox_enable_empty_option=cbox_enable_empty_option,
                textvariable=self._input_variables[key],
                width=width
            )

        elif widget_type == "datetime":
            widget = TimestampEntry(self.input_frame, format=dt_format, default_now=dt_default_now, textvariable=self._input_variables[key], width=width)


        elif widget_type == "entry":
            widget = ttk.Entry(self.input_frame, textvariable=self._input_variables[key])
            
        widget.grid(column=1, row=self._input_rows, sticky="w")

        if width:
            widget.configure(width=width)

        widget.configure(state="readonly" if is_readonly else "normal")

        self._input_widgets[key] = widget
        self._input_rows += 1



if __name__ == '__main__':

    from utils import toplevel_set_active

    root = tk.Tk()
    center_window(window=root, context_window=None)
    
    toplevel = BasicView(root, title='Test')
    toplevel_set_active(window=toplevel)
    
    ## Configure the toplevel
    toplevel.add_input(key='code', widget_type='entry', width=5)
    toplevel.add_input(key='description', widget_type='entry', width=20)
    toplevel.add_input(key='group', widget_type='combobox', width=20, cbox_values={'1': 'a', '2': 'b'}, cbox_enable_empty_option=True)
    toplevel.add_input(key='created_at', widget_type='datetime', width=20, dt_default_now=True) 

    
    ### center the toplevel
    toplevel.center()

    root.mainloop()