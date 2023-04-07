from utils import center_window, datetime_timezone_converter
from database.sqlite_handler import get_session
from database.models import AccountGroup, Account, Currency, AccountGroup
from tkinter import messagebox
from custom.toplevel import CustomTopLvel
from config import logger, LOCAL_TIME_ZONE
import tkinter as tk
import tkinter.ttk as ttk


# TODO: Use new templates
class _ChangeTemplate(CustomTopLvel):
    """ A template view for create and edit account groups"""
    
    def __init__(self, parent: tk.Toplevel | tk.Tk, title: str):
        super().__init__(parent, title=title, resizable=False)

        self.input_frame = self.get_input_frame(parent=self.main_frame)
        self.input_frame.grid(column=0, row=0)

        self.buttons_frame = self.get_buttons_frame(parent=self.main_frame)
        self.buttons_frame.grid(column=0, row=2, sticky="ew")
        self.buttons_frame.grid_anchor("center")

        center_window(window=self, context_window=self.parent)
        self.bind("<Return>", self.btn_accept)
        

    def btn_accept(self, event=None):
        raise NotImplementedError


    def get_account_groups_list(self):
        raise NotImplementedError


    def get_input_frame(self, parent):
        """Create the input frame."""
        
        self.parent_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.desc_var = tk.StringVar()

        input_frame = ttk.Frame(parent, padding=10)

        row_num = 0
        column_label = 0
        column_input = 1

        # Parent
        ttk.Label(input_frame, text='Parent')\
            .grid(column=column_label, row=row_num, padx=5, pady=5, sticky="w")
        cbox_parent = ttk.Combobox(input_frame, textvariable=self.parent_var, width=30, state="readonly")
        cbox_parent.grid(column=column_input, row=row_num, sticky="w")
        cbox_parent.config(values=self.get_account_groups_list())
            
        cbox_parent.current(0)
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
            parent_id = self.account_group_map.get(self.parent_var.get())
            assert parent_id is not None, f"Account Group {self.parent_var.get()} not found"
            parent_id = int(parent_id) if parent_id != '' else None

            assert self.name_var.get() != "", "Name is required"

            return {
                'parent_id': parent_id,
                'name': self.name_var.get(),
                'description': self.desc_var.get(),
            }

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.focus()
            return None

    
class AccountGroupNewView(_ChangeTemplate):
    """A view for creating a new account group"""

    def __init__(self, parent: tk.Toplevel | tk.Tk):
        super().__init__(parent, title="New Account Group")

    def get_account_groups_list(self):
        # Workaround: a map that associates the alias with the id
        self.account_group_map = {'<Empty>': ''}
        with get_session() as session:
            account_groups = session.query(AccountGroup).order_by(AccountGroup.name).all()
            self.account_group_map.update({group.alias: group.id for group in account_groups})

        account_groups_list = list(self.account_group_map.keys())
        account_groups_list.sort(key=lambda x: x.lower())
        
        return account_groups_list

       
    def btn_accept(self, event=None):
        validated_inputs = self.get_validated_inputs()
        if validated_inputs is None:
            return None
        
        try:
            with get_session() as session:
                session.add(AccountGroup(
                    name=validated_inputs['name'],
                    description=validated_inputs['description'],
                    parent_id=validated_inputs['parent_id'],
                ))
                session.commit()

            messagebox.showinfo("Success", "Account Group created successfully!")
            self.parent.event_generate("<<NewAccountGroupAdded>>")
            self.parent.focus()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.focus()


class AccountGroupEditView(_ChangeTemplate):
    """A view for editing an account group."""

    def __init__(self, parent: tk.Toplevel | tk.Tk, account_group_id: int):
        self.account_group_id = account_group_id
        self.set_account_group_map()
        super().__init__(parent, title="Edit Account Group")
        self.load_data()


    def load_data(self):
        try:
            with get_session() as session:
                self.account_group = session.query(AccountGroup).filter(AccountGroup.id == self.account_group_id).first()
                assert self.account_group is not None, f"Account Group {self.account_group_id} not found"
                
                parent_alias = self.account_group.parent.alias if self.account_group.parent else self.get_account_groups_list()[0]
                
                self.parent_var.set(parent_alias)
                self.name_var.set(self.account_group.name)
                self.desc_var.set(self.account_group.description)

        except Exception as e:
            messagebox.showerror("Error", str(e))
        
    
    def set_account_group_map(self):
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
                        .filter(AccountGroup.id == self.account_group_id)\
                            .first()
                )
            available_groups = session.query(AccountGroup).filter(AccountGroup.id.not_in(excluded_groups)).all()
        
            self.account_group_map = {'<Empty>': ''}
            self.account_group_map.update({group.alias: group.id for group in available_groups})
    
    
    def get_account_groups_list(self):
        account_groups_list = list(self.account_group_map.keys())
        account_groups_list.sort(key=lambda x: x.lower())
        
        return account_groups_list

        
    def btn_accept(self, event=None):
        validated_inputs = self.get_validated_inputs()
        if validated_inputs is None:
            return None
        
        try:
            with get_session() as session:
                self.account_group.name=validated_inputs['name']
                self.account_group.description=validated_inputs['description']
                self.account_group.parent_id=validated_inputs['parent_id']

                session.add(self.account_group)
                session.commit()
                
            messagebox.showinfo("Success", "Account Group edited successfully!")
            self.parent.event_generate("<<AccountGroupEdited>>")
            self.parent.focus()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.focus()


if __name__ == '__main__':
    from utils import test_toplevel_class
    test_toplevel_class(AccountGroupEditView, account_group_id=6)

