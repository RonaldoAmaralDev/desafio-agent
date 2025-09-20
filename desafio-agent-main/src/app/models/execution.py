from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, func
from .base import Base

class Execution(Base):
    __tablename__ = "executions"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    input = Column(String, nullable=False)
    output = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())