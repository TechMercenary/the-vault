from utils import center_window
from database.sqlite_handler import get_session
from tkinter import messagebox
from custom.custom_table import CustomTable
from config import logger
from database.models import Base
from custom.custom_widgets import PendulumEntry, KeyValueCombobox, DecimalEntry
from custom.custom_variables import PendulumVar, DecimalVar
import tkinter as tk
import tkinter.ttk as ttk
import pendulum
from decimal import Decimal
from abc import ABC, abstractmethod

class CustomTopLevel(tk.Toplevel, ABC):
    """ A custom toplevel window. 
    
        Use `self.body_frame` to add additional widgets.
    
        Features:
        
            - Autofocus on creation
            - Configurable top and footer buttons
            - Destoy on escape key
            - Body frame to add additional widgets

            Args:
                parent: The parent window
                title: The title of the window
                resizable: If the window is resizable
                top_buttons_config: A dictionary with the button's label as key, and the command (callable) as value
                fotter_buttons_config: A dictionary with the button's label as key, and the command (callable) as value
    """

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
        """ Destroy the window and focus on the parent. """
        super().destroy()
        self.parent.focus()

    def _set_contents(self):
        """ Set the top and footer buttons. """
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
        """ 
            Set the buttons in a row. 
            buttons_config: A dictionary with the button's label as key, and the command (function callable) as value
        """
        
        frame = ttk.Frame(self._root_frame)
        frame.grid(column=0, row=row, sticky="ew")
        frame.grid_anchor("center")

        # Create the buttons 
        for button_column, button_key in enumerate(buttons_config.keys()):
            ttk.Button(
                frame,
                text=button_key,
                command=buttons_config[button_key]
            ).grid(column=button_column, row=0, sticky="ew", padx=5, pady=5)


class TemplateListView(CustomTopLevel, ABC):
    """ A template for a list view. 
    
        Features:
            - Add, edit and delete buttons on the top
            - Close button on the footer
            - Auto center on creation
            - Auto refresh table's data on <<EventUpdateTable>> (on delete, on edit, on add)
            - Key bindings:
                - Delete: Delete the selected row
                - F2: Edit the selected row
                - Double click: Edit the selected row
                - Enter: Edit the selected row
            - Automatic item Add, item edit, and item delete bindings and view calls.
            - Configurations:
                - __model__: The database model
                - __edit_view__: The edit view
                - __new_view__: The new view
                - `get_data`: A function that returns the data to be displayed on the table
                - `add_columns`: A function that defines which columns are shown in the table
    """
    
    __model__: Base = None
    __edit_view__: CustomTopLevel = None
    __new_view__: CustomTopLevel = None
    
    def __init__(self, parent: tk.Toplevel | tk.Tk, title: str):
        
        super().__init__(
            parent=parent,
            title=title,
            resizable=True,
            top_buttons_config={
                'Add': self._on_add,
                'Edit': self._on_edit,
                'Delete': self._on_delete,
            },
            footer_buttons_config={
                'Close': self.destroy,
            },
        )
        
        self._set_table()

        center_window(window=self, context_window=self.parent)
        self.bind("<<EventUpdateTable>>", self.table.refresh)
        
        self.bind('<Delete>', self._on_delete)
        self.bind('<F2>', self._on_edit)
        self.bind('<Double-1>', self._on_edit)
        self.bind('<Return>', self._on_edit)

    @abstractmethod
    def get_data(self):
        """ 
            Get the data to be displayed on the table.
            It is used to configure the `func_get_data` parameter of the `CustomTable` class.
        """
        raise NotImplementedError

    @abstractmethod
    def add_columns(self, table: CustomTable):
        """
            Add the columns to the table. See `CustomTable.add_column` for more information.
        """
        raise NotImplementedError

    def _on_add(self, event=None):
        logger.debug('Add button clicked')
        self.__new_view__(self)

    def _on_edit(self, event=None):
        logger.debug('Edit button clicked')

        if selected_items:=self.table.get_items_data(selected_only=True):
            self.__edit_view__(self, selected_items[0]['id'])

    def _on_delete(self, event=None):
        logger.debug('Delete button clicked')
        
        if (selected_items:=self.table.get_items_data(selected_only=True)) \
            and messagebox.askyesno("Delete confirmation","Are you sure you want to delete the selected items?"):
            try:
                self._db_delete_item(ids=[item['id'] for item in selected_items])
            except Exception as e:
                messagebox.showerror("Error", str(e))
   
    def _db_delete_item(self, ids: list):
        """ Delete the items from the database using the `id` field"""
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
    """ A custom frame to easily create input forms."""
    
    def __init__(self, parent, padding=5, *args, **kwargs) -> None:
        super().__init__(parent, padding=padding, *args, **kwargs)

        self._input_variables = {}
        self._input_widgets = {}
        self._input_rows = 0

    def set_values(self, values: dict[str: str|int|Decimal] = None) -> None:
        """ Set the values of the input widgets using a dictionary."""

        if unset_keys := [key for key in values if key not in self._input_variables.keys()]:
            messagebox.showerror("Error", f"Keys [{', '.join(unset_keys)}] not found in the input variables.")
            self.parent.focus()
            self.destroy()
            return None

        for key, value in values.items():
            self._input_variables[key].set(value)


    def set_bind(self, key: str, event: str, func: callable) -> None:
        self._input_widgets[key].bind(event, func)

    def get_values(self) -> list[dict[str: str|int|float|bool]]:
        return {
            key: self._input_variables[key].get()
            for key in self._input_variables.keys()
        }


    def _add_input(self, key: str, widget: tk.Entry, text: str = None):
        ttk.Label(self, text=text or key.replace("_", ' ').title()) \
            .grid(column=0, row=len(self._input_variables), padx=5, pady=3, sticky="w")
        variable = tk.StringVar()
        widget.option_add('textvariable', variable)
        widget.grid(column=1, row=len(self._input_variables), sticky="w")
        self._input_widgets[key] = widget
        self._input_variables[key] = variable

    def add_input_decimal(self, key: str, text: str = None, width: int = None, state: str = None, format: str = None, value: Decimal|str = None) -> None:
        self._add_input(
            key=key,
            widget=DecimalEntry(self, width=width, state=state or "normal", format=format or '0.01', value=value),
            text=text,
        )

    def add_input_label(self, key: str, text: str = None, width: int = 100, value=None) -> None:
        self._add_input(
            key=key,
            widget=ttk.Label(self, width=width, value=value),
            text=text
        )
    
    def add_input_entry(self, key: str, text: str = None, width: int = 100, state: str = "normal", value=None) -> None:
        self._add_input(
            key=key,
            widget=ttk.Entry(self, width=width, state=state or "normal", value=value),
            text=text
        )

    def add_input_combobox(self, key: str, values: list|tuple, text: str = None, width: int = 100, state: str ="readonly") -> None:
        self._add_input(
            key=key,
            widget=ttk.Combobox(self, width=width, state=state, values=values),
            text=text
        )

    def add_input_pendulum(self, key: str, text: str = None, width: int = 20, format: str ="YYYY-MM-DD HH:mm:ss", value=None) -> None:
        self._add_input(
            key=key,
            widget=PendulumEntry(self, width=width, format=format, value=value),
            text=text
        )


class TemplateChange(CustomTopLevel, ABC):
    """
        Template for the new and edit windows.

        Needs to implement:
            - `set_inputs` to configure the inputs.
            - `on_accept` to configure the action when the user clicks on "Accept".
            - `get_validated_values` to validate the values of the inputs, it must return a dictionary with the values.
        
        features:
            - It has a body frame `input_frame` (an instance of FrameInput) to configure the inputs.
            - It has a footer with the buttons "Accept" and "Cancel".
            - Accept: It will call `get_validated_values`, and `on_accept` if the values are valid.
            - The "Accept" and "Cancel" button are already binded
            - The "Accept" button is binded to the <Return> key.
    """
    def __init__(self, parent: tk.Toplevel | tk.Tk, title: str) -> None:
        
        footer_buttons_config = {
            "Accept": self._on_accept_wrapper,
            "Cancel": self.destroy,
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
        self.bind("<Return>", self._on_accept_wrapper)
    
    @abstractmethod
    def set_inputs(self, input_frame: FrameInput) -> None:
        """
            Configure the inputs of the window. 
            See `FrameInput` for more information.
        """
        raise NotImplementedError
    
    @abstractmethod
    def on_accept(self, event=None, values: list[dict] = list) -> None:
        """
            This code will be executed when the user clicks on "Accept".
            The values are being passed from `get_validated_values`.
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_validated_values(self, input_values: dict) -> dict:
        """
            Validate the values of the inputs, it must return a dictionary with the values. 
            The values will be passed to `on_accept`.
        """
        raise NotImplementedError
    
    def _on_accept_wrapper(self, event=None) -> None:
        """
            Wrapper for the `on_accept` method.
            - It will call `get_validated_values`, and `on_accept` if the values are valid.
            - It will show an error message if the values are not valid.
            - It generates the event "<<EventUpdateTable>>" used by TemplateListView to update the table.
        """
        try:
            self.on_accept(values=self.get_validated_values(input_values=self.input_frame.get_values()))
            self.parent.event_generate("<<EventUpdateTable>>")
            self.parent.focus()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.focus()
