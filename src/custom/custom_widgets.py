from abc import abstractmethod
from tkinter import ttk
import tkinter as tk
import pendulum
from decimal import Decimal


class TemplateCustomEntry(ttk.Entry):
    """
    features:
        - When the entry is being edited, the input is parsed and the value is displayed in red if it is invalid.
        - When the entry loses focus, the input is parsed and the value is updated to the format specified.
    """
    def __init__(self, parent, format: str = None, **kwargs):
        super().__init__(master=parent, **kwargs)
        self._format = format
        self._parsed_value = None

        self.bind('<KeyRelease>', self._parse_input)
        self.bind('<FocusOut>', lambda event: self._update_widget())
    
    @abstractmethod
    def get_parsed_value(self, get_value: any) -> any:
        raise NotImplementedError
    
    def _parse_input(self, event=None) -> None:
        """ Try to parse the input and set it red if it is invalid. """
        try:
            self._parsed_value = self.get_parsed_value(get_value=self.get().strip(), format=self._format)
            self.config(foreground='black')
        except ValueError:
            self._parsed_value = None
            self.config(foreground='red')

    def _update_widget(self) -> None:
        """ If the input is valid, update the widget with the parsed value."""
        if self._parsed_value is not None:
            self.delete(0, tk.END)
            self.insert(0, self._parsed_value)

    def get(self) -> str:
        """ Return the parsed value. """
        return self._parsed_value


class PendulumEntry(TemplateCustomEntry):
    def __init__(self, parent, format: str ='YYYY-MM-DD HH:mm:ss', **kwargs):
        super().__init__(master=parent, format=format, **kwargs)

    def get_parsed_value(self, widget_value: str, format: str) -> str:
        return pendulum.parse(widget_value).format(format)


class DecimalEntry(TemplateCustomEntry):
    def __init__(self, parent, format: str = '0.00', **kwargs):
        super().__init__(master=parent, format=format, justify="right", **kwargs)

    def get_parsed_value(self, widget_value: str, format: str) -> str:
        return Decimal(widget_value).quantize(Decimal(format))

# TODO: Deprecar
class KeyValueCombobox(ttk.Combobox):
    """ A combobox that stores the values in a dictionary.
        The values are displayed in the combobox and the keys are stored.
    """
    def __init__(self, parent, func_get_values: callable, state="readonly", enable_empty_option: bool = False, **kwargs):
        """
            :func_get_values: 
                A function that returns a dictionary with the values {'key': value}, 
                the combobox will use it to update its values when the dropdown is opened.
            :enable_empty_option:
                If True, an empty option `<Empty>` will be added at the begining of the combobox.
        """
        
        self._key_value_dict = {}
        self._enable_empty_option = enable_empty_option
        super().__init__(master=parent, state=state, **kwargs)
        
        self._func_get_values = func_get_values
        
        self.bind("<<ComboboxSelected>>", self._update)
            
        self._update()
        self.current(0)

    def _update(self, event=None) -> None:
        """
            Use the function `func_get_values` to update the values of the combobox.
        """

        old_key = self.current_key()
        old_value = super().get()

        # Get the new values and update the combobox.
        key_values = self._func_get_values()
        self._key_value_dict = {None: '<Empty>', **key_values} if self._enable_empty_option else key_values
        self['values'] = list(self._key_value_dict.values())

        # If the old key is still in the new values, set the combobox to the old value.
        if old_key in self._key_value_dict:
            if old_value == self._key_value_dict[old_key]:
                self.current(self['values'].index(old_value))
            else:
                self.current(0)
        
    def current_key(self):
        """ Return the key of the current value. """
        
        for k in self._key_value_dict:
            if self._key_value_dict[k] == super().get():
                return k

    def get(self) -> dict[str: str]:
        """ Return the current key and value as dictionary. """
        return {'key': self.current_key(), 'value': super().get()}
        
