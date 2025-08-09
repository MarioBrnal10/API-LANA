from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Formato de Railway para MySQL
DATABASE_URL = os.getenv("DATABASE_URL", "mysql://root:xCJhHTKkZujUpKSFPQdCvLSlmfFGlYok@hopper.proxy.rlwy.net:38040/railway")

# Convertir la URL de Railway al formato que SQLAlchemy espera para MySQL
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()