from utils import center_window, datetime_timezone_converter
from database.sqlite_handler import get_session
from database.models import AccountGroup, Account
from sqlalchemy import func
from tkinter import messagebox
from custom.custom_table import CustomTable
from config import LOCAL_TIME_ZONE
from views.account_groups import AccountGroupEditView, AccountGroupNewView
from views.accounts import AccountNewView, AccountEditView
from custom.templates_view import CustomTopLevel
import tkinter as tk


class ChartOfAccountTable(CustomTable):
    """ Adapts the CustomTable to allow showing the groups and accounts in as a dependency tree."""

    def __init__(
            self,
            parent: tk.Toplevel | tk.Tk,
            selectmode: str = "extended",
        ):
        super().__init__(
            parent,
            selectmode=selectmode,
            tree_root_col_width=200,
            tree_expanded=True
        )

    def _insert_data(self):
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


class ChartOfAccountView(CustomTopLevel):
    """A view for the chart of accounts."""

    def __init__(self, parent: tk.Toplevel | tk.Tk):
        super().__init__(
            parent,
            title="Chart of Accounts",
            top_buttons_config={
                'New Account': self.on_new_account,
                'New Group': self.on_new_account_group,
                'Edit': self.on_edit_item,
                'Delete': self.on_delete_item
            },
            footer_buttons_config={
                'Close': self.destroy,
            },
        )
        
        self.set_table()
        center_window(window=self, context_window=self.parent)
        self.bind("<<EventUpdateTable>>", self.table.refresh)
        
        self.bind('<Delete>', self.on_delete_item)
        self.bind('<F2>', self.on_edit_item)
        self.bind('<Double-1>', self.on_edit_item)
        self.bind('<Return>', self.on_edit_item)
        
        
    def on_new_account(self):
        """Open the new account view."""
        AccountNewView(parent=self)
        
    def on_new_account_group(self):
        """Open the new account group view."""
        AccountGroupNewView(parent=self)
        
    def on_edit_item(self, event=None):
        """Open the edit view for the first item in the selected items list."""
        if data := self.table.get_items_data(selected_only=True):
            if data[0]['type'] == 'A':
                AccountEditView(parent=self, account_id=data[0]['id'])
            else:
                AccountGroupEditView(parent=self, account_group_id=data[0]['id'])

    def on_delete_item(self, event=None):
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
                    session.query(Account).filter(Account.id.in_(account_ids)).delete(synchronize_session=False)
                    session.query(AccountGroup).filter(AccountGroup.id.in_(account_group_ids)).delete(synchronize_session=False)
                    session.commit()

            except Exception as e:
                messagebox.showerror("Error", str(e))
                return None
            self.event_generate("<<EventUpdateTable>>")
    
    
    def set_table(self):
        """Create the table"""

        self.table = ChartOfAccountTable(parent=self.body_frame)
        self.table.add_column(column='type', text='Type', dtype=int, anchor=tk.E, minwidth=50, width=50)
        self.table.add_column(column='id', text='Id', dtype=int, anchor=tk.E, minwidth=50, width=50)
        self.table.add_column(column='description', dtype=str, anchor=tk.W, minwidth=10, width=200)
        self.table.add_column(column='account_number', dtype=str, anchor=tk.W, width=200)
        self.table.add_column(column='currency', dtype=str, anchor=tk.CENTER, minwidth=10, width=60)
        self.table.add_column(column='opened_at', dtype=str, anchor=tk.CENTER, minwidth=10, width=120)
        self.table.add_column(column='closed_at', dtype=str, anchor=tk.CENTER, minwidth=10, width=120)
        self.table.add_column(column='account_type', dtype=str, anchor=tk.W, minwidth=10, width=150)
        self.table.refresh()
        self.table.grid(column=0, row=0, sticky="nswe")
    


if __name__ == '__main__':
    from utils import toplevel_set_active
    
    root = tk.Tk()
    toplevel = ChartOfAccountView(root)
    center_window(window=root, context_window=None)
    toplevel_set_active(window=toplevel)
    center_window(window=toplevel, context_window=root)
    
    root.mainloop()
    



