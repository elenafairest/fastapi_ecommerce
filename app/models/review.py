from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from app.backend.db import Base


class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    comment = Column(String, nullable=True)
    comment_date = Column(Date, default=True)
    grade = Column(Integer)
    is_active = Column(Boolean, default=True)
