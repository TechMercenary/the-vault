from utils import center_window, get_datetime_from_db, get_datetime_to_db
from database.sqlite_handler import get_session
from database.models import Account, AccountType
from tkinter import messagebox
from custom.templates_view import TemplateChange, FrameInput
from database.common_queries import \
    get_account_groups_values, \
    get_account_types_values, \
    get_currencies_values
from views.config_views import VIEW_WIDGET_WIDTH
import tkinter as tk


def _get_values_for_db(input_values: dict) -> dict:
        if not input_values["name"]:
            raise ValueError("Name cannot be empty")
        if input_values["closed_at"] and input_values["opened_at"] > input_values["closed_at"]:
            raise ValueError("Opened at must be before closed at")
        
        return {
            'name': input_values['name'],
            'description': input_values['description'],
            'account_number': input_values['account_number'],
            'currency_id': input_values['currency']['key'],
            'opened_at': get_datetime_to_db(input_values['opened_at']),
            'closed_at': get_datetime_to_db(input_values['closed_at']) if input_values['closed_at'] else None,
            'account_group_id': input_values['group']['key'],
            'account_type_id': input_values['account_type']['key'],
        }


class AccountNewView(TemplateChange):
    """A view for creating a new account."""

    def __init__(self, parent: tk.Toplevel | tk.Tk,):
        super().__init__(parent, title="New Account")
        self.input_frame.set_binding(
            key="account_type",
            bindings={
                "<<ComboboxSelected>>": self.update_normal_side,
            }
        )
        self.update_normal_side()


    def update_normal_side(self, event=None):
        with get_session() as session:
            account_type = session\
                .query(AccountType)\
                    .filter(AccountType.id == self.input_frame.get_values()["account_type"]["key"])\
                        .first()
            self.input_frame.set_values({
                "normal_side": account_type.normal_side,
            })
        
    def set_inputs(self, input_frame: FrameInput):
        input_frame.add_input_combobox(
            key="group",
            func_get_values=get_account_groups_values,
            state="readonly",
            width=30,
        )
        input_frame.add_input_entry(key="name", width=VIEW_WIDGET_WIDTH['ACCOUNT_NAME'])
        input_frame.add_input_entry(key="description", width=VIEW_WIDGET_WIDTH['DESCRIPTION'])
        input_frame.add_input_entry(key="account_number", width=VIEW_WIDGET_WIDTH['DESCRIPTION'])
        input_frame.add_input_combobox(
            key="currency",
            func_get_values=get_currencies_values,
            state="readonly",
            width=10,
        )
        input_frame.add_input_pendulum(key="opened_at", default_now=True)
        input_frame.add_input_pendulum(key="closed_at", default_now=False)
        input_frame.add_input_combobox(
            key="account_type",
            func_get_values=get_account_types_values,
            state="readonly",
            width=50,
        )
        input_frame.add_input_label(key="normal_side", width=VIEW_WIDGET_WIDTH['ACCOUNT_TYPE_NORMAL_SIDE'])
        
    def get_validated_values(self, input_values: dict) -> dict:
        return _get_values_for_db(input_values)
        
    def on_accept(self, values: list[dict]):
        with get_session() as session:
            session.add(Account(
                name=values['name'],
                description=values['description'],
                account_number=values['account_number'],
                currency_id=values['currency_id'],
                opened_at=values['opened_at'],
                closed_at=values['closed_at'],
                account_group_id=values['account_group_id'],
                account_type_id=values['account_type_id']
            ))
            session.commit()


class AccountEditView(TemplateChange):
    """A view for editing an account."""

    def __init__(self, parent: tk.Toplevel | tk.Tk, account_id: int):
        self.account_id = account_id

        try:
            with get_session() as session:
                if not (account:= session.query(Account).filter(Account.id == self.account_id).first()):
                    raise ValueError(f"Account {self.account_id} not found")
                    
                self.account = account
                    
                super().__init__(parent, title="Edit Account")
            
                self.input_frame.set_values({
                    "id": self.account.id,
                    "group": self.account.account_group.alias,
                    "name": self.account.name,
                    "description": self.account.description,
                    "account_number": self.account.account_number,
                    "currency": self.account.currency.code,
                    "opened_at": get_datetime_from_db(self.account.opened_at),
                    "closed_at": get_datetime_from_db(self.account.closed_at) if self.account.closed_at else '',
                    "account_type": self.account.account_type.name,
                })

            self.input_frame.set_binding(
                key="account_type",
                bindings={
                    "<<ComboboxSelected>>": self.update_normal_side,
                }
            )
            self.update_normal_side()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.parent.focus()
            self.destroy()
        
    def update_normal_side(self, event=None):
        with get_session() as session:
            account_type = session\
                .query(AccountType)\
                    .filter(AccountType.id == self.input_frame.get_values()["account_type"]["key"])\
                        .first()
            self.input_frame.set_values({
                "normal_side": account_type.normal_side,
            })
        
    def set_inputs(self, input_frame: FrameInput):
        input_frame.add_input_label(key="id", text='Id', width=VIEW_WIDGET_WIDTH['ID'])
        input_frame.add_input_combobox(
            key="group",
            func_get_values=get_account_groups_values,
            state="readonly",
            width=30,
        )
        input_frame.add_input_entry(key="name", width=VIEW_WIDGET_WIDTH['ACCOUNT_NAME'])
        input_frame.add_input_entry(key="description", width=VIEW_WIDGET_WIDTH['DESCRIPTION'])
        input_frame.add_input_entry(key="account_number", width=VIEW_WIDGET_WIDTH['DESCRIPTION'])
        input_frame.add_input_combobox(
            key="currency",
            func_get_values=get_currencies_values,
            state="readonly",
            width=30,
        )
        input_frame.add_input_pendulum(key="opened_at")
        input_frame.add_input_pendulum(key="closed_at")
        input_frame.add_input_combobox(
            key="account_type",
            func_get_values=get_account_types_values,
            state="readonly",
            width=50,
        )
        input_frame.add_input_label(key="normal_side", width=VIEW_WIDGET_WIDTH['ACCOUNT_TYPE_NORMAL_SIDE'])
    
    def get_validated_values(self, input_values: dict) -> dict:
        return _get_values_for_db(input_values)

    def on_accept(self, values: list[dict]):
        with get_session() as session:
            self.account.name=values['name']
            self.account.description=values['description']
            self.account.account_number=values['account_number']
            self.account.currency_id=values['currency_id']
            self.account.opened_at=values['opened_at']
            self.account.closed_at=values['closed_at']
            self.account.account_group_id=values['account_group_id']
            self.account.account_type_id=values['account_type_id']

            session.add(self.account)
            session.commit()



if __name__ == '__main__':
    from utils import toplevel_set_active
    
    root = tk.Tk()
    toplevel = AccountEditView(root, 1)
    center_window(window=root, context_window=None)
    toplevel_set_active(window=toplevel)
    center_window(window=toplevel, context_window=root)
    
    root.mainloop()
    



