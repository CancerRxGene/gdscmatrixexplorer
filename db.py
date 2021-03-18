import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

engine = sa.create_engine('gevent_sqlite:///data/matrixexplorer.db', connect_args={'check_same_thread':False})
#engine = sa.create_engine('postgresql+psycopg2://combox_dev_admin:keneec34fds@vm-pg-cmp-score-dev.internal.sanger.ac.uk:5432/cmp_dev')

Base = declarative_base()

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
session = Session()
