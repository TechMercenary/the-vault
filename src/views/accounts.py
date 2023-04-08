from utils import center_window, datetime_timezone_converter
from database.sqlite_handler import get_session
from database.models import Account
from tkinter import messagebox
from config import LOCAL_TIME_ZONE
from custom.templates_view import TemplateNewEdit, FrameInput
from database.common_queries import \
    get_account_groups_values, \
    get_account_types_values, \
    get_currencies_values
import tkinter as tk
import pendulum


# TODO: Add the accounting `side` and its update on the account type change
class AccountNewView(TemplateNewEdit):
    """A view for creating a new account."""

    def __init__(self, parent: tk.Toplevel | tk.Tk,):
        super().__init__(parent, title="New Account")
        
    def set_inputs(self, input_frame: FrameInput):
        input_frame.add_input_combobox(
            key="group",
            func_get_values=get_account_groups_values,
            state="readonly",
            width=30,
        )
        input_frame.add_input_entry(key="name", width=30)
        input_frame.add_input_entry(key="description", width=30)
        input_frame.add_input_entry(key="account_number", width=30)
        input_frame.add_input_combobox(
            key="currency",
            func_get_values=get_currencies_values,
            state="readonly",
            width=10,
        )
        input_frame.add_input_datetime(key="opened_at", width=30, default_now=True)
        input_frame.add_input_datetime(key="closed_at", width=30, default_now=True)
        input_frame.add_input_combobox(
            key="account_type",
            func_get_values=get_account_types_values,
            state="readonly",
            width=50,
        )
        
    def get_validated_values(self, input_values: dict) -> dict:
        if not input_values["name"]:
            raise ValueError("Name is required")
        return {
            'name': input_values['name'],
            'description': input_values['description'],
            'account_number': input_values['account_number'],
            'currency_id': input_values['currency']['key'],
            'opened_at': input_values['opened_at'],
            'closed_at': input_values['closed_at'],
            'account_group_id': input_values['group']['key'],
            'account_type': input_values['account_type']['key'],
        }
        
    def on_accept(self, values: list[dict]):
        
        opened_at = pendulum.parser\
            .parse(values['opened_at'], tz=LOCAL_TIME_ZONE)\
                .in_timezone('UTC')\
                    .format('YYYY-MM-DD HH:mm:ss')
        
        closed_at = pendulum.parser\
            .parse(values['closed_at'], tz=LOCAL_TIME_ZONE)\
                .in_timezone('UTC')\
                    .format('YYYY-MM-DD HH:mm:ss')
        
        with get_session() as session:
            session.add(Account(
                name=values['name'],
                description=values['description'],
                account_number=values['account_number'],
                currency_id=values['currency_id'],
                opened_at=opened_at,
                closed_at=closed_at,
                account_group_id=values['account_group_id'],
                account_type=values['account_type']
            ))
            session.commit()


class AccountEditView(TemplateNewEdit):
    """A view for editing an account."""

    def __init__(self, parent: tk.Toplevel | tk.Tk, account_id: int):
        self.account_id = account_id

        try:
            with get_session() as session:
                if not (account:= session.query(Account).filter(Account.id == self.account_id).first()):
                    raise ValueError(f"Account {self.account_id} not found")
                    
                self.account = account
                    
                super().__init__(parent, title="Edit Account")
            
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

                self.input_frame.set_values({
                    "group": self.account.account_group.alias,
                    "name": self.account.name,
                    "description": self.account.description,
                    "account_number": self.account.account_number,
                    "currency": self.account.currency.code,
                    "opened_at": opened_at,
                    "closed_at": closed_at,
                    "account_type": self.account.account_type.value,
                })
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.parent.focus()
            self.destroy()
        
    def set_inputs(self, input_frame: FrameInput):
        input_frame.add_input_combobox(
            key="group",
            func_get_values=get_account_groups_values,
            state="readonly",
            width=30,
        )
        input_frame.add_input_entry(key="name", width=30)
        input_frame.add_input_entry(key="description", width=30)
        input_frame.add_input_entry(key="account_number", width=30)
        input_frame.add_input_combobox(
            key="currency",
            func_get_values=get_currencies_values,
            state="readonly",
            width=30,
        )
        input_frame.add_input_datetime(key="opened_at", width=30)
        input_frame.add_input_datetime(key="closed_at", width=30)
        input_frame.add_input_combobox(
            key="account_type",
            func_get_values=get_account_types_values,
            state="readonly",
            width=50,
        )
    
    def get_validated_values(self, input_values: dict) -> dict:
        if not input_values["name"]:
            raise ValueError("Name cannot be empty")
        
        return {
            'name': input_values['name'],
            'description': input_values['description'],
            'account_number': input_values['account_number'],
            'currency_id': input_values['currency']['key'],
            'opened_at': input_values['opened_at'],
            'closed_at': input_values['closed_at'],
            'account_group_id': input_values['group']['key'],
            'account_type': input_values['account_type']['key'],
        }


    def on_accept(self, values: list[dict]):

        opened_at = pendulum.parser\
            .parse(values['opened_at'], tz=LOCAL_TIME_ZONE)\
                .in_timezone('UTC')\
                    .format('YYYY-MM-DD HH:mm:ss')

        closed_at = pendulum.parser\
            .parse(values['closed_at'], tz=LOCAL_TIME_ZONE)\
                .in_timezone('UTC')\
                    .format('YYYY-MM-DD HH:mm:ss')

        with get_session() as session:
            self.account.name=values['name']
            self.account.description=values['description']
            self.account.account_number=values['account_number']
            self.account.currency_id=values['currency_id']
            self.account.opened_at=opened_at
            self.account.closed_at=closed_at
            self.account.account_group_id=values['account_group_id']
            self.account.account_type=values['account_type']

            session.add(self.account)
            session.commit()



if __name__ == '__main__':
    from utils import toplevel_set_active
    
    root = tk.Tk()
    toplevel = AccountNewView(root)
    center_window(window=root, context_window=None)
    toplevel_set_active(window=toplevel)
    center_window(window=toplevel, context_window=root)
    
    root.mainloop()
    



