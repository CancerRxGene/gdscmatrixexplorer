import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = sa.create_engine('sqlite:///data/db.sql')
Base = declarative_base()

session = sessionmaker(bind=engine)()
