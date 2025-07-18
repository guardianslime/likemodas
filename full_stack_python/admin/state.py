# full_stack_python/admin/state.py (SOLUCIÓN DEFINITIVA)

import reflex as rx
from typing import List, Dict
from ..auth.state import SessionState
from ..models import PurchaseModel, PurchaseStatus, UserInfo, PurchaseItemModel
import sqlalchemy
from sqlmodel import select

class AdminConfirmState(SessionState):
    # --- CAMBIO: El estado ahora guardará una lista de diccionarios ---
    pending_purchases: List[Dict] = []

    def load_pending_purchases(self):
        with rx.session() as session:
            # Primero, obtenemos los datos de la forma más robusta posible
            results = session.exec(
                select(PurchaseModel)
                .options(
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user)
                )
                .where(PurchaseModel.status == PurchaseStatus.PENDING)
                .order_by(PurchaseModel.purchase_date.asc())
            ).unique().all()

            # --- ✨ LÓGICA CLAVE: Convertimos los objetos en diccionarios simples ---
            # Esto evita cualquier error de serialización.
            purchases_as_dicts = []
            for p in results:
                purchases_as_dicts.append({
                    "id": p.id,
                    "purchase_date_formatted": p.purchase_date_formatted,
                    "total_price": p.total_price,
                    "username": p.userinfo.user.username if p.userinfo and p.userinfo.user else "N/A",
                    "email": p.userinfo.email if p.userinfo else "N/A",
                    "items_formatted": p.items_formatted,
                })
            
            self.pending_purchases = purchases_as_dicts

    @rx.event
    def confirm_payment(self, purchase_id: int):
        with rx.session() as session:
            purchase = session.get(PurchaseModel, purchase_id)
            if purchase:
                purchase.status = PurchaseStatus.CONFIRMED
                session.add(purchase)
                session.commit()
        # Volvemos a cargar y procesar los datos
        return self.load_pending_purchases