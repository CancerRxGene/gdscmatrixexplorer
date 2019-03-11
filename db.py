import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

engine = sa.create_engine('gevent_sqlite:///data/matrixexplorer.db', connect_args={'check_same_thread':False})
Base = declarative_base()

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
session = Session()
