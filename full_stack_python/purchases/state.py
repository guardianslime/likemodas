# full_stack_python/purchases/state.py (CORREGIDO Y COMPLETO)

import reflex as rx
from typing import List
from ..auth.state import SessionState
from ..models import PurchaseModel, UserInfo, PurchaseItemModel
from sqlmodel import select
import sqlalchemy

class PurchaseHistoryState(SessionState):
    purchases: List[PurchaseModel] = []

    def load_purchases(self):
        if not self.is_authenticated:
            self.purchases = []
            return

        with rx.session() as session:
            # --- ✨ CORRECCIÓN: Se simplifica la consulta eliminando .options() ---
            # Ya no se necesita .unique() porque la consulta es simple.
            self.purchases = session.exec(
                select(PurchaseModel)
                .where(PurchaseModel.userinfo_id == self.authenticated_user_info.id)
                .order_by(PurchaseModel.purchase_date.desc())
            ).all()