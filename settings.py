from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

CSV_LOCATION = "C:\Development\TCSS555\dataRev2"
MODEL_PATH = "C:\Development\TCSS555"
POSTGRES_USERNAME = "postgres"
POSTGRES_PASSWORD = "postgres"
POSTGRES_SERVERNAME = "localhost"
POSTGRES_PORT = "5432"
POSTGRES_DATABASENAME = "authorpaper"
POSTGRESQL_CONNECTION_STRING = "postgresql+psycopg2://{0}:{1}@{2}:{3}/{4}".format(POSTGRES_USERNAME, POSTGRES_PASSWORD, POSTGRES_SERVERNAME, POSTGRES_PORT, POSTGRES_DATABASENAME)

__postgres_engine = create_engine(POSTGRESQL_CONNECTION_STRING)
__postgres_sessionmaker = sessionmaker(bind=__postgres_engine)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = __postgres_sessionmaker()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
