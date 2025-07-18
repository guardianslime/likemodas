# full_stack_python/admin/state.py (CORREGIDO)

import reflex as rx
from typing import List
from ..auth.state import SessionState
from ..models import PurchaseModel, PurchaseStatus, UserInfo, PurchaseItemModel
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

    # --- ✨ CORRECCIÓN CLAVE: Se reemplaza @rx.background por @rx.event ---
    # El decorador @rx.background no es válido. @rx.event es el correcto para
    # un método que se va a ejecutar al cargar la página (on_load).
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
            self.pending_purchases = session.exec(statement).all()

    @rx.event
    def confirm_payment(self, purchase_id: int):
        """
        Confirma un pago, actualiza su estado y fecha de confirmación.
        """
        with rx.session() as session:
            purchase = session.get(PurchaseModel, purchase_id)
            if purchase and purchase.status == PurchaseStatus.PENDING:
                purchase.status = PurchaseStatus.CONFIRMED
                purchase.confirmed_at = datetime.utcnow()
                session.add(purchase)
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