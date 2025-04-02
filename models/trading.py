from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .base import Base
import enum

class TradeType(str, enum.Enum):
    """Types of trades."""
    BUY = "buy"
    SELL = "sell"

class PositionStatus(str, enum.Enum):
    """Status of trading positions."""
    OPEN = "open"
    CLOSED = "closed"
    PENDING = "pending"

class Position(Base):
    """Model for trading positions."""
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    symbol = Column(String, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    size = Column(Float, nullable=False)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    status = Column(Enum(PositionStatus), default=PositionStatus.OPEN, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="positions")
    trades = relationship("Trade", back_populates="position")
    
    def __repr__(self):
        return f"<Position {self.symbol} {self.status}>"

class Trade(Base):
    """Model for individual trades."""
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    position_id = Column(Integer, ForeignKey("position.id"), nullable=False)
    type = Column(Enum(TradeType), nullable=False)
    price = Column(Float, nullable=False)
    size = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="trades")
    position = relationship("Position", back_populates="trades")
    
    def __repr__(self):
        return f"<Trade {self.type} {self.symbol}>"

class PerformanceMetrics(Base):
    """Model for user performance metrics."""
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    total_pnl = Column(Float, default=0.0)
    average_pnl = Column(Float, default=0.0)
    max_win = Column(Float, default=0.0)
    max_loss = Column(Float, default=0.0)
    profit_factor = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="performance_metrics")
    
    def __repr__(self):
        return f"<PerformanceMetrics {self.user_id} {self.period_start} to {self.period_end}>" 