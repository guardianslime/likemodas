# likemodas/state.py

import reflex as rx

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
    """
    
    nav: NavState = NavState()
    cart: CartState = CartState()
    blog_posts: BlogPostState = BlogPostState()
    blog_add_form: BlogAddFormState = BlogAddFormState()
    blog_edit_form: BlogEditFormState = BlogEditFormState()
    comments: CommentState = CommentState()
    shipping_info: ShippingInfoState = ShippingInfoState()
    purchase_history: PurchaseHistoryState = PurchaseHistoryState()
    admin_confirm: AdminConfirmState = AdminConfirmState()
    payment_history: PaymentHistoryState = PaymentHistoryState()
    contact: ContactState = ContactState()
    search: SearchState = SearchState()
    notifications: NotificationState = NotificationState()