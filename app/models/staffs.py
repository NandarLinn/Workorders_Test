from sqlalchemy import Column, String
from db import Base

'''
Staffs Model for storing staff related details.
Staffs have different roles and status.
'''

class Staffs(Base):
    __tablename__ = "staffs"

    staff_id = Column(String, primary_key=True, index=True, nullable=False)
    staff_name = Column(String, nullable=False)
    role = Column(String, nullable=False) # Maid, Maid Supervisor, Technician, Supervisor
    status = Column(String, nullable=False) # Available, Assigned, On Leave
