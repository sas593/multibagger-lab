import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
URL=os.getenv("DATABASE_URL","sqlite:///./multibagger_lab.db")
engine=create_engine(URL,connect_args={"check_same_thread":False} if URL.startswith("sqlite") else {})
SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False)
def init_db(): Base.metadata.create_all(engine)
