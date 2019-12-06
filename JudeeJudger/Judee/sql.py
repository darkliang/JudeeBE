from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy
db_string = 'postgres+psycopg2://wht:123456@10.20.1.155:54321/Judee_dev'
db_engine = create_engine(db_string) 
DBSession = sessionmaker(bind=db_engine)
session = DBSession()
session.
print(db)