from config import logger
from sqlalchemy import create_engine, text, Integer, String, Numeric, ForeignKey, func, select, event
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import registry, Session, DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from typing_extensions import Annotated
from decimal import Decimal
from config import SQLALQUEMY_ECHO
import os


type_pk = Annotated[int, mapped_column(primary_key=True)]
type_desc = Annotated[str|None, mapped_column(nullable=False, default="")]
timestamp = Annotated[datetime, mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP()),]
str_30 = Annotated[str, 30]
str_50 = Annotated[str, 50]
num_12_4 = Annotated[Decimal, 12]
num_6_2 = Annotated[Decimal, 6]


class Base(DeclarativeBase):
    pass


class Currency(Base):
    __tablename__ = "currency"
    id: Mapped[type_pk]
    code: Mapped[str] = mapped_column(String(3), nullable=False, unique=True)
    description: Mapped[type_desc]

###########

class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[str|None]
    addresses: Mapped[list["Address"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

class Address(Base):
    __tablename__ = "address"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    user: Mapped["User"] = relationship(back_populates="addresses")
    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"

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


class DB:
    @classmethod
    def new_session(cls) -> Session:
        return get_session()
    
    @staticmethod
    def error_handler(func):
        def wrapper(*args, **kwargs):
            result = None
            error = None
            try:
                result = func(*args, **kwargs)
            except SQLAlchemyError as e:
                error = str(e)
            return {"result": result, "error": error}
        return wrapper
    

    @classmethod
    @error_handler
    def get_currencies(cls, ids: int | list=None):
        with cls.new_session() as session:
            query = session.query(Currency)
            if ids is not None:
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
    @error_handler
    def new_currency(cls, code: str, description: str) -> Currency:
        currency = None
        with cls.new_session() as session:
            currency = Currency(code=code, description=description)
            session.add(currency)
            session.commit()
            
        return currency
        
    @classmethod
    @error_handler
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
    @error_handler
    def delete_currencies(cls, ids: int | list=None) -> True:
        with cls.new_session() as session:
            ids = [ids] if isinstance(ids, int) else ids
            for currency in session.query(Currency).filter(Currency.id.in_(ids)).all():
                if currency is not None:
                    session.delete(currency)

            session.commit()
        return True



if __name__ == "__main__":
   
    result = DB.delete_currencies(ids=[])
    print(result['error'], result['result'])

