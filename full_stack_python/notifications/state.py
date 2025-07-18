# full_stack_python/notifications/state.py (ARCHIVO NUEVO)

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
        """Cuenta el número de notificaciones no leídas."""
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
        """Marca todas las notificaciones como leídas."""
        if not self.is_authenticated or not self.authenticated_user_info:
            return

        with rx.session() as session:
            # Actualiza el estado local
            for notification in self.notifications:
                if not notification.is_read:
                    notification.is_read = True
            
            # Actualiza la base de datos
            statement = (
                rx.update(NotificationModel)
                .where(
                    NotificationModel.userinfo_id == self.authenticated_user_info.id,
                    NotificationModel.is_read == False
                )
                .values(is_read=True)
            )
            session.exec(statement)
            session.commit()