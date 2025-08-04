# likemodas/purchases/state.py

import reflex as rx
from typing import List
from sqlmodel import select
import sqlalchemy

# Se importa el estado BASE
from ..auth.state import SessionState
from ..models import PurchaseModel, UserInfo, PurchaseItemModel, BlogPostModel

class PurchaseHistoryCardData(rx.Base):
    id: int
    purchase_date_formatted: str
    status: str
    total_price_cop: str
    shipping_name: str
    shipping_address: str
    shipping_neighborhood: str
    shipping_city: str
    shipping_phone: str
    items_formatted: list[str]

# La clase ahora hereda de SessionState
class PurchaseHistoryState(SessionState):
    purchases: List[PurchaseHistoryCardData] = rx.Field(default_factory=list)
    search_query: str = ""

    @rx.var
    def filtered_purchases(self) -> list[PurchaseHistoryCardData]:
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
        """Carga el historial y lo convierte a un formato seguro para la UI."""
        if not self.is_authenticated or not self.authenticated_user_info:
            self.purchases = []
            return

        with rx.session() as session:
            statement = (
                select(PurchaseModel)
                .options(
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(PurchaseModel.items)
                    .joinedload(PurchaseItemModel.blog_post)
                )
                .where(PurchaseModel.userinfo_id == self.authenticated_user_info.id)
                .order_by(PurchaseModel.purchase_date.desc())
            )
            db_results = session.exec(statement).unique().all()

            self.purchases = [
                PurchaseHistoryCardData(
                    id=p.id,
                    purchase_date_formatted=p.purchase_date_formatted,
                    status=p.status.value,
                    total_price_cop=p.total_price_cop,
                    shipping_name=p.shipping_name or "",
                    shipping_address=p.shipping_address or "",
                    shipping_neighborhood=p.shipping_neighborhood or "",
                    shipping_city=p.shipping_city or "",
                    shipping_phone=p.shipping_phone or "",
                    items_formatted=p.items_formatted,
                )
                for p in db_results
            ]