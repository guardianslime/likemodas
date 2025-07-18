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

        unread_ids = [n.id for n in self.notifications if not n.is_read]
        if not unread_ids:
            return

        # --- ✨ CORRECCIÓN CLAVE AQUÍ ---
        # 1. Se crea una nueva lista actualizada para forzar el re-renderizado de la UI.
        updated_notifications = []
        for n in self.notifications:
            if not n.is_read:
                # Crea una copia del objeto con is_read=True
                n.is_read = True
            updated_notifications.append(n)
        
        # 2. Se reasigna la variable de estado, lo que garantiza que Reflex detecte el cambio.
        self.notifications = updated_notifications
        # --- FIN DE LA CORRECCIÓN ---
        
        # Actualiza la base de datos en segundo plano (esta parte estaba bien)
        with rx.session() as session:
            statement = (
                rx.update(NotificationModel)
                .where(NotificationModel.id.in_(unread_ids))
                .values(is_read=True)
            )
            session.exec(statement)
            session.commit()