from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class QueryLog(Base):
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(String, nullable=False)
    db_user = Column(String, default="system") # 'user' is a reserved SQL word
    timestamp = Column(DateTime, default=datetime.utcnow)
    query_type = Column(String)
    table_name = Column(String)
    rows_affected = Column(Integer, default=0)
    execution_time = Column(Float, default=0.0)
    anomaly_score = Column(Float)
    status = Column(String) # ALLOWED, FLAGGED, BLOCKED

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("query_logs.id"))
    risk_level = Column(String)
    explanation = Column(String) # For GenAI later
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemSettings(Base):
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String, unique=True, index=True)
    setting_value = Column(Float)