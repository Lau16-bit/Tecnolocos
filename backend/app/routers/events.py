from fastapi import APIRouter, Depends, HTTPException
from app.services import event_service

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/")
def list_events_public():
    return event_service.list_events()

@router.get("/{event_id}")
def get_event(event_id: str):
    return event_service.get_event_by_id(event_id)

@router.post("/")
def create_event(event_data):
    return event_service.create_event(event_data)

@router.patch("/{event_id}/publish")
def publish_event(event_id: str):
    return event_service.publish_event(event_id)
