from sqlalchemy import Column, String, Text, DateTime, Integer, func, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import Base


class Prompt(Base):
    __tablename__ = "prompts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    version = Column(String(20), default="1.0")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)
    agent = relationship("Agent", back_populates="prompts")

    def __repr__(self):
        return f"<Prompt(id={self.id}, name={self.name}, version={self.version})>"


Index("idx_prompt_agent_name", Prompt.agent_id, Prompt.name)