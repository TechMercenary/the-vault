from tkinter import ttk
from functools import partial
import contextlib
import tkinter as tk
import pendulum


class TimestampEntry(ttk.Entry):
    def __init__(
            self,
            parent,
            format: str ='YYYY-MM-DD HH:mm:ss',
            value: str = None,
            default_now: bool = False,
            **kwargs
        ):
        
        super().__init__(master=parent, **kwargs)
            
        self._format = format
        
        if value:=value or (pendulum.now().format(format) if default_now else None):
            self.insert(tk.END, value)

        self.bind('<FocusOut>', self._parse_input)
   
    def _parse_input(self, event=None):
        input_str = self.get().strip()
        with contextlib.suppress(ValueError):
            new_value = pendulum.parser.parse(input_str).format(self._format)
            self.delete(0, tk.END)
            self.insert(0, new_value)


class KeyValueCombobox(ttk.Combobox):
    """ A combobox that stores the values in a dictionary.
        The values are displayed in the combobox and the keys are stored.
        :param func_get_values: A function that returns a dictionary with the values {'key': value}
            When it is set, the combobox will be updated when the dropdown is opened.
    """
    def __init__(self, parent, func_get_values: callable, enable_empty_option: bool = False, **kwargs):
        self._key_value_dict = {}
        self._enable_empty_option = enable_empty_option
        super().__init__(master=parent, **kwargs)
        
        self._func_get_values = func_get_values
        
        self.bind("<<ComboboxSelected>>", self._update)
            
        self._update()
        self.current(0)

    def _update(self, event=None):
        """Update the values of the combobox.
            The values are updated with the function passed to func_get_values.
        """
        old_key = self.current_key()
        old_value = self.current_value()
        key_values = self._func_get_values()
        self._key_value_dict = {None: '<Empty>', **key_values} if self._enable_empty_option else key_values
        self['values'] = list(self._key_value_dict.values())
        if old_key in self._key_value_dict:
            if old_value == self._key_value_dict[old_key]:
                self.current(self['values'].index(old_value))
            else:
                self.current(0)
        

    def current_key(self):
        for k in self._key_value_dict:
            if self._key_value_dict[k] == super().get():
                return k

    def current_value(self):
        return super().get()

    def get(self) -> str:
        return {'key': self.current_key(), 'value': self.current_value()}
        
