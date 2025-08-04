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
from .navigation.state import NavState

class AppState(SessionState):
    """
    El estado raíz y único de la aplicación.
    Hereda de SessionState para obtener la lógica de autenticación y tema.
    Contiene todos los demás estados como sub-estados.
    """
    
    # --- CORRECCIÓN FINAL ---
    # Se eliminan los paréntesis () de la instanciación.
    # Ahora solo declaramos el tipo del sub-estado.
    
    nav: NavState
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
        """
        Un evento on_load genérico para asegurar que los datos iniciales se cargan.
        """
        if not self.is_authenticated:
            return reflex_local_auth.LoginState.redir
        print("Estado global cargado para el usuario:", self.authenticated_username)