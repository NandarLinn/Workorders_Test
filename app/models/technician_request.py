from sqlalchemy import Column, String, DateTime, ForeignKey
from db import Base

''' 
TechnicianRequests can be created by guests or staffs with role 'Supervisor'.
Supervisor can assign TechnicianRequests to technicians.
Start and finish time to specific room will be recorded.
'''

class TechnicianRequests(Base):
    __tablename__ = "technician_requests"

    order_number = Column(String, primary_key=True, index=True, nullable=False)
    created_by = Column(String, nullable=False) # GuestID or StaffID
    room_number = Column(String, ForeignKey("rooms.room_number"), nullable=False)
    assigned_to = Column(String, ForeignKey("staffs.staff_id"), nullable=True) # Null if not assigned yet
    defect_type = Column(String) # Plumbing, Electrical, TV
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    status = Column(String, default='Created', nullable=False) # Created, Assigned, In Progress, Done, Cancelled