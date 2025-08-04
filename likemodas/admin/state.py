# likemodas/admin/state.py

import reflex as rx
from typing import List
import sqlalchemy
from sqlmodel import select
from datetime import datetime

# Se importa el estado unificado
from likemodas.auth.state import SessionState
from likemodas.state import AppState
from likemodas.utils.formatting import format_to_cop
from ..models import PurchaseModel, UserInfo, PurchaseItemModel, NotificationModel, PurchaseStatus

class PurchaseCardData(rx.Base):
    id: int
    customer_name: str
    customer_email: str
    purchase_date_formatted: str
    status: str
    total_price: float
    shipping_name: str
    shipping_full_address: str
    shipping_phone: str
    items_formatted: list[str]

    @property
    def total_price_cop(self) -> str:
        return format_to_cop(self.total_price)
    
class AdminConfirmState(AppState):
    # ✅ Inicialización segura de la lista
    pending_purchases: List[PurchaseCardData] = rx.Field(default_factory=list)

    @rx.event
    def load_pending_purchases(self):
        if not self.is_admin: 
            self.pending_purchases = []
            return
        with rx.session() as session:
            db_results = session.exec(
                select(PurchaseModel).options(
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)
                ).where(PurchaseModel.status == PurchaseStatus.PENDING).order_by(PurchaseModel.purchase_date.asc())
            ).unique().all()
            
            self.pending_purchases = [
                PurchaseCardData(
                    id=p.id,
                    customer_name=p.userinfo.user.username if p.userinfo and p.userinfo.user else "Usuario no disponible",
                    customer_email=p.userinfo.email if p.userinfo else "N/A",
                    purchase_date_formatted=p.purchase_date_formatted, status=p.status.value, total_price=p.total_price,
                    shipping_name=p.shipping_name or "",
                    shipping_full_address=f"{p.shipping_address or ''}, {p.shipping_neighborhood or ''}, {p.shipping_city or ''}",
                    shipping_phone=p.shipping_phone or "", items_formatted=p.items_formatted
                ) for p in db_results
            ]
            yield SessionState.set_new_purchase_notification(len(self.pending_purchases) > 0)

    @rx.event
    def confirm_payment(self, purchase_id: int):
        if not self.is_admin: return
        with rx.session() as session:
            purchase = session.get(PurchaseModel, purchase_id)
            if purchase:
                purchase.status = PurchaseStatus.CONFIRMED
                purchase.confirmed_at = datetime.utcnow()
                notification = NotificationModel(userinfo_id=purchase.userinfo_id, message=f"¡Tu compra #{purchase.id} ha sido confirmada!", url="/my-purchases")
                session.add(purchase); session.add(notification); session.commit()
                yield rx.toast.success(f"Compra #{purchase_id} confirmada.")
                yield AdminConfirmState.load_pending_purchases

    @classmethod
    def notify_admin_of_new_purchase(cls):
        return SessionState.set_new_purchase_notification(True)

class PaymentHistoryState(AppState):
    # ✅ Inicialización segura de la lista
    all_purchases: List[PurchaseCardData] = rx.Field(default_factory=list)
    search_query: str = ""

    @rx.var
    def filtered_purchases(self) -> list[PurchaseCardData]:
        if not self.search_query.strip(): return self.all_purchases
        query = self.search_query.lower()
        return [p for p in self.all_purchases if query in f"#{p.id}" or query in p.customer_name.lower() or query in p.customer_email.lower()]

    @rx.event
    def load_confirmed_purchases(self):
        if not self.is_admin: self.all_purchases = []; return
        with rx.session() as session:
            db_results = session.exec(
                select(PurchaseModel).options(
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)
                ).where(PurchaseModel.status != PurchaseStatus.PENDING).order_by(PurchaseModel.purchase_date.desc())
            ).unique().all()
            
            self.all_purchases = [
                PurchaseCardData(
                    id=p.id,
                    customer_name=p.userinfo.user.username if p.userinfo and p.userinfo.user else "Usuario no disponible",
                    customer_email=p.userinfo.email if p.userinfo else "N/A",
                    purchase_date_formatted=p.purchase_date_formatted, status=p.status.value, total_price=p.total_price,
                    shipping_name=p.shipping_name or "",
                    shipping_full_address=f"{p.shipping_address or ''}, {p.shipping_neighborhood or ''}, {p.shipping_city or ''}",
                    shipping_phone=p.shipping_phone or "", items_formatted=p.items_formatted
                ) for p in db_results
            ]