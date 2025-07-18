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
            # --- ✨ CORRECCIÓN: Se usa una consulta simple para obtener las compras ---
            purchases = session.exec(
                select(PurchaseModel)
                .where(PurchaseModel.status == PurchaseStatus.PENDING)
                .order_by(PurchaseModel.purchase_date.asc())
            ).all()

            # --- ✨ Se "despiertan" los datos anidados para asegurar que se carguen ---
            # Esto evita errores en el frontend al forzar la carga de datos aquí.
            for p in purchases:
                _ = p.userinfo.user.username
                _ = p.items_formatted

            self.pending_purchases = purchases

    @rx.event
    def confirm_payment(self, purchase_id: int):
        with rx.session() as session:
            purchase = session.get(PurchaseModel, purchase_id)
            if purchase:
                purchase.status = PurchaseStatus.CONFIRMED
                session.add(purchase)
                session.commit()
        return self.load_pending_purchases