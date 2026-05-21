from app.models.event import Event
from app.core.database import SessionLocal

def create_event(event_data):
    # Validaciones de fechas, cupos, etc.
    pass

def publish_event(event_id):
    # Cambiar estado de borrador a publicado
    pass

def cancel_event(event_id):
    # Cambiar estado a cancelado
    pass

def list_events(filters, page=1, size=20):
    # Listado con paginación y filtros
    pass
