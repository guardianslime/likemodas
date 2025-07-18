# full_stack_python/admin/state.py (SOLUCIÓN FINAL)

import reflex as rx
from typing import List
from ..auth.state import SessionState
from ..models import PurchaseModel, PurchaseStatus, UserInfo, PurchaseItemModel
import sqlalchemy
from sqlmodel import select

# --- ✨ NUEVO: Modelo de datos para la vista ---
# Esta clase le dice a Reflex exactamente qué datos y tipos se envían al frontend.
class PurchaseDisplay(rx.Base):
    id: int
    purchase_date_formatted: str
    total_price: float
    username: str
    email: str
    items_formatted: List[str]


class AdminConfirmState(SessionState):
    # --- CAMBIO: El estado ahora usará nuestro nuevo modelo de datos ---
    pending_purchases: List[PurchaseDisplay] = []

    def load_pending_purchases(self):
        with rx.session() as session:
            results = session.exec(
                select(PurchaseModel)
                .options(
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user)
                )
                .where(PurchaseModel.status == PurchaseStatus.PENDING)
                .order_by(PurchaseModel.purchase_date.asc())
            ).unique().all()

            # --- LÓGICA CLAVE: Convertimos los objetos de BD a nuestro modelo de vista ---
            purchases_to_display = []
            for p in results:
                purchases_to_display.append(
                    PurchaseDisplay(
                        id=p.id,
                        purchase_date_formatted=p.purchase_date_formatted,
                        total_price=p.total_price,
                        username=p.userinfo.user.username if p.userinfo and p.userinfo.user else "N/A",
                        email=p.userinfo.email if p.userinfo else "N/A",
                        items_formatted=p.items_formatted,
                    )
                )
            
            self.pending_purchases = purchases_to_display

    @rx.event
    def confirm_payment(self, purchase_id: int):
        with rx.session() as session:
            purchase = session.get(PurchaseModel, purchase_id)
            if purchase:
                purchase.status = PurchaseStatus.CONFIRMED
                session.add(purchase)
                session.commit()
        return self.load_pending_purchases