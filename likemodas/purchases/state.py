# likemodas/purchases/state.py (VERSIÓN FINAL Y CORREGIDA)

import reflex as rx
from typing import List
from ..auth.state import SessionState
from ..models import PurchaseModel, UserInfo, PurchaseItemModel, BlogPostModel
from sqlmodel import select
import sqlalchemy

class PurchaseHistoryState(SessionState):
    purchases: List[PurchaseModel] = []

    search_query: str = ""

    @rx.var
    def filtered_purchases(self) -> list[PurchaseModel]:
        """Filtra las compras del usuario por ID o contenido."""
        if not self.search_query.strip():
            return self.purchases
            
        query = self.search_query.lower()
        results = []
        for p in self.purchases:
            # Buscamos en el ID y en los nombres de los artículos
            items_text = " ".join(p.items_formatted).lower()
            if query in f"#{p.id}" or query in items_text:
                results.append(p)
        return results

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