from utils import center_window, get_datetime_from_db
from database.sqlite_handler import get_session
from database.models import AccountGroup, Account
from sqlalchemy import func
from tkinter import messagebox
from custom.custom_table import CustomTable
from config_views import TABLE_COLUMN_WIDTH
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
                
                for account in sorted(parent_group.accounts, key=lambda c: c.name.lower()):
                    if isinstance(account, Account):
                        iid = self._table.insert(parent_iid, 'end', text=account.name, values=tuple({
                            'type': 'A',
                            'id': account.id,
                            'description': account.description,
                            'account_number': account.account_number,
                            'currency': account.currency.code,
                            'opened_at': get_datetime_from_db(account.opened_at),
                            'closed_at': get_datetime_from_db(account.closed_at) if account.closed_at else '',
                            'account_type': account.account_type.name,
                            'normal_side': account.account_type.normal_side,
                            'overdraft': f"$ {account.overdraft_limit:.2f}" if account.overdraft_limit else '',
                        }.values()))
                
                for group in sorted(parent_group.children, key=lambda c: c.name.lower()):
                    iid = self._table.insert(parent_iid, 'end', text=group.name, values=tuple({
                        'type': 'G',
                        'id': group.id,
                        'description': group.description,
                    }.values()))
                    recursive_children(parent_iid=iid, parent_group=group)

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
                'New Account': lambda : AccountNewView(parent=self),
                'New Group': lambda : AccountGroupNewView(parent=self),
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
        self.table.add_column(column='type', text='Type', dtype=int, anchor=tk.E, width=50)
        self.table.add_column(column='id', text='Id', dtype=int, anchor=tk.E, width=TABLE_COLUMN_WIDTH['ID'])
        self.table.add_column(column='description', dtype=str, anchor=tk.W, width=TABLE_COLUMN_WIDTH['ACCOUNT_DESCRIPTION'])
        self.table.add_column(column='account_number', dtype=str, anchor=tk.W, width=TABLE_COLUMN_WIDTH['ACCOUNT_NUMBER'])
        self.table.add_column(column='currency', dtype=str, anchor=tk.CENTER, width=TABLE_COLUMN_WIDTH['CURRENCY_CODE'])
        self.table.add_column(column='opened_at', dtype=str, anchor=tk.CENTER, width=TABLE_COLUMN_WIDTH['TIMESTAMP'])
        self.table.add_column(column='closed_at', dtype=str, anchor=tk.CENTER, width=TABLE_COLUMN_WIDTH['TIMESTAMP'])
        self.table.add_column(column='account_type', dtype=str, anchor=tk.W, width=TABLE_COLUMN_WIDTH['ACCOUNT_TYPE_NAME'])
        self.table.add_column(column='normal_side', dtype=str, anchor=tk.W, width=TABLE_COLUMN_WIDTH['ACCOUNT_TYPE_NORMAL_SIDE'])
        self.table.add_column(column='overdraft', dtype=str, anchor=tk.E, width=TABLE_COLUMN_WIDTH['MONEY'])
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
    



