# likemodas/state.py

import reflex as rx
import reflex_local_auth

from .auth.state import SessionState
from .cart.state import CartState
from .blog.state import BlogPostState, BlogAddFormState, BlogEditFormState, CommentState
from .purchases.state import PurchaseHistoryState
from .admin.state import AdminConfirmState, PaymentHistoryState
from .contact.state import ContactState
from .account.shipping_info_state import ShippingInfoState
from .ui.search_state import SearchState
from .notifications.state import NotificationState
# NavState ya no se importa aquí

class AppState(SessionState):
    """
    El estado raíz que contiene todos los sub-estados DE DATOS.
    Ya no hereda de NavState.
    """
    
    # NavState se elimina de los sub-estados.
    cart: CartState
    blog_posts: BlogPostState
    blog_add_form: BlogAddFormState
    blog_edit_form: BlogEditFormState
    comments: CommentState
    shipping_info: ShippingInfoState
    purchase_history: PurchaseHistoryState
    admin_confirm: AdminConfirmState
    payment_history: PaymentHistoryState
    contact: ContactState
    search: SearchState
    notifications: NotificationState

    def on_load(self):
        if not self.is_authenticated:
            return reflex_local_auth.LoginState.redir
        print("Estado global cargado para el usuario:", self.authenticated_username)