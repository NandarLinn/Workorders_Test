import csv
import sys
from db import SessionLocal
from models import Rooms, Staffs

csv_header_to_column_mapping = {
    "room_number": "room_number",
    "room_type": "room_type",
    "room_status": "room_status",
    "staff_id": "staff_id",
    "staff_name": "staff_name",
    "role": "role",
    "status": "status"
}

def read_rooms_and_staffs(path: str):
    db = SessionLocal()
    mapper = lambda x: {csv_header_to_column_mapping.get(k): v for k, v in x.items()}
    with open(path) as rooms_and_staffs_data:
        reader = csv.DictReader(rooms_and_staffs_data)
        for row in reader:
            current_row = mapper(row)

            room_data = {
                "room_number": current_row["room_number"].upper(),
                "room_type": current_row["room_type"].lower(),
                "room_status": current_row["room_status"].lower(),
    
            }

            room = Rooms(**room_data)
            found_room = (
                db.query(Rooms)
                .filter_by(
                    room_number=room_data.get("room_number"),
                )
                .first()
            )

            if not found_room:
                db.add(room)
                db.commit()
                db.refresh(room)

            staff_data = {
                "staff_id": current_row["staff_id"].upper(),
                "staff_name": current_row["staff_name"].title(),
                "role": current_row["role"].lower(),
                "status": current_row["status"].lower(),
            }
            
            staff = Staffs(**staff_data)
            if staff_data.get("staff_id")!='':
                found_staff = (
                    db.query(Staffs)
                    .filter_by(staff_id=staff_data.get("staff_id"),
                    )
                    .first()
                )
                if not found_staff:
                    db.add(staff)
                    db.commit()
                    db.refresh(staff)

if __name__ == "__main__":
    # how to import data
    # cd /Users/linnaein/Projects/Testwork
    # source ../testwork_env/bin/activate
    # python -m seeds.importer_rooms_and_staffs ~/Downloads/rooms_and_staffs\ -\ Sheet1.csv
    read_rooms_and_staffs(sys.argv[1])
