import reflex as rx
import reflex_local_auth
from reflex.style import toggle_color_mode

from .state import AppState

# --- Módulos de la aplicación ---
from .auth import pages as auth_pages
from .pages import search_results
from .blog import blog_public_page_content, blog_public_detail_content, blog_post_add_content
from .cart import page as cart_page
from .purchases import page as purchases_page
from .admin import page as admin_page
from .contact import page as contact_page
from . import navigation
from .account import shipping_info as shipping_info_module
from .ui.skeletons import skeleton_navbar
from .ui.sidebar import sidebar, mobile_admin_menu, sidebar_dark_mode_toggle_item

# ========================================================================= #
# ======================== INICIO: NUEVA ESTRUCTURA ========================= #
# ========================================================================= #

# --- Componente: Botón de Modo Oscuro ---
def fixed_color_mode_button() -> rx.Component:
    """Botón flotante para cambiar el modo de color."""
    return rx.box(
        rx.button(
            rx.color_mode_cond(light=rx.icon(tag="sun"), dark=rx.icon(tag="moon")),
            on_click=toggle_color_mode,
            variant="soft",
            radius="full"
        ),
        position="fixed", bottom="1.5rem", right="1.5rem", z_index="1000",
    )

# --- Componente: Barra de Navegación Pública ---
def public_navbar() -> rx.Component:
    """La barra de navegación principal para usuarios públicos."""
    icon_color = rx.color_mode_cond("black", "white")
    
    authenticated_icons = rx.hstack(
        rx.link(
            rx.box(
                rx.icon("shopping-cart", size=22, color=icon_color),
                rx.cond(
                    AppState.cart_items_count > 0,
                    rx.box(
                        rx.text(AppState.cart_items_count, size="1", weight="bold"),
                        position="absolute", top="-5px", right="-5px",
                        padding="0 0.4em", border_radius="full", bg="red", color="white",
                    )
                ),
                position="relative", padding="0.5em"
            ),
            href="/cart"
        ),
        align="center", spacing="3", justify="end",
    )
    
    return rx.box(
        rx.grid(
            rx.hstack(
                rx.image(src="/logo.png", width="8em", height="auto", border_radius="md"),
                align="center", spacing="4", justify="start",
            ),
            rx.form(
                rx.input(
                    placeholder="Buscar productos...",
                    value=AppState.search_term,
                    on_change=AppState.set_search_term,
                    width="100%",
                ),
                on_submit=AppState.perform_search,
                width="100%",
            ),
            rx.cond(AppState.is_authenticated, authenticated_icons, rx.box()),
            columns="auto 1fr auto",
            align_items="center",
            width="100%",
            gap="1.5rem",
        ),
        position="fixed", top="0", left="0", right="0",
        width="100%", padding="0.75rem 1.5rem", z_index="999",
        bg=rx.color("accent", 3),
        style={"backdrop_filter": "blur(10px)"},
    )

# --- Layout Principal (el "envoltorio" de cada página) ---
def main_layout(child: rx.Component) -> rx.Component:
    """
    Este es el layout principal que envuelve CADA página.
    Maneja la hidratación y decide qué layout mostrar (público o admin).
    """
    def public_content():
        return rx.box(
            public_navbar(),
            rx.box(
                child,
                padding_top="6rem",
                padding_x="1em",
                padding_bottom="1em",
                width="100%",
            ),
            fixed_color_mode_button(),
            width="100%",
        )

    def admin_content():
        return rx.hstack(
            sidebar(),
            rx.box(child, padding="1em", width="100%"),
            align="start", spacing="0", width="100%", min_height="100vh",
        )

    return rx.cond(
        ~AppState.is_hydrated,
        # Muestra el esqueleto de la navbar mientras carga
        rx.box(skeleton_navbar(), height="6rem"),
        # Cuando está hidratado, elige el layout correcto
        rx.cond(AppState.is_admin, admin_content(), public_content()),
    )

# --- Configuración de la App ---
app = rx.App(
    theme=rx.theme(
        appearance="light", # Puedes cambiar a "dark" si lo prefieres
        has_background=True,
        radius="medium",
        accent_color="violet",
    ),
)

# --- Definición de Rutas (AHORA USANDO main_layout) ---
app.add_page(main_layout(blog_public_page_content()), route="/", on_load=[AppState.on_load])
app.add_page(main_layout(search_results.search_results_content()), route="/search-results", title="Resultados de Búsqueda", on_load=AppState.on_load)
app.add_page(main_layout(auth_pages.my_login_page_content()), route=reflex_local_auth.routes.LOGIN_ROUTE, on_load=AppState.on_load)
app.add_page(main_layout(auth_pages.my_register_page_content()), route=reflex_local_auth.routes.REGISTER_ROUTE, on_load=AppState.on_load)
app.add_page(main_layout(auth_pages.verification_page_content()), route="/verify-email", on_load=[AppState.on_load, AppState.verify_token])
app.add_page(main_layout(auth_pages.forgot_password_page_content()), route="/forgot-password", on_load=AppState.on_load)
app.add_page(main_layout(auth_pages.reset_password_page_content()), route="/reset-password", on_load=[AppState.on_load, AppState.on_load_check_token])
app.add_page(main_layout(blog_public_detail_content()), route=f"{navigation.routes.BLOG_PUBLIC_DETAIL_ROUTE}/[id]", title="Detalle del Producto", on_load=[AppState.on_load, AppState.on_load_public_detail])
app.add_page(main_layout(cart_page.cart_page_content()), route="/cart", title="Mi Carrito", on_load=[AppState.on_load, AppState.load_default_shipping_info])
app.add_page(main_layout(purchases_page.purchase_history_content()), route="/my-purchases", title="Mis Compras", on_load=[AppState.on_load, AppState.load_purchases])
app.add_page(main_layout(shipping_info_module.shipping_info_content()), route=navigation.routes.SHIPPING_INFO_ROUTE, title="Información de Envío", on_load=[AppState.on_load, AppState.load_addresses])
app.add_page(main_layout(blog_post_add_content()), route=navigation.routes.BLOG_POST_ADD_ROUTE, on_load=AppState.on_load)
app.add_page(main_layout(admin_page.admin_confirm_content()), route="/admin/confirm-payments", title="Confirmar Pagos", on_load=[AppState.on_load, AppState.load_pending_purchases])
app.add_page(main_layout(admin_page.payment_history_content()), route="/admin/payment-history", title="Historial de Pagos", on_load=[AppState.on_load, AppState.load_confirmed_purchases])
app.add_page(main_layout(contact_page.contact_entries_list_content()), route=navigation.routes.CONTACT_ENTRIES_ROUTE, on_load=[AppState.on_load, AppState.load_entries])