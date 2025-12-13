# models/app_data.py
# 普通应用数据模型 (非敏感数据)

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean
from sqlalchemy.sql import func
from .database import AppDataBase


class AppConfig(AppDataBase):
    """Model for storing non-sensitive application configuration."""
    __tablename__ = 'app_config'
    
    key = Column(String(255), primary_key=True, nullable=False)
    value = Column(Text, nullable=True)
    category = Column(String(100), default='general')  # telegram, cloud, emby, etc.
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f'<AppConfig(key={self.key}, category={self.category})>'


class AdminCredential(AppDataBase):
    """Model for admin authentication (password hash stored encrypted in secrets.db)."""
    __tablename__ = 'admin_credentials'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, default='admin')
    two_factor_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f'<AdminCredential(username={self.username})>'


class TaskHistory(AppDataBase):
    """Model for storing task execution history."""
    __tablename__ = 'task_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_type = Column(String(100), nullable=False)  # offline, strm, organize
    status = Column(String(50), default='pending')  # pending, running, completed, failed
    details = Column(Text)  # JSON details
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f'<TaskHistory(id={self.id}, task_type={self.task_type}, status={self.status})>'
