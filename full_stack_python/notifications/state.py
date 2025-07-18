# full_stack_python/notifications/state.py (CÓDIGO REEMPLAZADO)

import reflex as rx
from typing import List
from ..auth.state import SessionState
from ..models import NotificationModel
from sqlmodel import select, col

class NotificationState(SessionState):
    """Gestiona las notificaciones del usuario."""
    
    notifications: List[NotificationModel] = []
    
    @rx.var
    def unread_count(self) -> int:
        """Cuenta solo las notificaciones no leídas."""
        return sum(1 for n in self.notifications if not n.is_read)

    @rx.event
    def load_notifications(self):
        """Carga las notificaciones del usuario desde la base de datos."""
        if not self.is_authenticated or not self.authenticated_user_info:
            self.notifications = []
            return
        
        with rx.session() as session:
            self.notifications = session.exec(
                select(NotificationModel)
                .where(NotificationModel.userinfo_id == self.authenticated_user_info.id)
                .order_by(col(NotificationModel.created_at).desc())
            ).all()

    @rx.event
    def mark_all_as_read(self):
        """Marca todas las notificaciones como leídas al abrir el menú."""
        if not self.is_authenticated or not self.authenticated_user_info:
            return

        # IDs de las notificaciones no leídas
        unread_ids = [n.id for n in self.notifications if not n.is_read]
        if not unread_ids:
            return # No hacer nada si no hay nada que marcar

        # Actualiza el estado local para que la UI reaccione al instante
        for notification in self.notifications:
            if not notification.is_read:
                notification.is_read = True
        
        # Actualiza la base de datos en segundo plano
        with rx.session() as session:
            statement = (
                rx.update(NotificationModel)
                .where(NotificationModel.id.in_(unread_ids))
                .values(is_read=True)
            )
            session.exec(statement)
            session.commit()