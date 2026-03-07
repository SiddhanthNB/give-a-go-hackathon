import lib.utils.constants as constants
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(constants.DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
