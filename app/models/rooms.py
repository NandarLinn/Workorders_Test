from sqlalchemy import Column, String
from db import Base

'''
In this case, we are going to create a new model called Rooms. Room numbers are unique, so we will use it as the primary key.
Room type is the type of room, e.g. Single, Double, Twin, etc. This field can be used later for recommendation system. Which room type is the most popular, etc.
Room status is the status of the room, e.g. Vacant or Occupied. Price is skipped for now.
So, staff can use this system to check which room is vacant or which room is Occupied.
'''

class Rooms(Base):
    __tablename__ = "rooms"

    room_number = Column(String, primary_key=True, index=True, nullable=False)
    room_type = Column(String, nullable=False)
    room_status = Column(String, nullable=False) # Occupied, Vacant