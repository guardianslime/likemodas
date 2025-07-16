import reflex as rx
import reflex_local_auth
from . import routes

def force_reload_go_to(path: str):
    """Navega a una URL forzando una recarga completa de la página."""
    return rx.call_script(f"window.location.href = '{path}'")

class NavState(rx.State):
    def to_home(self):
        return rx.redirect(routes.HOME_ROUTE)

    def to_register(self):
        return rx.redirect(reflex_local_auth.routes.REGISTER_ROUTE)

    def to_login(self):
        return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)

    def to_logout(self):
        return rx.redirect(routes.LOGOUT_ROUTE)

    def to_about_us(self):
        return rx.redirect(routes.ABOUT_US_ROUTE)

    def to_articles(self):
        return rx.redirect(routes.ARTICLE_LIST_ROUTE)

    def to_blog(self):
        return rx.redirect(routes.BLOG_POSTS_ROUTE)

    def to_blog_create(self):
        return rx.redirect(routes.BLOG_POST_ADD_ROUTE)

    def to_pulic_galeri(self):
        return rx.redirect(routes.BLOG_PUBLIC_PAGE_ROUTE)

    def to_contact(self):
        return rx.redirect(routes.CONTACT_US_ROUTE)

    def to_pricing(self):
        return rx.redirect(routes.PRICING_ROUTE)
