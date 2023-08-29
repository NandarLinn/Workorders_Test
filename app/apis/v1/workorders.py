from typing import Any, Annotated
from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from models import Staffs, Guests
from db import get_db
import uuid
from datetime import datetime
from models import TechnicianRequests, MaidRequests, AmenityRequests, CleaningRequests, Rooms
from dateutil.parser import parse

'''
UUID is grobally unique identifier.So the chances of encountering a duplicate ID even in external data are very, very small.
They can be generated without the need to check against a central node, so in a distributed system, each node can generate UUIDs autonomously without fear of duplication or consistency issues.
Due to these reason UUID is used as order_number.
'''

router = APIRouter()

def get_current_user(user_id: str, db: Session = Depends(get_db)):
    user_id = user_id.upper()
    if not user_id.isupper():
        guest = db.query(Guests).filter(Guests.id == user_id).first()
        if not guest:
            raise HTTPException(status_code=404, detail="User not found: Cannot create workorder")
        return [guest.id]
    else:
        staff = db.query(Staffs).filter(Staffs.staff_id == user_id).first()
        if not staff:
            raise HTTPException(status_code=404, detail="User not found: Cannot create workorder")
        return [staff.staff_id, staff.role]
    
@router.get("/workorders/{user_id}/workorder_requests")
async def get_workorders_requests(user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    result = []

    if len(user) == 2 and user[1] == 'maid supervisor':
        # For Maid Supervisors
        cleaning_requests = db.query(CleaningRequests).all()
        maid_requests = db.query(MaidRequests).all()
        amenity_requests = db.query(AmenityRequests).all()

        # Check for empty lists and append accordingly
        if cleaning_requests:
            result.append({"cleaning_requests": cleaning_requests})
        if maid_requests:
            result.append({"maid_requests": maid_requests})
        if amenity_requests:
            result.append({"amenity_requests": amenity_requests})

    elif len(user) == 2 and user[1] == "supervisor":
        # For Supervisors
        technician_requests = db.query(TechnicianRequests).all()

        # Check for empty list and append accordingly
        if technician_requests:
            result.append({"technician_requests": technician_requests})

    elif len(user) == 1:
        # For Guests
        guest = db.query(Guests).filter(Guests.id == user[0]).first()

        if guest.checkout_date > datetime.now():
            cleaning_requests = db.query(CleaningRequests).filter(CleaningRequests.room_number == guest.room_number).all()
            maid_requests = db.query(MaidRequests).filter(MaidRequests.room_number == guest.room_number).all()
            technician_requests = db.query(TechnicianRequests).filter(TechnicianRequests.room_number == guest.room_number).all()
            amenity_requests = db.query(AmenityRequests).filter(AmenityRequests.created_by == guest.id).all()

            if cleaning_requests:
                result.append({"cleaning_requests": cleaning_requests})
            if maid_requests:
                result.append({"maid_requests": maid_requests})
            if technician_requests:
                result.append({"technician_requests": technician_requests})
            if amenity_requests:
                result.append({"amenity_requests": amenity_requests})
        else:
            raise HTTPException(status_code=403, detail="You have already checked out. Cannot see workorders.")

    else:
        raise HTTPException(status_code=403, detail="Permission denied: Cannot see workorders.")

    return {"request": result}

@router.post("/workorders/{user_id}/cleaning_requests")
async def create_cleaning_request(
    user: str = Depends(get_current_user),
    room_number: str = Form(...),
    started_at: str = Form(...),
    finished_at: str = Form(...),
    assigned_to: str = Form(...),
    status: str = Form(...),
    db: Session = Depends(get_db)
) -> Any:
    
    if len(user) == 2 and user[1]=='maid supervisor':
        # For Maid Supervisors
        cleaning_request_data = {
            "order_number": str(uuid.uuid4()),
            "created_by": user[0].upper(),
            "room_number": room_number.upper(),
            "started_at": parse(started_at),
            "finished_at": parse(finished_at),
            "assigned_to": assigned_to.upper(),
            "status": status.lower()
        }
        
        staff = db.query(Staffs).filter(Staffs.staff_id == assigned_to.upper()).first()
        room = db.query(Rooms).filter(Rooms.room_number == cleaning_request_data.get("room_number")).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Staff not found")
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        if status.lower() not in ["created", "assigned"]:
            raise HTTPException(status_code=400, detail="Invalid status. assigned, created are only allowed.")
        
        if staff.role == "cleaning staff":
            conflicting_cleaning_request = (
                db.query(CleaningRequests)
                .filter(
                    CleaningRequests.room_number == cleaning_request_data["room_number"],
                    CleaningRequests.started_at < cleaning_request_data["finished_at"],
                    CleaningRequests.finished_at > cleaning_request_data["started_at"]
                )
                .first()
            )

            if conflicting_cleaning_request:
                raise HTTPException(status_code=409, detail="The room is already assigned to another cleaning staff during the requested time range")

            conflicting_staff_request = (
                db.query(CleaningRequests)
                .filter(
                    CleaningRequests.assigned_to == cleaning_request_data["assigned_to"],
                    CleaningRequests.started_at < cleaning_request_data["finished_at"],
                    CleaningRequests.finished_at > cleaning_request_data["started_at"]
                )
                .first()
            )
           
            if conflicting_staff_request:
                raise HTTPException(status_code=409, detail="The cleaning staff is already assigned to another room during the requested time range")
            
            if staff.status == "on leave":
                raise HTTPException(status_code=400, detail="This cleaning staff is on leave.")
            
            cleaning_request = CleaningRequests(**cleaning_request_data)
            db.add(cleaning_request)
            db.commit()
            db.refresh(cleaning_request)
            staff.status = "assigned"
            db.commit()
            db.refresh(staff)

        else:
            raise HTTPException(status_code=403, detail="Assign to a cleaning staff.")
    else:
        raise HTTPException(status_code=403, detail="Permission denied: Cleaning request can only be created by staffs with role 'Maid Supervisor'")
    return {"message": f"Cleaning request created successfully"}

@router.post("/workorders/{user_id}/maid_requests")
def create_maid_requests(
    user: dict = Depends(get_current_user),
    room_number: str = Form(...),
    started_at: str = Form(...),
    finished_at: str = Form(...),
    assigned_to: str = Form(...),
    description: str = Form(...),
    status: str = Form(...),
    db: Session = Depends(get_db)
) -> Any:
    
    if len(user) == 2 and user[1]=='maid supervisor':
        # For Maid Supervisors
        maid_request_data = {
            "order_number": str(uuid.uuid4()),
            "created_by": user[0].upper(),
            "room_number": room_number.upper(),
            "started_at": parse(started_at),
            "finished_at": parse(finished_at),
            "assigned_to": assigned_to.upper(),
            "description": description,
            "status": status.lower()
        }
        staff = db.query(Staffs).filter(Staffs.staff_id == assigned_to.upper()).first()        
        room = db.query(Rooms).filter(Rooms.room_number == room_number.upper()).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Staff not found")
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        if status.lower() not in ["created", "assigned"]:
            raise HTTPException(status_code=400, detail="Invalid status. created, assigned are only allowed.")
        
        if staff.role == "maid":
            conflicting_maid_request = (
                db.query(MaidRequests)
                .filter(
                    MaidRequests.room_number == maid_request_data["room_number"],
                    MaidRequests.started_at < maid_request_data["finished_at"],
                    MaidRequests.finished_at > maid_request_data["started_at"]
                )
                .first()
            )

            if conflicting_maid_request:
                raise HTTPException(status_code=409, detail="The room is already assigned to another maid during the requested time range")

            conflicting_staff_request = (
                db.query(MaidRequests)
                .filter(
                    MaidRequests.assigned_to == maid_request_data["assigned_to"],
                    MaidRequests.started_at < maid_request_data["finished_at"],
                    MaidRequests.finished_at > maid_request_data["started_at"]
                )
                .first()
            )
           
            if conflicting_staff_request:
                raise HTTPException(status_code=409, detail="The maid is already assigned to another room during the requested time range")
            
            if staff.status == "on leave":
                raise HTTPException(status_code=400, detail="This maid is on leave.")
            
            maid_request = MaidRequests(**maid_request_data)
            db.add(maid_request)
            db.commit()
            db.refresh(maid_request)

        else:
            raise HTTPException(status_code=403, detail="Assign to a maid.")
    else:
        raise HTTPException(status_code=403, detail="Permission denied: Maid request can only be created by staffs with role 'Maid Supervisor'")
    return {"message": f"Maid request created successfully"}

@router.post("/workorders/{user_id}/technician_requests")
def create_technician_request(
    user: str = Depends(get_current_user),
    room_number: str = Form(...),
    started_at: Annotated[str | None, Form()] = '8/29/2021 10:00',
    finished_at: Annotated[str | None, Form()] = '8/29/2021 10:00',
    assigned_to: str = 'TEMP002',
    status: str = 'created',
    defect_type: str = Form(...),
    db: Session = Depends(get_db)
) -> Any:
    if len(user) == 2 and user[1]=='supervisor':
        # For Supervisors
        technician_request_data = {
            "order_number": str(uuid.uuid4()),
            "created_by": user[0].upper(),
            "room_number": room_number.upper(),
            "started_at": parse(started_at),
            "finished_at": parse(finished_at),
            "assigned_to": assigned_to.upper(),
            "defect_type": defect_type,
            "status": status.lower()
        }
     
        staff = db.query(Staffs).filter(Staffs.staff_id == technician_request_data.get('assigned_to')).first()
        room = db.query(Rooms).filter(Rooms.room_number == technician_request_data.get('room_number')).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Staff not found")
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        if status.lower() not in ["created", "assigned"]:
            raise HTTPException(status_code=400, detail="Invalid status. created, assigned are only allowed.")
        
        if staff.role == "technician":

            conflicting_technical_request = (
                db.query(TechnicianRequests)
                .filter(
                    TechnicianRequests.room_number == technician_request_data["room_number"],
                    TechnicianRequests.started_at < technician_request_data["finished_at"],
                    TechnicianRequests.finished_at > technician_request_data["started_at"]
                )
                .first()
            )

            if conflicting_technical_request:
                raise HTTPException(status_code=409, detail="The room is already assigned to another technician during the requested time range")

            conflicting_staff_request = (
                db.query(TechnicianRequests)
                .filter(
                    TechnicianRequests.assigned_to == technician_request_data["assigned_to"],
                    TechnicianRequests.started_at < technician_request_data["finished_at"],
                    TechnicianRequests.finished_at > technician_request_data["started_at"]
                )
                .first()
            )
           
            if conflicting_staff_request:
                raise HTTPException(status_code=409, detail="The staff is already assigned to technician room during the requested time range")
            
            if staff.status == "on leave":
                raise HTTPException(status_code=400, detail="This technician is on leave.")

            technician_request = TechnicianRequests(**technician_request_data)
            db.add(technician_request)
            db.commit()
            db.refresh(technician_request)
        else:
            raise HTTPException(status_code=403, detail="Assign to a technician.")
    
    elif len(user) == 1:

        technician_request_data = {
        "order_number": str(uuid.uuid4()),
        "created_by": str(user[0]),
        "room_number": room_number.upper(),
        "started_at": parse(started_at),
        "finished_at": parse(finished_at),
        "assigned_to": assigned_to.upper(),
        "defect_type": defect_type,
        "status": status.lower()
        }

        # For Guests
        guest = db.query(Guests).filter(Guests.id == user[0]).first()
        if not guest:
            raise HTTPException(status_code=404, detail="Guest not found")
        
        found_technician_request = (
            db.query(TechnicianRequests)
            .filter_by(
                room_number=technician_request_data.get("room_number"),
                defect_type = technician_request_data.get("defect_type")
            ).first()
        )

        if found_technician_request:
            raise HTTPException(status_code=403, detail="You have already created a technician request for this room.")
       
        if guest.room_number.upper() != room_number.upper():
            raise HTTPException(status_code=403, detail="Permission Denied. You can only create technician request for your own room.")
        
        if guest.checkout_date < datetime.now():
            raise HTTPException(status_code=403, detail="You have already checked out. Cannot create technician request.")
        
        if status.lower() not in ["created"]:
            raise HTTPException(status_code=400, detail="Invalid status. created is only allowed.")
        
        technician_request = TechnicianRequests(**technician_request_data)
        db.add(technician_request)
        db.commit()
        db.refresh(technician_request)
        
    else:
        raise HTTPException(status_code=403, detail="Permission Denied. Technician request can only be created by staffs with role 'Supervisor' and 'Guest'.")
    
    return {"message": f"Technician request created successfully"}

@router.post("/workorders/{user_id}/amenity_requests")
def create_amenity_requests(
    user: str = Depends(get_current_user),
    room_number: str = Form(...),
    amenity_type: str = Form(...),
    quantity: int= Form(...),
    db: Session = Depends(get_db)
) -> Any:
    if len(user) == 1:
        # For Guests only
        guest = db.query(Guests).filter(Guests.id == user[0]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if guest.room_number.upper() != room_number.upper():
            raise HTTPException(status_code=403, detail="Permission Denied. You can only create amenity request for your own room.")
        
        if guest.checkout_date > datetime.now():
            amenity_request_data = {
                "order_number": str(uuid.uuid4()),
                "created_by": int(user[0]),
                "room_number": room_number,
                "amenity_type": amenity_type,
                "quantity": quantity,
            }
            amenity_request = AmenityRequests(**amenity_request_data)
            db.add(amenity_request)
            db.commit()
            db.refresh(amenity_request)
        else:
            raise HTTPException(status_code=403, detail="You have already checked out. Cannot create amenity request.")

    else:
        raise HTTPException(status_code=403, detail="Amenity request can only be created by guests.")
    return {"message": f"Amenity request created successfully"}

@router.put("/workorders/{user_id}/cleaning_requests")
async def update_cleaning_request(
    user: str = Depends(get_current_user),
    order_number: str = Form(...),
    status: str = Form(...),
    db: Session = Depends(get_db)
) -> Any:
    # Check user role and permission
    if len(user) == 2 and user[1] == 'maid supervisor':
        cleaning_request = db.query(CleaningRequests).filter(CleaningRequests.order_number == order_number).first()
        if not cleaning_request:
            raise HTTPException(status_code=404, detail="Cleaning request not found")
        
        if status.lower() not in ["assigned, in progress", "done", "cancelled"]:
            raise HTTPException(status_code=400, detail="Invalid status. assigned, in progress, done, cancelled are only allowed.")
        
        staff = db.query(Staffs).filter(Staffs.staff_id == cleaning_request.assigned_to.upper()).first()

        if status == "in progress":
            staff.status = "not available"
        elif status == "done" or status == "cancelled":
            staff.status = "available"
        
        cleaning_request.status = status
        db.commit()
        db.refresh(cleaning_request)
        db.commit()
        db.refresh(staff)

    elif len(user) == 1:
        # For Guests
        cleaning_request = db.query(CleaningRequests).filter(CleaningRequests.order_number == order_number).first()
        if not cleaning_request:
            raise HTTPException(status_code=404, detail="Cleaning request not found")
        
        if status == "cancelled":
            staff = db.query(Staffs).filter(Staffs.staff_id == cleaning_request.assigned_to.upper()).first()
            staff.status = "available"
            cleaning_request.status = status
            db.commit()
            db.refresh(cleaning_request)
            db.commit()
            db.refresh(staff)
        else:
            raise HTTPException(status_code=403, detail="Invalid status. cancelled is only allowed")

    else:
        raise HTTPException(status_code=403, detail="Permission denied: Cleaning request can only be created by staffs with role 'Maid Supervisor'")

    return {"message": "Cleaning request updated successfully"}

@router.put("/workorders/{user_id}/maid_requests")
async def update_maid_request(
    user: str = Depends(get_current_user),
    order_number: str = Form(...),
    status: str = Form(...),
    db: Session = Depends(get_db)
) -> Any:
    # Check user role and permission
    if len(user) == 2 and user[1] == 'maid supervisor':
        maid_request = db.query(MaidRequests).filter(MaidRequests.order_number == order_number).first()
        if not maid_request:
            raise HTTPException(status_code=404, detail="Maid request not found")
        if status.lower() not in ["assigned, in progress", "done", "cancelled"]:
            raise HTTPException(status_code=400, detail="Invalid status. assigned, in progress, done, cancelled are only allowed.")
        
        if status == "in progress" or status == "done" or status == "cancelled":
            staff = db.query(Staffs).filter(Staffs.staff_id == maid_request.assigned_to.upper()).first()
            
            if status == "in progress":
                staff.status = "not available"
            elif status == "done" or status == "cancelled":
                staff.status = "available"

            maid_request.status = status
            db.commit()
            db.refresh(maid_request)
            db.commit()
            db.refresh(staff)

    else:
        raise HTTPException(status_code=403, detail="Permission denied: Maid request can only be updated by staffs with role 'Maid Supervisor'")

    return {"message": "Maid request updated successfully"}

@router.put("/workorders/{user_id}/technician_requests")
async def update_technician_request(
   user: str = Depends(get_current_user),
    order_number: str = Form(...),
    started_at: str = Form(...),
    finished_at: str = Form(...),
    assigned_to: str = Form(...),
    status: str = Form(...),
    db: Session = Depends(get_db)
) -> Any:
    # Check user role and permission
    if len(user) == 2 and user[1] == 'supervisor':
        technician_request_data = {
        "order_number": str(uuid.uuid4()),
        "created_by": str(user[0]),
        "started_at": parse(started_at),
        "finished_at": parse(finished_at),
        "assigned_to": assigned_to.upper(),
        "status": status.lower()
        }
        technician_request = db.query(TechnicianRequests).filter(TechnicianRequests.order_number == order_number).first()
        if not technician_request:
            raise HTTPException(status_code=404, detail="Technician request not found")
        staff = db.query(Staffs).filter(Staffs.staff_id == assigned_to.upper()).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Staff not found")
        if status.lower() not in ["assigned, in progress", "done", "cancelled"]:
            raise HTTPException(status_code=400, detail="Invalid status. assigned, in progress, done, cancelled are only allowed.")
        
        if staff.role == "technician":
            conflicting_technical_request = (
                db.query(TechnicianRequests)
                .filter(
                    TechnicianRequests.room_number == technician_request.room_number,
                    TechnicianRequests.started_at < technician_request_data["finished_at"],
                    TechnicianRequests.finished_at > technician_request_data["started_at"]
                )
                .first()
            )

            if conflicting_technical_request:
                raise HTTPException(status_code=409, detail="The room is already assigned to another technician during the requested time range")

            conflicting_staff_request = (
                db.query(TechnicianRequests)
                .filter(
                    TechnicianRequests.assigned_to == technician_request_data["assigned_to"],
                    TechnicianRequests.started_at < technician_request_data["finished_at"],
                    TechnicianRequests.finished_at > technician_request_data["started_at"]
                )
                .first()
            )
           
            if conflicting_staff_request:
                raise HTTPException(status_code=409, detail="The staff is already assigned to technician room during the requested time range")
            
            if staff.status == "on leave":
                raise HTTPException(status_code=400, detail="This technician is on leave.")
            
            technician_request.status = status
            technician_request.started_at = parse(started_at)
            technician_request.finished_at = parse(finished_at)
            technician_request.assigned_to = assigned_to.upper()
            db.commit()
            db.refresh(technician_request)
            db.commit()
            db.refresh(staff)

    else:
        raise HTTPException(status_code=403, detail="Permission denied: Technician request can only be updated by staffs with role 'Supervisor'")

    return {"message": "Technician request updated successfully"}