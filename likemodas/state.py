# likemodas/state.py

import reflex as rx
import reflex_local_auth

# Se importan todas las clases de estado que se van a fusionar
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

# --- CORRECCIÓN FINAL ---
# Se elimina 'SessionState' de la lista de bases, porque las otras clases
# ya heredan de ella. Python lo resolverá automáticamente.
class AppState(
    NavState, 
    CartState, 
    BlogPostState, 
    BlogAddFormState, 
    BlogEditFormState, 
    CommentState, 
    PurchaseHistoryState, 
    AdminConfirmState, 
    PaymentHistoryState, 
    ContactState, 
    ShippingInfoState, 
    SearchState, 
    NotificationState
):
    """
    El estado raíz y único de la aplicación.
    Fusiona todos los demás estados a través de herencia múltiple.
    """
    
    def on_load(self):
        """
        Un evento on_load genérico para asegurar que los datos iniciales se cargan.
        """
        if not self.is_authenticated:
            return reflex_local_auth.LoginState.redir
        print("Estado global cargado para el usuario:", self.authenticated_username)