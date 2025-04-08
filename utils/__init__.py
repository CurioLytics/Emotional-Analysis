# Make utils a proper package and expose key functions
from .webhook import send_webhook_notification
from .database import get_supabase_client, execute_query

__all__ = [
    'send_webhook_notification',
    'get_supabase_client',
    'execute_query'
]
