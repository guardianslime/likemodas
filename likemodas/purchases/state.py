# likemodas/purchases/state.py (VERSIÓN ESTRUCTURALMENTE CORREGIDA)

import reflex as rx
from typing import List
from ..auth.state import SessionState
from ..models import PurchaseModel, UserInfo, PurchaseItemModel, BlogPostModel
from sqlmodel import select
import sqlalchemy

# --- ✨ 1. CREAR UN MODELO DE DATOS SIMPLE PARA LA UI ---
# Este objeto solo contiene los datos que la vista necesita, en formatos simples.
class PurchaseHistoryCardData(rx.Base):
    id: int
    purchase_date_formatted: str
    status: str
    total_price_cop: str
    shipping_name: str
    shipping_full_address: str
    shipping_phone: str
    items_formatted: list[str]

class PurchaseHistoryState(SessionState):
    # --- ✨ 2. CAMBIAR EL TIPO DE LA LISTA DE COMPRAS ---
    purchases: List[PurchaseHistoryCardData] = []
    search_query: str = ""

    @rx.var
    def filtered_purchases(self) -> list[PurchaseHistoryCardData]:
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
            # La consulta a la base de datos sigue siendo la misma y es correcta
            statement = (
                select(PurchaseModel)
                .options(
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(PurchaseModel.items)
                    .joinedload(PurchaseItemModel.blog_post)
                    .joinedload(BlogPostModel.comments)
                )
                .where(PurchaseModel.userinfo_id == self.authenticated_user_info.id)
                .order_by(PurchaseModel.purchase_date.desc())
            )
            db_results = session.exec(statement).unique().all()

            # --- ✨ 3. CONVERTIR LOS RESULTADOS DE LA DB AL DTO SEGURO ---
            # Este es el paso crucial que previene el error de serialización.
            self.purchases = [
                PurchaseHistoryCardData(
                    id=p.id,
                    purchase_date_formatted=p.purchase_date_formatted,
                    status=p.status.value,  # Usamos .value para obtener el string del enum
                    total_price_cop=p.total_price_cop,
                    shipping_name=p.shipping_name or "",
                    shipping_full_address=f"{p.shipping_address}, {p.shipping_neighborhood}, {p.shipping_city}",
                    shipping_phone=p.shipping_phone or "",
                    items_formatted=p.items_formatted, # La propiedad del modelo ya devuelve una lista segura
                )
                for p in db_results
            ]