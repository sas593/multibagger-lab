from datetime import datetime
from sqlalchemy import String,Float,Integer,DateTime,Text
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
class Base(DeclarativeBase): pass
class User(Base):
    __tablename__="users"; id:Mapped[int]=mapped_column(Integer,primary_key=True); email:Mapped[str]=mapped_column(String(255),unique=True,index=True); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class PortfolioHolding(Base):
    __tablename__="portfolio_holdings"; id:Mapped[int]=mapped_column(Integer,primary_key=True); user_id:Mapped[int]=mapped_column(Integer,index=True); ticker:Mapped[str]=mapped_column(String(32),index=True); quantity:Mapped[float]=mapped_column(Float); average_buy_price:Mapped[float]=mapped_column(Float)
class PortfolioSettings(Base):
    __tablename__="portfolio_settings"; user_id:Mapped[int]=mapped_column(Integer,primary_key=True); xirr_pct:Mapped[float|None]=mapped_column(Float,nullable=True); available_cash:Mapped[float]=mapped_column(Float,default=0)
class AuditLog(Base):
    __tablename__="audit_logs"; id:Mapped[int]=mapped_column(Integer,primary_key=True); user_id:Mapped[int]=mapped_column(Integer,index=True); action:Mapped[str]=mapped_column(String(100)); payload:Mapped[str]=mapped_column(Text); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
