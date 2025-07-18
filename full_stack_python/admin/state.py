# full_stack_python/admin/state.py (CORREGIDO Y DEFINITIVO)

import reflex as rx
from typing import List
from ..auth.state import SessionState
from ..models import PurchaseModel, PurchaseStatus, UserInfo, PurchaseItemModel
import sqlalchemy
from sqlmodel import select

class AdminConfirmState(SessionState):
    pending_purchases: List[PurchaseModel] = []

    def load_pending_purchases(self):
        with rx.session() as session:
            # --- ✨ CORRECCIÓN: Se restaura la consulta completa con carga explícita (eager loading) ---
            self.pending_purchases = session.exec(
                select(PurchaseModel)
                .options(
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)
                )
                .where(PurchaseModel.status == PurchaseStatus.PENDING)
                .order_by(PurchaseModel.purchase_date.asc())
            ).unique().all() # Se usa .unique().all() para manejar correctamente los datos anidados

    @rx.event
    def confirm_payment(self, purchase_id: int):
        with rx.session() as session:
            purchase = session.get(PurchaseModel, purchase_id)
            if purchase:
                purchase.status = PurchaseStatus.CONFIRMED
                session.add(purchase)
                session.commit()
        return self.load_pending_purchases