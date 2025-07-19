# likemodas/admin/state.py (CORREGIDO)

import reflex as rx
from typing import List
from ..auth.state import SessionState
from ..models import PurchaseModel, PurchaseStatus, UserInfo, PurchaseItemModel, NotificationModel
import sqlalchemy
from sqlmodel import select
from datetime import datetime


class AdminConfirmState(SessionState):
    """
    Estado para que el administrador vea y confirme los pagos pendientes.
    """
    pending_purchases: List[PurchaseModel] = []
    new_purchase_notification: bool = False

    @rx.var
    def has_pending_purchases(self) -> bool:
        """Verifica si hay compras pendientes."""
        return len(self.pending_purchases) > 0

    @rx.event
    def load_pending_purchases(self):
        """
        Carga las compras con estado 'PENDING' desde la base de datos.
        """
        if not self.is_admin:
            self.pending_purchases = []
            return

        with rx.session() as session:
            statement = (
                select(PurchaseModel)
                .options(
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)
                )
                .where(PurchaseModel.status == PurchaseStatus.PENDING)
                .order_by(PurchaseModel.purchase_date.asc())
            )
            # --- ✨ CORRECCIÓN CLAVE: Se añade .unique() ---
            # Esto consolida las filas duplicadas que resultan de cargar la colección de 'items'.
            self.pending_purchases = session.exec(statement).unique().all()

    @rx.event
    def confirm_payment(self, purchase_id: int):
        """
        Confirma un pago, actualiza su estado y crea una notificación para el usuario.
        """
        with rx.session() as session:
            purchase = session.get(PurchaseModel, purchase_id)
            if purchase and purchase.status == PurchaseStatus.PENDING:
                # Actualizar la compra
                purchase.status = PurchaseStatus.CONFIRMED
                purchase.confirmed_at = datetime.utcnow()
                session.add(purchase)

                # --- ✨ LÓGICA AÑADIDA PARA CREAR NOTIFICACIÓN ---
                notification = NotificationModel(
                    userinfo_id=purchase.userinfo_id,
                    message=f"🎉 ¡Tu pago de ${purchase.total_price:.2f} ha sido confirmado!",
                    url="/my-purchases" # Redirige al historial de compras
                )
                session.add(notification)
                # --- FIN DE LA LÓGICA AÑADIDA ---

                session.commit()
                
                yield rx.toast.success(f"Pago de {purchase.userinfo.email} confirmado.")
                yield self.load_pending_purchases
            else:
                yield rx.toast.error("La compra no se pudo confirmar o ya fue procesada.")
    @rx.event
    def notify_admin_of_new_purchase(self):
        """
        Activa una notificación visual para el admin.
        """
        self.new_purchase_notification = True
        yield rx.toast.info("¡Hay una nueva compra pendiente de aprobación!", duration=10000)

    @rx.event
    def clear_notification(self):
        """Limpia la notificación después de ser vista."""
        self.new_purchase_notification = False

class PaymentHistoryState(SessionState):
    """
    Estado para que el administrador vea el historial de pagos confirmados.
    """
    confirmed_purchases: List[PurchaseModel] = []

    @rx.var
    def has_confirmed_purchases(self) -> bool:
        """Verifica si hay compras en el historial."""
        return len(self.confirmed_purchases) > 0

    @rx.event
    def load_confirmed_purchases(self):
        # ...
        with rx.session() as session:
            statement = (
                select(PurchaseModel)
                .options(
                    # 👇 CORRECCIÓN: Se eliminó el "" de esta línea
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)
                )
                .where(PurchaseModel.status == PurchaseStatus.CONFIRMED)
                .order_by(PurchaseModel.confirmed_at.desc())
            )
            self.confirmed_purchases = session.exec(statement).unique().all()

