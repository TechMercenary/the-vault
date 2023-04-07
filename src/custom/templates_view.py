from utils import center_window
from database.sqlite_handler import get_session
from tkinter import messagebox
from custom.custom_table import CustomTable
from config import logger
from database.models import Base
from custom.custom_widgets import TimestampEntry, KeyValueCombobox
from custom.custom_variables import PendulumVar
import tkinter as tk
import tkinter.ttk as ttk


class CustomTopLevel(tk.Toplevel):
    """A custom toplevel window."""

    def __init__(
        self, 
        parent: tk.Toplevel | tk.Tk,
        title: str = "Tk",
        resizable: bool = False,
        top_buttons_config: dict = None,
        footer_buttons_config: dict = None,
    ):

        super().__init__(parent)
        # Tkinter variables
        self.parent = parent
        self.title(title)
        self.transient(parent)
        self.resizable(resizable, resizable)
        self.focus()

        # Custom variables
        self._top_buttons_config = top_buttons_config
        self._footer_buttons_config = footer_buttons_config

        self._set_contents()
        self.bind('<Escape>', self.destroy)

    def destroy(self, event=None):
        super().destroy()
        self.parent.focus()

    def _set_contents(self):
        ##### Frames
        self._root_frame = ttk.Frame(self)

        # Top buttons
        if self._top_buttons_config:
            self._set_row_buttons(row=0, buttons_config=self._top_buttons_config)

        # Body frame
        self.body_frame = ttk.Frame(self._root_frame)
        self.body_frame.grid(column=0, row=1)
        
        # Footer buttons
        if self._footer_buttons_config:
            self._set_row_buttons(row=2, buttons_config=self._footer_buttons_config)
        
        self._root_frame.grid(column=0, padx=3, pady=3, ipadx=3, ipady=3, row=0)

    def _set_row_buttons(self, row: int, buttons_config : dict):
        
        frame = ttk.Frame(self._root_frame)
        frame.grid(column=0, row=row, sticky="ew")
        frame.grid_anchor("center")
        
        for button_column, button_key in enumerate(buttons_config.keys()):
            ttk.Button(
                frame,
                text=button_key,
                command=buttons_config[button_key]
            ).grid(column=button_column, row=0, sticky="ew", padx=5, pady=5)


class TemplateListView(CustomTopLevel):
    """ A template for a list view. """
    
    __model__: Base = None
    __edit_view__: CustomTopLevel = None
    __new_view__: CustomTopLevel = None
    
    def __init__(
        self, parent: tk.Toplevel | tk.Tk, title: str):
        
        super().__init__(
            parent=parent,
            title=title,
            resizable=True,
            top_buttons_config={
                'Add': self.btn_add_command,
                'Edit': self.btn_edit_command,
                'Delete': self.btn_delete_command,
            },
            footer_buttons_config={
                'Close': self.destroy,
            },
        )
        
        self._set_table()

        center_window(window=self, context_window=self.parent)
        self.bind("<<EventUpdateTable>>", self.table.refresh)
        
        self.bind('<Delete>', self.btn_delete_command)
        self.bind('<F2>', self.btn_edit_command)
        self.bind('<Double-1>', self.btn_edit_command)
        self.bind('<Return>', self.btn_edit_command)

    def get_data(self):
        raise NotImplementedError

    def add_columns(self, table: CustomTable):
        raise NotImplementedError

    def btn_add_command(self, event=None):
        logger.debug('Add button clicked')
        self.__new_view__(self)

    def btn_edit_command(self, event=None):
        logger.debug('Edit button clicked')

        if selected_items:=self.table.get_items_data(selected_only=True):
            self.__edit_view__(self, selected_items[0]['id'])

    def btn_delete_command(self, event=None):
        logger.debug('Delete button clicked')
        
        if (selected_items:=self.table.get_items_data(selected_only=True)) \
            and messagebox.askyesno("Delete confirmation","Are you sure you want to delete the selected items?"):
            try:
                self._db_delete_item(ids=[item['id'] for item in selected_items])
            except Exception as e:
                messagebox.showerror("Error", str(e))
   
    def _db_delete_item(self, ids: list):
        with get_session() as session:
            session.query(self.__model__).filter(self.__model__.id.in_(ids)).delete(synchronize_session=False)
            session.commit()
        self.event_generate("<<EventUpdateTable>>")
   
    def _set_table(self):
        """Create the Table"""
        self.table = CustomTable(parent=self.body_frame, func_get_data=self.get_data)
        self.add_columns(table=self.table)
        self.table.refresh()
        self.table.grid(column=0, row=0, sticky="ew")


class FrameInput(ttk.Frame):
    
    def __init__(self, parent, padding=5, *args, **kwargs ) -> None:
        super().__init__(parent, padding=padding, *args, **kwargs)

        self._input_variables = {}
        self._input_widgets = {}
        self._input_rows = 0

    def set_values(self, values: dict[str: tk.StringVar| PendulumVar] = None) -> None:
        for key, value in values.items():
            if key in self._input_variables.keys():
                self._input_variables[key].set(value)
            else:
                messagebox.showerror("Error", f'Key {key} not found in the input variables.')
                self.parent.focus()
                self.destroy()

    def get_input_widgets(self) -> list[dict[str: tk.Widget]]:
        return [{key: self._input_widgets[key] for key in self._input_widgets.keys()}]

    def set_binding(self, key: str, bindings: dict) -> None:
        """Set bindings to the input widget.
            :param key: The key of the input.
            :param bindings: A dictionary with the bindings. {'event': function}
        """
        for event, func in bindings.items():
            self._input_widgets[key].bind(event, func)
       
    def _set_widget(self, key: str, widget: tk.Widget, variable: tk.StringVar) -> None:
        widget.grid(column=1, row=self._get_inputs_qty(), sticky="w")
        self._input_widgets[key] = widget
        self._input_variables[key] = variable
    
    def _get_inputs_qty(self) -> int:
        return len(self._input_variables)

    def _set_label(self, key: str, text: str = None) -> None:
        ttk.Label(self, text=text or key.replace("_",' ').title())\
            .grid(column=0, row=self._get_inputs_qty(), padx=5, pady=3, sticky="w")

    def get_values(self) -> list[dict[str: str|int|float|bool]]:
        return {key: self._input_variables[key].get() for key in self._input_variables.keys()}
        
    def add_input_entry(
        self,
        key: str,
        text: str = None,
        width: int = 100,
        state: str = "normal"
    ) -> None:
        """Add an entry input to the view.
            :param key: The key of the input.
            :param text: The text to display.
            :param width: The width of the input.
            :param state: One of ['normal', 'readonly'].
        """
        self._set_label(key, text)
        variable = tk.StringVar()
        widget = ttk.Entry(self, textvariable=variable, width=width, state=state)
        self._set_widget(key=key, widget=widget, variable=variable)


    def add_input_combobox(
        self,
        key: str,
        text: str = None,
        width: int = 100,
        values: dict = None,
        func_update: callable = None,
        enable_empty_option: bool = False,
        state="readonly"
    ) -> None:

        self._set_label(key, text)
        variable = tk.StringVar()
        widget = KeyValueCombobox(
            self,
            func_update=func_update,
            values=values,
            enable_empty_option=enable_empty_option,
            textvariable=variable,
            width=width,
            state=state
        )
        self._set_widget(key=key, widget=widget, variable=variable)

    def add_input_datetime(
        self,
        key: str,
        text: str = None,
        width: int = 100,
        format: str ="YYYY-MM-DD HH:mm:ss",
        default_now: bool = False
    ) -> None:
        self._set_label(key, text)
        variable = PendulumVar(format=format)
        widget = TimestampEntry(
            self,
            format=format,
            default_now=default_now,
            textvariable=variable,
            width=width
        )
        self._set_widget(key=key, widget=widget, variable=variable)


class TemplateNewEdit(CustomTopLevel):

    def __init__(self, parent: tk.Toplevel | tk.Tk, title: str):
        
        footer_buttons_config = {
            "Aceptar": self.btn_accept,
            "Cancelar": self.destroy,
        }
        
        super().__init__(
            parent,
            title=title,
            footer_buttons_config=footer_buttons_config
        )

        # input frame
        self.input_frame = FrameInput(self.body_frame, padding=10)
        self.set_inputs(input_frame=self.input_frame)
        self.input_frame.grid(column=0, row=0)

        center_window(window=self, context_window=self.parent)
        self.bind("<Return>", self.btn_accept)
    
    def set_inputs(self, input_frame: FrameInput):
        raise NotImplementedError
    
    def on_accept(self, values: list[dict]):
        raise NotImplementedError
    
    def get_validated_values(self, input_values: dict) -> dict:
        raise NotImplementedError
    
    def btn_accept(self, event=None):
        try:
            values = self.get_validated_values(input_values=self.input_frame.get_values())
            self.on_accept(values=values)
            self.parent.event_generate("<<EventUpdateTable>>")
            self.parent.focus()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.focus()


if __name__ == '__main__':
    from utils import toplevel_set_active
    
    root = tk.Tk()
    
    toplevel = CustomTopLevel(parent=root)
    
    frame = FrameInput(toplevel)
    frame.grid(column=0, row=0, sticky="news")
    frame.add_input_entry(key="code", width=10)
    frame.add_input_entry(key="description", width=30)
    
    toplevel_set_active(window=toplevel)
    center_window(window=root, context_window=None)
    center_window(window=toplevel, context_window=root)
    
    root.mainloop()

