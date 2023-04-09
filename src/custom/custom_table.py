from functools import partial
import tkinter as tk
import tkinter.ttk as ttk


class CustomTable(tk.Frame):
    """ A custom table widget.
        Usage:
        
        1. Create an instance of the widget: 
        2. Set the columns that will be shown using the method `add_column`. (See more in the docstring of the method).
        3. Call the `refresh` method to load/update the data. (See more in the docstring of the method).
    """
    
    def __init__(self,
        parent: tk.Toplevel | tk.Tk,
        selectmode="extended",
        tree_root_col_width : int = 0,
        tree_expanded: bool = False,
        func_get_data: callable = lambda: [],
    ) -> None:
        """
            Args:
                selectmode: 
                    - "extended": Multiple items can be selected using the shift and control keys.
                    - "browse": Only one item can be selected at a time.
                    - "none": No items can be selected.
                tree_root_col_width: The width of the column #0 of the treeview. If 0, the column will not be shown.
                tree_expanded: If True, the treeview will be expanded by default.
                func_get_data: The function that will be called to get the data to be shown in the table. 
                    - It must return a list of dictionaries.
                    - The keys must be the same as the `column` parameter of the `add_column` method.
        """
        super().__init__(parent)

        self._tree_root_col_width = tree_root_col_width
        self._tree_expanded = tree_expanded
        self._func_get_data = func_get_data
        self._col_config = {}  # Stores the configuration of the columns
        self._first_update = True # Flag to determine if the table has been updated for the first time (workaround).
        
        # Create the table
        self._table = ttk.Treeview(self, selectmode=selectmode)
        self._table.grid(column=0, row=0, sticky="nsew")
        
        # Create the scrollbar
        self._scrollbar = ttk.Scrollbar(self, orient="vertical", command=self._table.yview)
        self._table.configure(yscrollcommand=self._scrollbar.set)
        self._scrollbar.grid(column=1, row=0, sticky="ns")
        
        # Make the treeview stretch to fill the window
        self.grid_columnconfigure(0, weight=1)
        
    def bind(self, *args) -> None:
        """Bind an event to the table."""
        self._table.bind(*args)


    def _expand_items(self) -> None:
        """Expand all items in the treeview."""
        
        def expand_treeview(item):
            # Expand the item to show its subitems
            self._table.item(item, open=True)
            
            # Recursively expand all subitems
            for child_item in self._table.get_children(item):
                expand_treeview(child_item)

        # Expand the entire TreeView
        for item in self._table.get_children():
            expand_treeview(item)
    

    def get_columns(self) -> list[str]:
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
        
        # Store the column configuration
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
                'text': text or column.replace('_',' ').title(),
                'command': lambda: self._sort_table(column=column),
            }
        }
        

    def _sort_table(self, column: str) -> None:
        """Sort the table by the given column."""
        
        # Get all tuples of values and items' indexes
        items = []
        for index in self._table.get_children(''):
            value = self._table.set(index, column)
            items.append((value, index))

        # Determine if the sorting should be ascending or descending
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
        
    def _delete_all(self) -> None:
        """Delete all items in the table."""
        
        for item in self._table.get_children():
            self._table.delete(item)

    def _configure_columns(self) -> None:
        """ 
            Set the table's columns and headings according to the stored configuration.
            Observation: 
                The configuration is only applied once due to a bug in Tkinter,
                where new columns are not being displayed properly. The creation
                of new columns are needed in case the data's colummns change. For this reason,
                it is not allowed to change the columns after the first update.
        """
        if self._first_update:
            
            # Assing columns and hide the first column
            self._table["columns"] = tuple(self._col_config.keys())
            self._table.column("#0", width=self._tree_root_col_width, stretch=bool(self._tree_root_col_width))

            # Assign headings and column attributes
            for column in self._col_config.keys():
                self._table.column(column, **self._col_config[column]['column_config'])
                self._table.heading(column, **self._col_config[column]['heading_config'])
            self._first_update = False

    def _insert_data(self) -> None:
        """ Extracts the data from the `func_get_data` and inserts it into the table."""
        
        for item in self._func_get_data():
            values = tuple(item[column] for column in self.get_columns())
            self._table.insert('', 'end', values=values)
            

    def refresh(self, event=None) -> None:
        """
            Update the table's data.
            Do not remove the `event` argument, it is used to bind the function to events.
        """
        self._delete_all()
        self._insert_data()
        self._configure_columns()
        if self._tree_expanded:
            self._expand_items()

    def get_items_data(self, selected_only: bool = False) -> list[dict[str: str|int|float]]:
        """Return the selected items."""
        
        columns = self.get_columns()
        data = []
        for item_id in self._table.selection() if selected_only else self._table.get_children():
            # get the item's data as a tuple
            item_values = self._table.item(item_id)['values']
            # Map tuple's values with the column names
            item_data = {
                # `len(item_values)` It is used over `len(columns)` because the item's values may be less than the columns, but never greater
                columns[index]: item_values[index] for index in range(len(item_values))
            }
            
            # Add the items's data to the list
            data.append(item_data)

        return data


    
