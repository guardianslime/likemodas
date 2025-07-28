# likemodas/purchases/state.py

import reflex as rx
from typing import List
from ..auth.state import SessionState
from ..models import PurchaseModel, UserInfo, PurchaseItemModel, BlogPostModel
from sqlmodel import select
import sqlalchemy

# --- ✅ SOLUCIÓN: Objeto de Datos Simple (DTO) para la UI de historial del usuario ---
class UserPurchaseData(rx.Base):
    id: int
    purchase_date_formatted: str
    status: str
    total_price: float
    shipping_name: str
    shipping_full_address: str
    shipping_phone: str
    items_formatted: list[str]

class PurchaseHistoryState(SessionState):
    # --- La variable de estado ahora usa el objeto simple ---
    purchases: List[UserPurchaseData] = []
    search_query: str = ""

    @rx.var
    def filtered_purchases(self) -> list[UserPurchaseData]:
        """Filtra las compras del usuario por ID o contenido."""
        if not self.search_query.strip():
            return self.purchases
            
        query = self.search_query.lower()
        results = []
        for p in self.purchases:
            items_text = " ".join(p.items_formatted).lower()
            if query in f"#{p.id}" or query in items_text:
                results.append(p)
        return results

    @rx.event
    def load_purchases(self):
        """Carga y transforma el historial de compras del usuario actual."""
        if not self.is_authenticated or not self.authenticated_user_info:
            self.purchases = []
            return

        with rx.session() as session:
            statement = (
                select(PurchaseModel)
                .options(
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)
                )
                .where(PurchaseModel.userinfo_id == self.authenticated_user_info.id)
                .order_by(PurchaseModel.purchase_date.desc())
            )
            db_results = session.exec(statement).unique().all()

            # --- Transformación de PurchaseModel a UserPurchaseData ---
            self.purchases = [
                UserPurchaseData(
                    id=p.id,
                    purchase_date_formatted=p.purchase_date_formatted,
                    status=p.status.value,
                    total_price=p.total_price,
                    shipping_name=p.shipping_name or "",
                    shipping_full_address=f"{p.shipping_address or ''}, {p.shipping_neighborhood or ''}, {p.shipping_city or ''}",
                    shipping_phone=p.shipping_phone or "",
                    items_formatted=p.items_formatted
                )
                for p in db_results
            ]