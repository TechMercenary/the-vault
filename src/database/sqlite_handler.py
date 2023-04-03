from config import logger
from sqlalchemy import create_engine, text, Integer, String, Numeric, ForeignKey, func, select, event
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import registry, Session, DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from typing_extensions import Annotated
from decimal import Decimal
from config import SQLALQUEMY_ECHO
from database.models import *
import os
import pandas as pd


engine = create_engine(
    f"sqlite+pysqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'the_vault.db')}",
    echo=SQLALQUEMY_ECHO,
    logging_name=logger.name
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


Base.metadata.create_all(engine)

def get_session() -> Session:
    return Session(engine)


def db_error_handler(func):
    def wrapper(*args, **kwargs):
        result = None
        error = None
        try:
            result = func(*args, **kwargs)
        except SQLAlchemyError as e:
            error = str(e)
        return {"result": result, "error": error}
    return wrapper


class DbBase:
    @classmethod
    def new_session(cls) -> Session:
        return get_session()


class DbCurrency(DbBase):

    @classmethod
    @db_error_handler
    def get_currencies(cls, ids: int | list=None):
        with cls.new_session() as session:
            query = session.query(Currency)
            if ids:
                ids = [ids] if isinstance(ids, int) else ids
                query = query.filter(Currency.id.in_(ids))
            currencies = query.order_by(func.lower(Currency.code)).all()

            return [
                {
                    'id': currency.id,
                    'code': currency.code,
                    'description': currency.description,
                }
                for currency in currencies
            ]
        

    @classmethod
    @db_error_handler
    def new_currency(cls, code: str, description: str) -> Currency:
        currency = None
        with cls.new_session() as session:
            currency = Currency(code=code, description=description)
            session.add(currency)
            session.commit()
            
            return currency
        
    @classmethod
    @db_error_handler
    def edit_currency(cls, currency_id:int, code: str, description: str) -> Currency:
        currency = None
        with cls.new_session() as session:
            
            currency = session.query(Currency).filter_by(id=currency_id).first()
            if currency is None:
                raise ValueError(f"Currency with code '{code}' not found")

            currency.code = code
            currency.description = description

            session.commit()

            return currency


    @classmethod
    @db_error_handler
    def delete_currencies(cls, ids: int | list=None) -> True:
        with cls.new_session() as session:
            ids = [ids] if isinstance(ids, int) else ids
            for currency in session.query(Currency).filter(Currency.id.in_(ids)).all():
                if currency is not None:
                    session.delete(currency)

            session.commit()
            return True


class DbAccount(DbBase):

    @classmethod
    @db_error_handler
    def get_account_groups(cls, ids: int | list=None):
        with cls.new_session() as session:
            query = session.query(AccountGroup)
            if ids:
                ids = [ids] if isinstance(ids, int) else ids
                query = query.filter(AccountGroup.id.in_(ids))
            account_groups = query.order_by(func.lower(AccountGroup.name)).all()

            return [
                {
                    'id': account_group.id,
                    'name': account_group.name,
                    'description': account_group.description,
                    'parent_id': account_group.parent_id,
                    'accounts': [account.id for account in account_group.accounts] if account_group.accounts else '',
                }
                for account_group in account_groups
            ]
        
    @classmethod
    @db_error_handler
    def get_accounts(cls, ids: int | list=None):
        with cls.new_session() as session:
            query = session.query(Account)
            if ids:
                ids = [ids] if isinstance(ids, int) else ids
                query = query.filter(Account.id.in_(ids))
            accounts = query.order_by(func.lower(Account.name)).all()

            return [
                {
                    'id': account.id,
                    'name': account.name,
                    'description': account.description,
                    'account_number': account.account_number,
                    'currency_id': account.currency_id,
                    'currency_code': account.currency.code,
                    'normal_side': account.normal_side,
                    'opened_at': account.opened_at,
                    'closed_at': account.closed_at,
                    'account_group_id': account.account_group_id,
                    'account_type': account.account_type,
                }
                for account in accounts
            ]



if __name__ == "__main__":
   
    with get_session() as session:
        import datetime; from pytz import timezone
        account = Account(
              name='test',
              currency_id=1,
              opened_at=timezone('America/Sao_Paulo').localize(datetime.datetime.now()),
              account_group_id=1,
              account_type='ASSET',
       )
        session.add(account)
        session.commit()


    

