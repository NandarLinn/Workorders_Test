from sqlalchemy import Column, ForeignKey, String, DateTime
from db import Base

'''
CleaningRequests can only be created by staffs with role 'Maid Supervisor'.
Maid Supervisor can assign CleaningRequests to maids. Start and finish time to specific room will be recorded.
'''
class CleaningRequests(Base):
    __tablename__ = "cleaning_requests"

    order_number = Column(String, primary_key=True, index=True, nullable=False)
    created_by = Column(String, ForeignKey("staffs.staff_id"), nullable=False)
    room_number = Column(String, ForeignKey("rooms.room_number"), nullable=False)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    assigned_to = Column(String)
    status = Column(String, default='Created', nullable=False) # Created, Assigned, In Progress, Done, Cancelled