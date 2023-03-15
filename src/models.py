import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

# from src.database import Base, engine

SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
     
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    role = Column(String, CheckConstraint("role = \"MEMBER\" or role = \"ADMIN\" or role = \"TECHNICIAN\""), nullable=False)
    designation = Column(String)
    company = Column(String)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)