from sqlalchemy import Column, String, DateTime, func, Index
from datetime import datetime
from models.database import Base


class Secret(Base):
    """Model for storing encrypted secrets."""
    __tablename__ = 'secrets'
    
    key = Column(String(255), primary_key=True, unique=True, nullable=False)
    encrypted_value = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_key', 'key'),
    )
    
    def __repr__(self):
        return f'<Secret(key={self.key}, updated_at={self.updated_at})>'
