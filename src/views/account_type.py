from database.sqlite_handler import get_session
from database.models import AccountType
from tkinter import messagebox
from sqlalchemy import func
from custom.custom_table import CustomTable
from custom.templates_view import TemplateListView, TemplateChange, FrameInput
from views.config_views import VIEW_WIDGET_WIDTH, TABLE_COLUMN_WIDTH

import tkinter as tk


class AccountTypeChangeView(TemplateChange):
    """A view for editing a account type."""

    def __init__(self, parent: tk.Toplevel | tk.Tk, account_type_id: int = None):
        
        if account_type_id:
            with get_session() as session:
                if not (account_type:=session.query(AccountType).filter(AccountType.id == account_type_id).first()):
                    messagebox.showerror("Error", f"Account Type {account_type_id} not found")
                    self.parent.focus()
                    self.destroy()
                    
            self.account_type = account_type
        
            super().__init__(parent, title="Edit Account Type")

            self.input_frame.set_values({
                "id": self.account_type.id,
                "name": self.account_type.name,
                "normal_side": self.account_type.normal_side
            })
        else:
            super().__init__(parent, title="New Account Type")


    def set_inputs(self, input_frame: FrameInput):
        if getattr(self, "account_type", None):
            input_frame.add_input_label(key="id", text='Id', width=VIEW_WIDGET_WIDTH['ID'])
        input_frame.add_input_entry(key="name", width=VIEW_WIDGET_WIDTH['ACCOUNT_TYPE_NAME'])
        input_frame.add_input_combobox(key="normal_side", width=VIEW_WIDGET_WIDTH['ACCOUNT_TYPE_NORMAL_SIDE'], func_get_values=lambda: {0: "DEBIT", 1: "CREDIT"})

    
    def get_validated_values(self, input_values: dict) -> dict:
        if not input_values["name"]:
            raise ValueError("Name is required")
        if input_values["normal_side"]['value'] not in ["DEBIT", "CREDIT"]:
            raise ValueError("Normal side must be either 'DEBIT' or 'CREDIT'")
        return {
                'name': input_values["name"],
                'normal_side': input_values["normal_side"]['value']
            }

        
    def on_accept(self, values: list[dict]):
        with get_session() as session:
            if getattr(self, "account_type", None):
                self.account_type.name = values['name']
                self.account_type.normal_side = values['normal_side']
                account_type = self.account_type
            else:
                account_type = AccountType(
                    name=values['name'],
                    normal_side=values['normal_side']
                )
            session.add(account_type)
            session.commit()


class AccountTypeListView(TemplateListView):
    """A view for the account type."""

    __model__ = AccountType
    __edit_view__ = AccountTypeChangeView
    __new_view__ = AccountTypeChangeView

    def __init__(self, parent: tk.Toplevel | tk.Tk):
        super().__init__(parent, title="Account Types")
  
  
    def get_data(self):
        """Get the account types from the database."""

        with get_session() as session:
            account_types = session.query(AccountType).order_by(func.lower(AccountType.name)).all()
            return [
                {
                    'id': account_type.id,
                    'name': account_type.name,
                    'normal_side': account_type.normal_side,
                }
                for account_type in account_types
            ]
    
    def add_columns(self, table: CustomTable):
        table.add_column(column='id', dtype=int, anchor=tk.E, width=TABLE_COLUMN_WIDTH['ID'])
        table.add_column(column='name', dtype=str, anchor=tk.W, width=TABLE_COLUMN_WIDTH['ACCOUNT_TYPE_NAME'], is_sorted_asc=True)
        table.add_column(column='normal_side', dtype=str, anchor=tk.W, width=TABLE_COLUMN_WIDTH['ACCOUNT_TYPE_NORMAL_SIDE'])


if __name__ == '__main__':
    from utils import test_toplevel_class
    test_toplevel_class(AccountTypeListView)

