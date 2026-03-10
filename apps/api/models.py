from sqlalchemy import Column, Integer, String, DateTime, func
from database import Base

class Comparison(Base):
   __tablename__ = "comparisons"

   id = Column(Integer, primary_key=True, index=True)
   title = Column(String, nullable=False) 
   created_at = Column(DateTime, server_default=func.now())