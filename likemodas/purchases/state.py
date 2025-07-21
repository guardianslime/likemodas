# likemodas/purchases/state.py (VERSIÓN FINAL Y CORREGIDA)

import reflex as rx
from typing import List
from ..auth.state import SessionState
from ..models import PurchaseModel, UserInfo, PurchaseItemModel, BlogPostModel
from sqlmodel import select
import sqlalchemy

class PurchaseHistoryState(SessionState):
    purchases: List[PurchaseModel] = []

    @rx.event
    def load_purchases(self):
        """Carga el historial de compras del usuario actual."""
        if not self.is_authenticated or not self.authenticated_user_info:
            self.purchases = []
            return

        with rx.session() as session:
            # --- CORRECCIÓN CLAVE AQUÍ ---
            # Se añade un `joinedload` explícito para los comentarios del post,
            # lo que previene el error `DetachedInstanceError` en esta página.
            statement = (
                select(PurchaseModel)
                .options(
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(PurchaseModel.items)
                    .joinedload(PurchaseItemModel.blog_post)
                    .joinedload(BlogPostModel.comments)  # <--- ESTA LÍNEA ES LA SOLUCIÓN
                )
                .where(PurchaseModel.userinfo_id == self.authenticated_user_info.id)
                .order_by(PurchaseModel.purchase_date.desc())
            )
            self.purchases = session.exec(statement).unique().all()