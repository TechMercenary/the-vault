
from sqlalchemy import func
from database.sqlite_handler import get_session, AccountGroup, Currency
from config import AccountTypeEnum

# TODO: Search and move all common queries to this file

def get_account_groups_values() -> list[dict]:
    with get_session() as session:
        account_groups = session.query(AccountGroup).order_by(AccountGroup.name).all()
        return {group.id: group.alias for group in account_groups}

def get_account_types_values() -> list[dict]:
    return {key: key for key in AccountTypeEnum.__members__.keys()}


def get_currencies_values() -> list[dict]:
    with get_session() as session:
        currencies = session.query(Currency).order_by(func.lower(Currency.code)).all()
        return {currency.id: currency.code for currency in currencies}



