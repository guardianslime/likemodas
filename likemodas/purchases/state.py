# likemodas/purchases/state.py (CORREGIDO Y COMPLETO)

import reflex as rx
from typing import List
from ..auth.state import SessionState
from ..models import PurchaseModel, UserInfo, PurchaseItemModel
from sqlmodel import select
import sqlalchemy

class PurchaseHistoryState(SessionState):
    purchases: List[PurchaseModel] = []

    def load_purchases(self):
        # Se añade una comprobación para asegurar que el usuario está logueado
        if not self.is_authenticated or not self.authenticated_user_info:
            self.purchases = []
            return

        with rx.session() as session:
            statement = (
                select(PurchaseModel)
                .options(
                    # Esta consulta necesita cargar los items para poder mostrarlos
                    sqlalchemy.orm.joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)
                )
                .where(PurchaseModel.userinfo_id == self.authenticated_user_info.id)
                .order_by(PurchaseModel.purchase_date.desc())
            )
            # --- ✨ CORRECCIÓN CLAVE: Añadir .unique() aquí también ---
            self.purchases = session.exec(statement).unique().all()