# import json
# from datetime import datetime
# import pytest
# from httpx import AsyncClient
# from .main import app
# from db import SessionLocal
# from models import TechnicianRequests, CleaningRequests, MaidRequests

# @pytest.fixture
# def client():
#     with AsyncClient(app=app, base_url="http://testserver") as client:
#         yield client

# def test_create_cleaning_request(client):
#     response = client.post(
#         "/workorders/{user_id}/cleaning_requests",
#         json={
#             "order_number": "6b2571fe-4600-11ee-931d-6c4008b8813a",
#             "created_by": "MDSP01",
#             "room_number": "A001",
#             "started_at": "2023-08-29T10:00:00",
#             "finished_at": "2023-08-29T12:00:00",
#             "assigned_to": "CLN001",
#             "status": "created"
#         }
#     )
#     assert response.status_code == 200
#     assert response.json() == {"message": "Cleaning request created successfully"}

# def test_create_maid_request(client):
#     response = client.post(
#         "/workorders/{user_id}/maid_requests",
#         json={
#             "order_number": "8523d21c-4600-11ee-931d-6c4008b8813a",
#             "created_by": "MDSP01",
#             "assigned_to": "MD001",
#             "room_number": "A002",
#             "started_at": "2023-08-29T10:00:00",
#             "finished_at": "2023-08-29T12:00:00",
#             "description": "Clean the room",
#             "status": "created"
#         }
#     )
#     assert response.status_code == 200
#     assert response.json() == {"message": "Maid request created successfully"}

# def test_create_technician_request(client):
#     response = client.post(
#         "/workorders/{user_id}/technician_requests",
#         json={
#             "order_number": "970a5ba4-4600-11ee-931d-6c4008b8813a",
#             "created_by": "SUP001",
#             "room_number": "A002",
#             "assigned_to": "TECH001",
#             "defect_type": "Plumbing",
#             "started_at": "2023-08-29T10:00:00",
#             "finished_at": "2023-08-29T12:00:00",
#             "status": "created"
#         }
#     )
#     assert response.status_code == 200
#     assert response.json() == {"message": "Technician request created successfully"}

#     def test_create_amenity_request(client):
#         response = client.post(
#             "/workorders/{user_id}/amenity_requests",
#             json={
#                 "order_number": "b1154824-4600-11ee-931d-6c4008b8813a",
#                 "created_by": 18,
#                 "room_number": "E004",
#                 "amenity_type": "Towel",
#                 "quantity": 2,
#             }
#     )
#     assert response.status_code == 200
#     assert response.json() == {"message": "Amenity request created successfully"}


# def test_update_cleaning_request(client):
#     # Create a sample technician request in the database
#     db = SessionLocal()
#     new_cleaning_request = CleaningRequests(
#         order_number="7872f764-45fb-11ee-a87c-6c4008b8813a",
#         created_by="MDSP01",
#         room_number="A003",
#         started_at=datetime(2023, 8, 29, 11, 0, 0),
#         finished_at=datetime(2023, 8, 29, 12, 0, 0),
#         assigned_to="CLN003",
#         status="created"
#     )
#     db.add(new_cleaning_request)
#     db.commit()

#     # Now update the technician request
#     response = client.put(
#         "/workorders/{user_id}/technician_requests",
#         json={
#             "order_number": "7872f764-45fb-11ee-a87c-6c4008b8813a",
#             "status": "in progress"
#         }
#     )
#     assert response.status_code == 200
#     assert response.json() == {"message": "Cleaning request updated successfully"}

# def test_update_maid_request(client):
#     # Create a sample technician request in the database
#     db = SessionLocal()
#     new_maid_request = MaidRequests(
#         order_number="d116e3ee-4600-11ee-931d-6c4008b8813a",
#         created_by="MDSP01",
#         room_number="A004",
#         started_at=datetime(2023, 8, 29, 11, 0, 0),
#         finished_at=datetime(2023, 8, 29, 12, 0, 0),
#         assigned_to="MD003",
#         status="created"
#     )
#     db.add(new_maid_request)
#     db.commit()

#     # Now update the technician request
#     response = client.put(
#         "/workorders/{user_id}/technician_requests",
#         json={
#             "order_number": "d116e3ee-4600-11ee-931d-6c4008b8813a",
#             "status": "assigned"
#         }
#     )
#     assert response.status_code == 200
#     assert response.json() == {"message": "Cleaning request updated successfully"}

# def test_update_technician(client):
#     # Create a sample technician request in the database

#     db = SessionLocal()
#     new_maid_request = TechnicianRequests(
#         order_number="e57701b6-4600-11ee-931d-6c4008b8813a",
#         created_by="SUP001",
#         room_number="A005",
#         started_at=datetime(2023, 8, 29, 11, 0, 0),
#         finished_at=datetime(2023, 8, 29, 12, 0, 0),
#         assigned_to="TECH005",
#         status="created"
#     )
#     db.add(new_maid_request)
#     db.commit()

#     # Now update the technician request
#     response = client.put(
#         "/workorders/{user_id}/technician_requests",
#         json={
#             "order_number": "e57701b6-4600-11ee-931d-6c4008b8813a",
#             "created_by": "SUP001",
#             "room_number": "A005",
#             "started_at": "2023-08-29T10:00:00",
#             "finished_at": "2023-08-29T12:00:00",
#             "assigned_to": "TECH005",
#             "status": "assigned"
#         }
#     )
#     assert response.status_code == 200
#     assert response.json() == {"message": "Cleaning request updated successfully"}


# def test_get_workorders_requests_guest(client):
#     response = client.get("/workorders/18/workorder_requests")
#     assert response.status_code == 403