from sqlalchemy import  Column, Integer, String
from database import Base

class Conversions(Base):
    __tablename__ = "conversions"

    id = Column(Integer, primary_key=True, index=True)
    original = Column(String)
    converted = Column(String)
    status = Column(String)