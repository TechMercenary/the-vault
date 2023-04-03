from typing import Callable
from utils import center_window, wrapper_message_error, datetime_timezone_converter
from database.sqlite_handler import DbAccount, DbCurrency, get_session
from database.models import AccountGroup, Account, Currency
from sqlalchemy import func
from tkinter import messagebox
from functools import partial
from custom_widgets.table import CustomTable
from custom_widgets.toplevel import CustomTopLvel
from config import logger, AccountType, MAP_ACCOUNT_TYPE_TO_SIDE, LOCAL_TIME_ZONE
from views.account_groups import AccountGroupEditView, AccountGroupNewView
import tkinter as tk
import tkinter.ttk as ttk
import pandas as pd
import numpy as np
import pendulum


class AccountTable(CustomTable):
    """ Adapts the CustomTable to allow showing the groups and accounts in as a dependency tree."""

    def __init__(self, parent: tk.Toplevel | tk.Tk, selectmode: str = "extended"):
        super().__init__(parent, selectmode=selectmode, first_col_width=200, tree_expanded=True)

    def insert_data(self):
        """
            Overrides the `super` method in order to process the data before each insert:

            1. Extract the data from the database and then create two dataframes with the data.
            2. Create a template for the row data, which have the same columns as the table (in the same order).
            3. Fill the template with the data from the database using recursion:
                3.1 First it loops through the root account groups, and inserts the accounts associated with the group.
                3.2 Then it loops through the sub groups and accounts, while inserting first the accounts and then the sub groups.
        """

        with get_session() as session:
            def recursive_children(parent_iid: str, parent_group: AccountGroup):
                children = sorted(parent_group.accounts, key=lambda c: c.name.lower())
                children.extend(sorted(parent_group.children, key=lambda c: c.name.lower()))
                
                for child in children:
                    
                    opened_at = getattr(child, 'opened_at','')
                    if opened_at:
                        opened_at = datetime_timezone_converter(opened_at, tz_from='UTC', tz_to=LOCAL_TIME_ZONE)
                    
                    closed_at = getattr(child, 'closed_at','')
                    if closed_at:
                        closed_at = datetime_timezone_converter(closed_at, tz_from='UTC', tz_to=LOCAL_TIME_ZONE)
                    
                    
                    iid = self._table.insert(parent_iid, 'end', text=child.name, values=tuple({
                        'type': 'A' if isinstance(child, Account) else 'G',
                        'id': child.id,
                        'description': child.description,
                        'account_number': getattr(child, 'account_number',''),
                        'currency': getattr(getattr(child, 'currency',{}),'code',''),
                        'opened_at': opened_at,
                        'closed_at': closed_at,
                        'account_type': getattr(getattr(child, 'account_type', {}),'value',''),
                    }.values()))
                    if isinstance(child, AccountGroup):
                        recursive_children(parent_iid=iid, parent_group=child)

            # Iterate through the root groups
            for group in session.query(AccountGroup).filter_by(parent_id=None).order_by(func.lower(AccountGroup.name)).all():
                iid = self._table.insert('', 'end', text=group.name, values=tuple({
                    'type': 'G',
                    'id': group.id,
                    'description': group.description,
                }.values()))
                recursive_children(parent_iid=iid, parent_group=group)


class AccountListView(CustomTopLvel):
    """A view for the chart of accounts."""

    def __init__(self, parent: tk.Toplevel | tk.Tk):
        super().__init__(parent, title="Chart of Accounts")
        
        buttons_frame = self.get_buttons_frame(parent=self.main_frame)
        buttons_frame.grid(column=0, row=0, sticky="ew")
        buttons_frame.grid_anchor("center")
        buttons_frame.columnconfigure("all", pad=15)
        
        self.create_table(column=0, row=1)
        
        close_frame = self.get_close_frame(parent=self.main_frame)
        close_frame.grid(column=0, row=2, sticky="ew")
        close_frame.grid_anchor("center")
        
        center_window(window=self, context_window=self.parent)
        self.bind("<<NewAccountAdded>>", self.update_table)
        self.bind("<<AccountEdited>>", self.update_table)
        self.bind("<<ItemDeleted>>", self.update_table)
        self.bind("<<NewAccountGroupAdded>>", self.update_table)
        self.bind("<<AccountGroupEdited>>", self.update_table)
        self.bind("<<AccountGroupDeleted>>", self.update_table)
        
        self.bind('<Delete>', self.btn_delete_item)
        self.bind('<F2>', self.btn_edit_item)
        self.bind('<Double-1>', self.btn_edit_item)
        self.bind('<Return>', self.btn_edit_item)


    def get_buttons_frame(self, parent):
        """Create the buttons frame."""

        buttons_frame = ttk.Frame(parent, padding=10)
        ttk.Button(buttons_frame, text='New Account', command=self.btn_new_account).grid(column=0, row=0)
        ttk.Button(buttons_frame, text='New Group', command=self.btn_new_account_group).grid(column=1, row=0)
        ttk.Button(buttons_frame, text='Edit', command=self.btn_edit_item).grid(column=2, row=0)
        ttk.Button(buttons_frame, text='Delete', command=self.btn_delete_item).grid(column=3, row=0)
        return buttons_frame


    def update_table(self, event):
        """Update the table with the latest data from the database."""
        self.table.update_table()
        logger.debug("Chart of Accounts updated")


    def create_table(self, column: int, row: int):
        """Create the table"""

        self.table = AccountTable(parent=self.main_frame)
        self.table.add_column(column='type', text='Type', dtype=int, anchor=tk.E, minwidth=50, width=50)
        self.table.add_column(column='id', text='Id', dtype=int, anchor=tk.E, minwidth=50, width=50)
        self.table.add_column(column='description', dtype=str, anchor=tk.W, minwidth=10, width=200)
        self.table.add_column(column='account_number', dtype=str, anchor=tk.W, width=200)
        self.table.add_column(column='currency', dtype=str, anchor=tk.CENTER, minwidth=10, width=60)
        self.table.add_column(column='opened_at', dtype=str, anchor=tk.CENTER, minwidth=10, width=120)
        self.table.add_column(column='closed_at', dtype=str, anchor=tk.CENTER, minwidth=10, width=120)
        self.table.add_column(column='account_type', dtype=str, anchor=tk.W, minwidth=10, width=100)
        self.table.update_table()
        self.table.grid(column=column, row=row, sticky="nswe")


    def get_close_frame(self, parent):
        """Create the close frame."""
        close_frame = ttk.Frame(parent, padding=5)
        ttk.Button(close_frame, text='Cerrar', command=self.destroy).grid(column=0, row=0)
        return close_frame


    def btn_new_account(self):
        """Open the new account view."""
        AccountNewView(parent=self)
        
    def btn_new_account_group(self):
        """Open the new account group view."""
        AccountGroupNewView(parent=self)


    def btn_edit_item(self, event=None):
        """Open the edit view for the first item in the selected items list."""

        if data := self.table.get_items_data(selected_only=True):
            if data[0]['type'] == 'A':
                AccountEditView(parent=self, account_id=data[0]['id'])
            else:
                AccountGroupEditView(parent=self, account_group_id=data[0]['id'])


    def btn_delete_item(self, event=None):
        """Delete the selected items"""

        if messagebox.askyesno("Delete confirmation", "Are you sure you want to delete the selected items?"):
            
            try:
                account_ids = [
                    items_data['id']
                    for items_data in self.table.get_items_data(selected_only=True) if items_data['type'] == 'A'
                ]
                account_group_ids = [
                    items_data['id']
                    for items_data in self.table.get_items_data(selected_only=True) if items_data['type'] == 'G'
                ]
                
                with get_session() as session:
                    accounts_deleted = session.query(Account).filter(Account.id.in_(account_ids)).delete(synchronize_session=False)
                    groups_deleted = session.query(AccountGroup).filter(AccountGroup.id.in_(account_group_ids)).delete(synchronize_session=False)
                    session.commit()

            except Exception as e:
                messagebox.showerror("Error", str(e))
                return None
                
            messagebox.showinfo("Success", f"Accounts deleted: {accounts_deleted}, Groups deleted: {groups_deleted}")
            self.event_generate("<<ItemDeleted>>")



class _ChangeTemplate(CustomTopLvel):
    """ A template view for create and edit accounts"""
    
    def __init__(self, parent: tk.Toplevel | tk.Tk, title: str):
        super().__init__(parent, title=title, resizable=False)

        self.input_frame = self.get_input_frame(parent=self.main_frame)
        self.input_frame.grid(column=0, row=0)

        self.buttons_frame = self.get_buttons_frame(parent=self.main_frame)
        self.buttons_frame.grid(column=0, row=2, sticky="ew")
        self.buttons_frame.grid_anchor("center")

        center_window(window=self, context_window=self.parent)
        self.bind("<Return>", self.btn_accept)
        self.update_normal_side()
        
    def btn_accept(self, event=None):
        raise NotImplementedError

    def update_normal_side(self, event=None):
        self.normal_side_var.set(MAP_ACCOUNT_TYPE_TO_SIDE[self.account_type_var.get()])


    def get_input_frame(self, parent):
        """Create the input frame."""
        
        self.account_group_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        self.account_number_var = tk.StringVar()
        self.currency_var = tk.StringVar()
        self.normal_side_var = tk.StringVar()
        self.opened_at_var = tk.StringVar()
        self.closed_at_var = tk.StringVar()
        self.account_type_var = tk.StringVar()

        input_frame = ttk.Frame(parent, padding=10)

        row_num = 0
        column_label = 0
        column_input = 1

        # Account Group
        ttk.Label(input_frame, text='Account Group')\
            .grid(column=column_label, row=row_num, padx=5, pady=5, sticky="w")
        cbox_account_group = ttk.Combobox(input_frame, textvariable=self.account_group_var, width=30, state="readonly")
        cbox_account_group.grid(column=column_input, row=row_num, sticky="w")
        with get_session() as session:
            account_groups = session.query(AccountGroup).order_by(AccountGroup.name).all()
            self.account_group_map = {group.alias: group.id for group in account_groups} # Workaround: a map that associates the alias with the id
            cbox_account_group.config(values=list(self.account_group_map.keys()))
        cbox_account_group.current(0)
        row_num += 1

        # Name
        ttk.Label(input_frame, text='Name')\
            .grid(column=column_label, row=row_num, padx=5, pady=5, sticky="w")
        ttk.Entry(input_frame, textvariable=self.name_var, width=30, takefocus=True)\
            .grid(column=column_input, row=row_num, sticky="w"); row_num += 1
        # Description
        ttk.Label(input_frame, text='Descripcion')\
            .grid(column=column_label, row=row_num, padx=5, pady=5, sticky="w")
        ttk.Entry(input_frame, textvariable=self.desc_var, width=30)\
            .grid(column=column_input, row=row_num, sticky="w"); row_num += 1
        # Account Number
        ttk.Label(input_frame, text='Account Number')\
            .grid(column=column_label, row=row_num, padx=5, pady=5, sticky="w")
        ttk.Entry(input_frame, textvariable=self.account_number_var, width=30)\
            .grid(column=column_input, row=row_num, sticky="w"); row_num += 1
        # Currency
        ttk.Label(input_frame, text='Currency')\
            .grid(column=column_label, row=row_num, padx=5, pady=5, sticky="w")
        cbox_currency = ttk.Combobox(input_frame, textvariable=self.currency_var, width=10, state="readonly")
        cbox_currency.grid(column=column_input, row=row_num, sticky="w")
        
        with get_session() as session:
            currencies = session.query(Currency).order_by(Currency.code).all()
        cbox_currency.config(values=[currency.code for currency in currencies])
        cbox_currency.current(0)
        row_num += 1
            
        # Opened At
        ttk.Label(input_frame, text='Opened At')\
            .grid(column=column_label, row=row_num, padx=5, pady=5, sticky="w")
        ttk.Entry(input_frame, textvariable=self.opened_at_var, width=30)\
            .grid(column=column_input, row=row_num, sticky="w")

        # Default value            
        self.opened_at_var.set(pendulum.now(tz="America/Argentina/Buenos_Aires").format("YYYY-MM-DD HH:mm"))
            
        row_num += 1
        
        # Closed At
        ttk.Label(input_frame, text='Closed At')\
            .grid(column=column_label, row=row_num, padx=5, pady=5, sticky="w")
        ttk.Entry(input_frame, textvariable=self.closed_at_var, width=30)\
            .grid(column=column_input, row=row_num, sticky="w"); row_num += 1
            
        # Account Type
        ttk.Label(input_frame, text='Account Type')\
            .grid(column=column_label, row=row_num, padx=5, pady=5, sticky="w")
            
        cbox_account_type = ttk.Combobox(input_frame, textvariable=self.account_type_var, width=30, state="readonly")
        cbox_account_type.grid(column=column_input, row=row_num, sticky="w")
        cbox_account_type.config(values=list(AccountType.__members__.keys()))
        cbox_account_type.current(0)
        
        cbox_account_type.bind("<<ComboboxSelected>>", self.update_normal_side)
        
        row_num += 1

        # Normal Side
        ttk.Label(input_frame, text='Normal Side')\
            .grid(column=column_label, row=row_num, padx=5, pady=5, sticky="w")
        ttk.Label(input_frame, text="", textvariable=self.normal_side_var)\
            .grid(column=column_input, row=row_num, pady=5, sticky="w")
            
        row_num += 1
        
        return input_frame


    def get_buttons_frame(self, parent):
        """Create the buttons frame."""
        
        buttons_frame = ttk.Frame(parent)
        
        ttk.Button(buttons_frame, text='Aceptar', command=self.btn_accept).grid(column=0, row=2)
        ttk.Frame(buttons_frame, width=50).grid(column=1, row=2) # spacer
        ttk.Button(buttons_frame, text='Cancelar', command=self.destroy).grid(column=2, row=2)
        
        return buttons_frame
    
    def get_validated_inputs(self):
        try:
            # Validations
            
            opened_at = datetime_timezone_converter(
                    date_str=self.opened_at_var.get(),
                    tz_from=LOCAL_TIME_ZONE,
                    tz_to='UTC',
                )
            assert opened_at is not None, f"Invalid date format on OPENED_AT ({self.opened_at_var.get()}). Use YYYY-MM-DD MM:HH:SS"

            closed_at = datetime_timezone_converter(
                    date_str=self.closed_at_var.get(),
                    tz_from=LOCAL_TIME_ZONE,
                    tz_to='UTC',
                ) if self.closed_at_var.get() else ''
            
            assert closed_at is not None, f"Invalid date format on CLOSED_AT ({self.closed_at_var.get()}). Use YYYY-MM-DD MM:HH:SS"

            account_group_id = self.account_group_map.get(self.account_group_var.get())
            assert account_group_id is not None, f"Account Group {self.account_group_var.get()} not found"

            assert self.name_var.get() != "", "Name is required"

            with get_session() as session:
                currency = session.query(Currency).filter(Currency.code == self.currency_var.get()).first()
                assert currency is not None, f"Currency {self.currency_var.get()} not found"

            return {
                'name': self.name_var.get(),
                'description': self.desc_var.get(),
                'account_number': self.account_number_var.get(),
                'currency_id': currency.id,
                'opened_at': opened_at,
                'closed_at': closed_at,
                'account_group_id': account_group_id,
                'account_type': self.account_type_var.get(),
            }

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.focus()
            return None
    
    
class AccountNewView(_ChangeTemplate):
    """A view for creating a new account."""

    def __init__(self, parent: tk.Toplevel | tk.Tk):
        super().__init__(parent, title="New Account")

       
    def btn_accept(self, event=None):
        validated_inputs = self.get_validated_inputs()
        if validated_inputs is None:
            return None
        
        try:
            with get_session() as session:
                session.add(Account(
                    name=validated_inputs['name'],
                    description=validated_inputs['description'],
                    account_number=validated_inputs['account_number'],
                    currency_id=validated_inputs['currency_id'],
                    opened_at=validated_inputs['opened_at'],
                    closed_at=validated_inputs['closed_at'],
                    account_group_id=validated_inputs['account_group_id'],
                    account_type=validated_inputs['account_type']
                ))
                session.commit()
                
            messagebox.showinfo("Success", "Account created successfully!")
            self.parent.event_generate("<<NewAccountAdded>>")
            self.parent.focus()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.focus()


class AccountEditView(_ChangeTemplate):
    """A view for editing an account."""

    def __init__(self, parent: tk.Toplevel | tk.Tk, account_id: int):
        super().__init__(parent, title="Edit Account")
        self.account_id = account_id
        self.load_data()

    def load_data(self):
        try:
            with get_session() as session:
                self.account = session.query(Account).filter(Account.id == self.account_id).first()
                assert self.account is not None, f"Account {self.account_id} not found"
                
                opened_at = datetime_timezone_converter(
                    date_str=str(self.account.opened_at),
                    tz_from='UTC',
                    tz_to=LOCAL_TIME_ZONE,
                )
                
                closed_at = datetime_timezone_converter(
                    date_str=str(self.account.closed_at),
                    tz_from='UTC',
                    tz_to=LOCAL_TIME_ZONE,
                ) if self.account.closed_at else ''
                
                self.account_group_var.set(self.account.account_group.alias)
                self.name_var.set(self.account.name)
                self.desc_var.set(self.account.description)
                self.account_number_var.set(self.account.account_number)
                self.currency_var.set(self.account.currency.code)
                self.opened_at_var.set(opened_at)
                self.closed_at_var.set(closed_at)
                self.account_type_var.set(self.account.account_type.value)
                
                self.update_normal_side()

        except Exception as e:
            messagebox.showerror("Error", str(e))
        
        
    def btn_accept(self, event=None):
        validated_inputs = self.get_validated_inputs()
        if validated_inputs is None:
            return None
        
        try:
            with get_session() as session:
                self.account.name=validated_inputs['name']
                self.account.description=validated_inputs['description']
                self.account.account_number=validated_inputs['account_number']
                self.account.currency_id=validated_inputs['currency_id']
                self.account.opened_at=validated_inputs['opened_at']
                self.account.closed_at=validated_inputs['closed_at']
                self.account.account_group_id=validated_inputs['account_group_id']
                self.account.account_type=validated_inputs['account_type']

                session.add(self.account)
                session.commit()
                
            messagebox.showinfo("Success", "Account edited successfully!")
            self.parent.event_generate("<<AccountEdited>>")
            self.parent.focus()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.focus()


if __name__ == '__main__':
    from utils import test_toplevel_class
    test_toplevel_class(AccountListView)

