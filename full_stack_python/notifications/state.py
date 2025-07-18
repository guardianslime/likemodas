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
        """
        Marca las notificaciones como leídas, fuerza la actualización de la UI
        y luego recarga los datos.
        """
        if not self.is_authenticated or not self.authenticated_user_info:
            return

        unread_ids = [n.id for n in self.notifications if not n.is_read]
        if not unread_ids:
            return

        # 1. Actualiza la base de datos como antes
        with rx.session() as session:
            statement = (
                rx.update(NotificationModel)
                .where(NotificationModel.id.in_(unread_ids))
                .values(is_read=True)
            )
            session.exec(statement)
            session.commit()

        # --- ✨ CORRECCIÓN CLAVE Y DEFINITIVA ---
        # 2. Forzamos la actualización de la UI vaciando la lista localmente.
        #    El `yield` envía este cambio al frontend de inmediato.
        self.notifications = []
        yield

        # 3. Volvemos a llenar la lista con los datos actualizados (ya leídos)
        #    para que sigan apareciendo en el menú si el usuario lo vuelve a abrir.
        yield self.load_notifications()