from config import logger
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from datetime import datetime
from config import SQLALQUEMY_ECHO
from database.models import *
import os


engine = create_engine(
    f"sqlite+pysqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'the_vault.db')}",
    echo=SQLALQUEMY_ECHO,
    logging_name=logger.name
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
        This is used to enable foreign key constraints in SQLite.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


Base.metadata.create_all(engine)

def get_session() -> Session:
    return Session(engine)




    

