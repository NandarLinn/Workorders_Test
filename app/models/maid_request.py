from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from db import Base

'''
MaidRequests can only be created by staffs with role 'Maid Supervisor'.
Maid Supervisor can assign MaidRequests to maids.
Start and finish time to specific room will be recorded.
'''

class MaidRequests(Base):
    __tablename__ = "maid_requests"

    order_number = Column(String, primary_key=True, index=True, nullable=False)
    created_by = Column(String, ForeignKey('staffs.staff_id'), nullable=False)
    assigned_to = Column(String, ForeignKey('staffs.staff_id'), nullable=False)
    room_number = Column(String, ForeignKey('rooms.room_number'), nullable=False)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    description = Column(String)
    status = Column(String, default='Created', nullable=False) # Created, Assigned, In Progress, Done, Cancelled