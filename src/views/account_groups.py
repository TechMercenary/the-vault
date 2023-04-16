from database.sqlite_handler import get_session
from database.models import AccountGroup, AccountGroup
from database.common_queries import get_account_groups_values
from tkinter import messagebox
from custom.templates_view import TemplateChange, FrameInput
from views.config_views import VIEW_WIDGET_WIDTH
import tkinter as tk


class AccountGroupNewView(TemplateChange):
    """A view for creating a new account group"""

    def __init__(self, parent: tk.Toplevel | tk.Tk):
        super().__init__(parent, title="New Account Group")

    def set_inputs(self, input_frame: FrameInput):
        input_frame.add_input_combobox(
            key="parent",
            func_get_values=get_account_groups_values,
            enable_empty_option=True,
            state="readonly",
            width=VIEW_WIDGET_WIDTH['ACCOUNT_GROUP_ALIAS'],
        )
        input_frame.add_input_entry(key="name", width=VIEW_WIDGET_WIDTH['ACCOUNT_NAME'])
        input_frame.add_input_entry(key="description", width=VIEW_WIDGET_WIDTH['DESCRIPTION'])
       
    def get_validated_values(self, input_values: dict) -> dict:
        if not input_values['name']:
            raise ValueError("Name cannot be empty")
        return {
            'name': input_values['name'],
            'description': input_values['description'],
            'parent_id': input_values['parent']['key'],
        }
       
    def on_accept(self, values: list[dict]):
        with get_session() as session:
            session.add(AccountGroup(
                name=values['name'],
                description=values['description'],
                parent_id=values['parent_id'],
            ))
            session.commit()

    
class AccountGroupEditView(TemplateChange):
    """A view for editing an account group."""

    def __init__(self, parent: tk.Toplevel | tk.Tk, account_group_id: int):
        
        with get_session() as session:
            if not (account_group := session.query(AccountGroup).filter(AccountGroup.id == account_group_id).first()):
                messagebox.showerror("Error", f"Account Group {account_group_id} not found")
                self.parent.focus()
                self.destroy()
                
            self.account_group = account_group
            
            super().__init__(parent, title="Edit Account Group")

            self.input_frame.set_values({
                "id": self.account_group.id,
                "parent": self.account_group.parent.alias if self.account_group.parent else "<Empty>",
                "name": self.account_group.name,
                "description": self.account_group.description
            })
            
            
    def get_account_groups_values(self):
        with get_session() as session:
            def get_exluded_groups(parent_group):
                excluded_groups = [parent_group.id]
                if not parent_group.children:
                    return excluded_groups
                for child in parent_group.children:
                    excluded_groups.extend(get_exluded_groups(parent_group=child))
                return excluded_groups

            excluded_groups = get_exluded_groups(
                    parent_group=session.query(AccountGroup)\
                        .filter(AccountGroup.id == self.account_group.id)\
                            .first()
                )
            available_groups = session.query(AccountGroup).filter(AccountGroup.id.not_in(excluded_groups)).all()
        
            return {group.id: group.alias for group in available_groups}
        
            
    def set_inputs(self, input_frame: FrameInput):
        input_frame.add_input_label(key="id", text='Id', width=VIEW_WIDGET_WIDTH['ID'])
        input_frame.add_input_combobox(
            key="parent",
            func_get_values=self.get_account_groups_values,
            enable_empty_option=True,
            state="readonly",
            width=VIEW_WIDGET_WIDTH['ACCOUNT_GROUP_ALIAS'],
        )
        input_frame.add_input_entry(key="name", width=VIEW_WIDGET_WIDTH['ACCOUNT_NAME'])
        input_frame.add_input_entry(key="description", width=VIEW_WIDGET_WIDTH['DESCRIPTION'])

    def get_validated_values(self, input_values: dict) -> dict:
        if not input_values['name']:
            raise ValueError("Name cannot be empty")
        return {
            'name': input_values['name'],
            'description': input_values['description'],
            'parent_id': input_values['parent']['key'],
        }
    

    def on_accept(self, values: list[dict]):
        with get_session() as session:
            self.account_group.name=values['name']
            self.account_group.description=values['description']
            self.account_group.parent_id=values['parent_id']

            session.add(self.account_group)
            session.commit()


if __name__ == '__main__':
    from utils import test_toplevel_class
    # test_toplevel_class(AccountGroupEditView, account_group_id=4)
    test_toplevel_class(AccountGroupNewView)

