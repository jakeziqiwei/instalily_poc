import uuid
from datetime import datetime
from typing import List, Tuple
from sqlalchemy import create_engine, Column, String, Float, DateTime
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"
    order_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, nullable=False)
    items = Column(JSON, nullable=False) 
    status = Column(String, default="pending")

class OrderDB:
    def __init__(self, db_path="sqlite:///./src/db/orders.db"):
        self.engine = create_engine(db_path, connect_args={"check_same_thread": False})
        self.Session = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
        Base.metadata.create_all(bind=self.engine)

    def create_order(self, user_id: str, items: List[Tuple[str, int]], total_amount: float, status="pending") -> Order:
        session = self.Session()
        order = Order(user_id=user_id, items=items, total_amount=total_amount, status=status)
        session.add(order)
        session.commit()
        session.refresh(order)
        session.close()
        return order

    def get_orders_by_user(self, user_id: str) -> List[Order]:
        session = self.Session()
        orders = session.query(Order).filter(Order.user_id == user_id).all()
        session.close()
        return orders

    def get_order_by_id(self, order_id: str) -> Order:
        session = self.Session()
        order = session.query(Order).filter(Order.order_id == order_id).first()
        session.close()
        return order

    def update_order_status(self, order_id: str, new_status: str) -> Order:
        session = self.Session()
        order = session.query(Order).filter(Order.order_id == order_id).first()
        if order:
            order.status = new_status
            session.commit()
            session.refresh(order)
        session.close()
        return order
