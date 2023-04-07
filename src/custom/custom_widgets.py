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
        
        if value:=value or (pendulum.now() if default_now else None):
            self.insert(tk.END, value)

        self.bind('<FocusOut>', self._parse_input)
        self._parse_input()
    
    def _parse_input(self, event=None):
        input_str = self.get().strip()

        with contextlib.suppress(ValueError):
            new_value = pendulum.parse(input_str).format(self._format)
            self.delete(0, tk.END)
            self.insert(new_value)


class KeyValueCombobox(ttk.Combobox):
    """ A combobox that stores the values in a dictionary.
        The values are displayed in the combobox and the keys are stored.
        :param func_update: A function that returns a dictionary with the values {'key': value}
            When it is set, the combobox will be updated when the dropdown is opened.
    """
    def __init__(self, parent, func_update: callable = None, values: dict | list = None, enable_empty_option: bool = False, **kwargs):
        self._key_value_dict = {}
        self._enable_empty_option = enable_empty_option
        super().__init__(master=parent, **kwargs)
        
        self._func_update = func_update
        self._values = values
        
        if func_update:
            self.bind("<<ComboboxSelected>>", partial(self.update, func_update=func_update))
            
        self.update(func_update=func_update, values=values)

    def update(self, event=None, values: dict | list | None = None, func_update: callable = None):
        """Update the values of the combobox.
            The values are updated with the function passed to func_update.
        """
        values_dict = None
        if func_update:=func_update or self._func_update:
            values_dict = func_update()
        elif (values:=values or self._values):
            if isinstance(values, list):
                values_dict = { str(index): values[index] for index in range(len(values))}
            elif isinstance(values, dict):
                values_dict = values

        if values_dict:
            self._set_values(values_dict)


    def _set_values(self, key_values: dict):
        """Set the values of the combobox.
            :param key_values: A dictionary with the values {'key': value}
        """
        self._key_value_dict = {'': '<Empty>', **key_values} if self._enable_empty_option else key_values
        self['values'] = list(self._key_value_dict.values())

    def current_key(self):
        current_value = self.get()
        return self._key_value_dict.get(current_value)

    def current_value(self):
        return self.get()

