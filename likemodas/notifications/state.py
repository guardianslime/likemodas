import reflex as rx
from typing import List
from ..auth.state import SessionState
from ..models import NotificationModel
# --- ✨ 1. AÑADIR 'update' A LA IMPORTACIÓN ---
from sqlmodel import select, col, update

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
        """
        Actualiza la UI al instante para que el contador desaparezca y luego
        actualiza la base de datos en segundo plano.
        """
        if not self.is_authenticated or not self.authenticated_user_info:
            return

        unread_ids = [n.id for n in self.notifications if not n.is_read]
        if not unread_ids:
            return

        self.notifications = self.notifications.copy()
        for notification in self.notifications:
            notification.is_read = True
        
        with rx.session() as session:
            statement = (
                # --- ✨ 2. USAR 'update' EN LUGAR DE 'rx.update' ---
                update(NotificationModel)
                .where(NotificationModel.id.in_(unread_ids))
                .values(is_read=True)
            )
            session.exec(statement)
            session.commit()
