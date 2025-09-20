from sqlalchemy import Column, String, DateTime, Integer, func, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Prompt(Base):
    __tablename__ = "prompts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    content = Column(String, nullable=False)
    version = Column(String, default="1.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    agent = relationship("Agent", back_populates="prompts")