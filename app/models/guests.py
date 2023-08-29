from sqlalchemy import Column, ForeignKey, String, DateTime, Integer
from db import Base

'''
Guests Model for storing guest related details to know which guest is staying in which room.
Checkin and Checkout date will be recorded.
'''

class Guests(Base):
    __tablename__ = "guests"

    id = Column(Integer, primary_key=True, index=True)
    guest_name = Column(String, nullable=False)
    checkin_date = Column(DateTime, nullable=False)
    checkout_date = Column(DateTime, nullable=False)
    phone_number = Column(String, nullable=False)
    room_number = Column(String, ForeignKey("rooms.room_number"), nullable=False)