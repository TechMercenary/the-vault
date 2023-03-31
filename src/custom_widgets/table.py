from functools import partial
import tkinter as tk
import tkinter.ttk as ttk


class CustomTable(tk.Frame):
    """ A custom table widget.
        Usage:
        
        1. First, create an instance of the widget: 
        
            CustomTable(parent, selectmode="extended", data=data)
            
            - Only the `parent` argument is required.
            - The `selectmode` argument is optional. It can be "extended", "browse", or "none" . (See https://tcl.tk/man/tcl8.6/TkCmd/ttk_treeview.htm#M6)
            - The `data` argument is optional:
                - It is a list of dictionaries. 
                - Each dictionary represents a row. 
                - The keys of the dictionary are the column names
                
        2. Then, add the columns (and their configurations) that will be shown in the table.
            This is done by calling the `add_column` method for each column. (See more in the docstring of the method).
            
        3. Finally, call the `update` method to show/update the table with the data. (See more in the docstring of the method).
    
    """
    
    def __init__(self, parent, selectmode="extended", data=None) -> None:
        super().__init__(parent)

        self._data = data
    
        # Create the table
        self._table = ttk.Treeview(self, selectmode=selectmode)
        self._table.grid(column=0, row=0)
        
        # Create the scrollbar
        self._scrollbar = ttk.Scrollbar(self, orient="vertical", command=self._table.yview)
        self._table.configure(yscrollcommand=self._scrollbar.set)
        self._scrollbar.grid(column=1, row=0, sticky="ns")
        
        # Attribute for the columns configurations
        self._col_config = {}
        
        # Workaround. See `self._configure_columns`
        self.first_update = True


    def bind(self, *args):
        """Bind an event to the table."""
        self._table.bind(*args)


    def get_columns(self) -> list:
        """Return the column names."""

        return list(self._col_config.keys())

        
    def add_column(self,
                   column: str,
                   text: str = None,
                   dtype: int|str|float = str,
                   anchor: str = tk.CENTER,
                   minwidth: int = 20,
                   width: int = 200,
                   stretch: bool = True,
                   is_sorted_asc: bool|None = None
               ) -> None:
        """Add a column and configuration to the table.
        
        Args:
            column (str): The internal name of the column. This is the key of the dictionary in the `data` argument.
            text (str, optional): The display text to be shown in the heading. Defaults to the "Title Case" of the `column` parameter.
            dtype (int|str|float, optional): The data type of the column. Defaults to str. It is used to sort the column.
            anchor (str, optional): The aligment of the values in the column. Defaults to tk.CENTER.
                - tk.W: Left
                - tk.CENTER: Center
                - tk.E: Right
            minwidth (int, optional): The minimum width of the column. Defaults to 20.
            width (int, optional): The width of the column. Defaults to 200.
            stretch (bool, optional): Whether the column should stretch to fill the available space. Defaults to True.
            is_sorted_asc (bool|None, optional): Whether the column's data is sorted in:
                - ascending order (True),
                - descending order (False),
                - or neither (None)
        """
        
        # Add the column to the table
        
        self._col_config[column] = {
            'dtype': dtype,
            'is_sorted_asc': is_sorted_asc,
            'column_config': {
                'anchor': anchor,
                'minwidth': minwidth,
                'width': width,
                'stretch': stretch,
            },
            'heading_config': {
                'text': text or column.title(),
                'command': lambda: self._sort_table(column=column),
            }
        }
        

    def _sort_table(self, column):
        """Sort the table by the given column."""
        
        # Get all tuples of values and ids
        items = []
        for index in self._table.get_children(''):
            value = self._table.set(index, column)
            items.append((value, index))

        # Determine if the sort is reversed
        sort_descending = bool(self._col_config[column]['is_sorted_asc'])

        # Reset sort for all columns except the current one
        for col in self._col_config.keys():
            if col != column:
                self._col_config[col]['is_sorted_asc'] = None
            else:
                self._col_config[column]['is_sorted_asc'] = not sort_descending

        # Sort the data
        def get_sort_key(item, dtype: str | int | float) -> str | int | float:
            value, _ = item
            return dtype(value).lower() if isinstance(dtype, str) else dtype(value)

        dtype = self._col_config[column]['dtype']
        items.sort(reverse=sort_descending, key=partial(get_sort_key, dtype=dtype))

        # Reassign the values to the table
        for index, (val, k) in enumerate(items):
            self._table.move(k, '', index)
        
    def delete_all(self):
        """Delete all items in the table."""
        
        for item in self._table.get_children():
            self._table.delete(item)

    def _configure_columns(self):
        """ Configure the columns only for the first update.
            It seems there's a bug in Tkinter where new columns are not being 
            configured properly. This is a workaround.
        """
        if self.first_update:
            
            # Assing columns and hide the first column
            self._table["columns"] = tuple(self._col_config.keys())
            self._table.column("#0", width=0, stretch=tk.NO)

            # Assign headings and column attributes
            for column in self._col_config.keys():
                self._table.column(column, **self._col_config[column]['column_config'])
                self._table.heading(column, **self._col_config[column]['heading_config'])
            self.first_update = False


    def update_table(self, data: list = None):
        """Update the table data."""

        # Update the data
        self._data = data or self._data

        self._configure_columns()

        self.delete_all()

        # Insert data based on the column configuration
        for item in self._data:
            values = tuple(item[column] for column in self.get_columns())
            self._table.insert('', 'end', values=values)

    def get_items_data(self, selected_only: bool = False):
        """Return the selected items."""
        
        columns = self.get_columns()
        data = []
        for item_id in self._table.selection() if selected_only else self._table.get_children():
            # get the item's data as a tuple
            item_values = self._table.item(item_id)['values']

            # Map tuple's values with the column names
            item_data = {
                columns[index]: item_values[index] for index in range(len(columns))
            }
            
            # Add the items's data to the list
            data.append(item_data)

        return data


if __name__ == '__main__':
    # Example of use
    
    root = tk.Tk()
    root.title("Test Table")

    data = [
        {'id': 1, 'name': 'John', 'age': 30},
        {'id': 2, 'name': 'Jane', 'age': 25},
        {'id': 3, 'name': 'Bob', 'age': 40},
        {'id': 4, 'name': 'Alice', 'age': 28},
        {'id': 5, 'name': 'David', 'age': 33},
        {'id': 6, 'name': 'Emma', 'age': 22},
        {'id': 7, 'name': 'Frank', 'age': 45},
        {'id': 8, 'name': 'Grace', 'age': 27},
        {'id': 9, 'name': 'Henry', 'age': 32},
        {'id': 10, 'name': 'Isabella', 'age': 29},
        {'id': 11, 'name': 'Jack', 'age': 38},
        {'id': 12, 'name': 'Karen', 'age': 24},
        {'id': 13, 'name': 'Leo', 'age': 31},
        {'id': 14, 'name': 'Megan', 'age': 26},
        {'id': 15, 'name': 'Nathan', 'age': 36}
    ]

    table = CustomTable(root, selectmode="extended", data=data)
    table.add_column(column='id', dtype=int, anchor=tk.E, minwidth=20, width=50)
    table.add_column(column='name', anchor=tk.W, width=100)
    table.add_column(column='age', anchor=tk.E, width=50)
    table.update_table()
    table.grid(column=0, row=0, columnspan=3, padx=10, pady=10)

    def print_selected():
        print(table.get_items_data(selected_only=True))

    def print_all():
        print(table.get_items_data())

    def update_data():
        new_data = [
            {'id': 100, 'name': 'AAA', 'age': 0},
            {'id': 101, 'name': 'BBB', 'age': 1},
            {'id': 102, 'name': 'CCC', 'age': 2},
        ]
        table.update_table(data=new_data)

    tk.Button(root, text="Print Selected", command=print_selected, padx=10, pady=10).grid(column=0, row=1)
    tk.Button(root, text="Print All Items", command=print_all, padx=10, pady=10).grid(column=1, row=1)
    tk.Button(root, text="Update data", command=update_data, padx=10, pady=10).grid(column=2, row=1)
    
    root.update_idletasks()
    root.geometry(f"+{root.winfo_screenwidth()//2-root.winfo_width()//2}+{root.winfo_screenheight()//2-root.winfo_height()//2}")

    root.mainloop()
    
