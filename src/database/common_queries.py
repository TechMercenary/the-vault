
from sqlalchemy import func
from database.sqlite_handler import get_session, AccountGroup, Currency, AccountType, Account
from config import AccountTypeEnum


def get_account_groups_values() -> list[dict[int: str]]:
    """ 
        Returns the list of account groups as a dictionary of {id: alias} pairs.
    """
    with get_session() as session:
        account_groups = session.query(AccountGroup).order_by(func.lower(AccountGroup.name)).all()
        return {group.id: group.alias for group in account_groups}


def get_accounts_values() -> list[dict[int: str]]:
    """ 
        Returns the list of accounts as a dictionary of {id: alias} pairs.
    """
    with get_session() as session:
        # accounts = session.query(AccountGroup).order_by(func.lower(AccountGroup.alias)).all()
        accounts = session.query(Account).all()
        return {account.id: account.alias for account in accounts}


def get_account_types_values() -> list[dict[str: str]]:
    """ 
        Returns the list of account_types as a dictionary of {id: value} pairs.
    """
    with get_session() as session:
        account_types = session.query(AccountType).order_by(func.lower(AccountType.name)).all()
        return {account_type.id: account_type.name for account_type in account_types}
    

def get_currencies_values() -> list[dict[int: str]]:
    """
        Returns the list of currencies as a dictionary of {id: code} pairs.
    """
    with get_session() as session:
        currencies = session.query(Currency).order_by(func.lower(Currency.code)).all()
        return {currency.id: currency.code for currency in currencies}

