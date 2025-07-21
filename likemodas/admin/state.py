# likemodas/admin/state.py (VERSIÓN FINAL Y CORREGIDA)

import reflex as rx
from typing import List
from ..auth.state import SessionState
from ..models import BlogPostModel, PurchaseModel, PurchaseStatus, UserInfo, PurchaseItemModel, NotificationModel
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
        # --- CORRECCIÓN: Se importa BlogPostModel aquí adentro ---
        from ..models import BlogPostModel
        
        if not self.is_admin:
            self.pending_purchases = []
            return

        with rx.session() as session:
            statement = (
                select(PurchaseModel)
                .options(
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(PurchaseModel.items)
                    .joinedload(PurchaseItemModel.blog_post)
                    .joinedload(BlogPostModel.comments)
                )
                .where(PurchaseModel.status == PurchaseStatus.PENDING)
                .order_by(PurchaseModel.purchase_date.asc())
            )
            self.pending_purchases = session.exec(statement).unique().all()

    @rx.event
    def confirm_payment(self, purchase_id: int):
        """
        Confirma un pago, actualiza su estado y crea una notificación para el usuario.
        """
        with rx.session() as session:
            purchase = session.get(PurchaseModel, purchase_id)
            if purchase and purchase.status == PurchaseStatus.PENDING:
                purchase.status = PurchaseStatus.CONFIRMED
                purchase.confirmed_at = datetime.utcnow()
                session.add(purchase)

                notification = NotificationModel(
                    userinfo_id=purchase.userinfo_id,
                    message=f"🎉 ¡Tu pago de ${purchase.total_price:.2f} ha sido confirmado!",
                    url="/my-purchases"
                )
                session.add(notification)
                session.commit()
                
                yield rx.toast.success(f"Pago de {purchase.userinfo.email} confirmado.")
                yield type(self).load_pending_purchases
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
        if not self.is_admin:
            self.confirmed_purchases = []
            return
        
        with rx.session() as session:
            # --- CORRECCIÓN CLAVE AQUÍ TAMBIÉN ---
            statement = (
                select(PurchaseModel)
                .options(
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(PurchaseModel.items)
                    .joinedload(PurchaseItemModel.blog_post)
                    .joinedload(BlogPostModel.comments)  # <--- ESTA LÍNEA ES LA SOLUCIÓN
                )
                .where(PurchaseModel.status == PurchaseStatus.CONFIRMED)
                .order_by(PurchaseModel.confirmed_at.desc())
            )
            self.confirmed_purchases = session.exec(statement).unique().all()