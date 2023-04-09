from utils import center_window
from database.sqlite_handler import get_session
from tkinter import messagebox
from custom.custom_table import CustomTable
from config import logger
from database.models import Base
from custom.custom_widgets import TimestampEntry, KeyValueCombobox
from custom.custom_variables import DateTimeVar
import tkinter as tk
import tkinter.ttk as ttk
from abc import ABC, abstractmethod

class CustomTopLevel(tk.Toplevel, ABC):
    """ A custom toplevel window. 
    
        Features:
        
            - Autofocus on creation
            - Configurable top and footer buttons
            - Destoy on escape key
            - Body frame to add additional widgets
    """

    def __init__(
        self, 
        parent: tk.Toplevel | tk.Tk,
        title: str = "Tk",
        resizable: bool = False,
        top_buttons_config: dict = None,
        footer_buttons_config: dict = None,
    ):
        """ 
            Args:
                parent: The parent window
                title: The title of the window
                resizable: If the window is resizable
                top_buttons_config: A dictionary with the button's label as key, and the command (callable) as value
                fotter_buttons_config: A dictionary with the button's label as key, and the command (callable) as value
        """

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
    
    def __init__(self, parent, padding=5, *args, **kwargs ) -> None:
        super().__init__(parent, padding=padding, *args, **kwargs)

        self._input_variables = {}
        self._input_widgets = {}
        self._input_rows = 0

    def set_values(self, values: dict[str: str|int|float] = None) -> None:
        """ Set the values of the input widgets using a dictionary."""
        for key, value in values.items():
            if key in self._input_variables.keys():
                self._input_variables[key].set(value)
            else:
                messagebox.showerror("Error", f'Key {key} not found in the input variables.')
                self.parent.focus()
                self.destroy()

    def get_input_widgets(self) -> list[dict[str: tk.Widget]]:
        """
            Get the input widgets. 
            Returns a list of dictionaries with the key and the widget.
        """
        return [{key: self._input_widgets[key] for key in self._input_widgets.keys()}]

    def set_binding(self, key: str, bindings: dict) -> None:
        """Set bindings to the input widget.
            :key: The key of the input.
            :bindings: A dictionary with the bindings. {'event': function}
        """
        for event, func in bindings.items():
            self._input_widgets[key].bind(event, func)
       
    def _set_widget(self, key: str, widget: tk.Widget, variable: tk.StringVar) -> None:
        """Set the widget and the variable to the input widgets and variables dictionaries."""
        
        widget.grid(column=1, row=self._get_inputs_qty(), sticky="w")
        self._input_widgets[key] = widget
        self._input_variables[key] = variable
        
    
    def _get_inputs_qty(self) -> int:
        """ Get the amount of inputs."""
        return len(self._input_variables)


    def _set_label(self, text: str) -> None:
        """ 
            Create a ttk.Label 
            
            :param text: The text of the label.
        """
        ttk.Label(self, text=text).grid(column=0, row=self._get_inputs_qty(), padx=5, pady=3, sticky="w")

    def get_values(self) -> list[dict[str: str|int|float|bool]]:
        """ 
            Get a dictionary with the values of the input widgets.
            
            For each key in the input widgets dictionary it will return the value of the `variable` associated with the widget.
                In case the widget is a `KeyValueCombobox` it will return the value of the widget itself,
                because it is not a simple string but a dictionary.
        """
        
        values = {}
        for key in self._input_variables.keys():
            value = None
            if isinstance(self._input_widgets[key], KeyValueCombobox):
                value = self._input_widgets[key].get()
            else:
                value = self._input_variables[key].get()
            values[key] = value
        return values

    def _validate_state(self, state: str):
        assert state in {
            'normal',
            'readonly',
        }, "The state must be one of ['normal', 'readonly']"


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
        self._validate_state(state=state)
        self._set_label(text=text or key.replace("_", ' ').title())
        variable = tk.StringVar()
        widget = ttk.Entry(self, textvariable=variable, width=width, state=state)
        self._set_widget(key=key, widget=widget, variable=variable)


    def add_input_combobox(
        self,
        key: str,
        func_get_values: callable,
        text: str = None,
        width: int = 100,
        enable_empty_option: bool = False,
        state="readonly"
    ) -> None:
        """
            Add a combobox input to the view.
            args:
                key: The key of the input.
                func_get_values: A function to get the values of the combobox. 
                    It must return a dictionary where the key is the `id` in the database.
                text: The text to display.
                width: The width of the input.
                enable_empty_option: If True it will add the option {None: '<Empty>'} at the begining.
                state: One of ['normal', 'readonly'].
        """

        self._validate_state(state=state)
        self._set_label(text=text or key.replace("_", ' ').title())
        variable = tk.StringVar()
        widget = KeyValueCombobox(
            self,
            func_get_values=func_get_values,
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
        default_now: bool = False,
        state: str = "normal"
    ) -> None:
        """ 
            Add a datetime input to the view.
            
            args:
                key: The key of the input.
                text: The text to display.
                width: The width of the input.
                format: The format of the datetime. Used to validate and extract the data as `str`.
                default_now: If True it will set the default value to the current datetime.
                state: One of ['normal', 'readonly'].
        """
        
        self._validate_state(state=state)
        self._set_label(text=text or key.replace("_", ' ').title())
        variable = DateTimeVar(format=format)
        widget = TimestampEntry(
            parent=self,
            format=format,
            default_now=default_now,
            textvariable=variable,
            width=width
        )
        self._set_widget(key=key, widget=widget, variable=variable)


class TemplateNewEdit(CustomTopLevel, ABC):
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
            values = self.get_validated_values(input_values=self.input_frame.get_values())
            self.on_accept(values=values)
            self.parent.event_generate("<<EventUpdateTable>>")
            self.parent.focus()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.focus()
