# full_stack_python/admin/state.py
import reflex as rx
from typing import List
from ..auth.state import SessionState
from ..models import PurchaseModel, PurchaseStatus, UserInfo
import sqlalchemy


class AdminConfirmState(SessionState):
    pending_purchases: List[PurchaseModel] = []

    def load_pending_purchases(self):
        with rx.session() as session:
            self.pending_purchases = session.exec(
                rx.select(PurchaseModel)
                .options(
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)
                )
                .where(PurchaseModel.status == PurchaseStatus.PENDING)
                .order_by(PurchaseModel.purchase_date.asc())
            ).all()

    @rx.event
    def confirm_payment(self, purchase_id: int):
        with rx.session() as session:
            purchase = session.get(PurchaseModel, purchase_id)
            if purchase:
                purchase.status = PurchaseStatus.CONFIRMED
                session.add(purchase)
                session.commit()
        # Recargamos la lista para que la compra confirmada desaparezca
        return self.load_pending_purchases