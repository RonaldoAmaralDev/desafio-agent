from sqlalchemy import Column, String, DateTime, Integer, func
from .base import Base

class Prompt(Base):
    __tablename__ = "prompts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    content = Column(String, nullable=False)
    version = Column(String, default="1.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())