# likemodas/likemodas.py (VERSIÓN FINAL Y CORREGIDA)

import reflex as rx
import reflex_local_auth
from .state import AppState
from .models import Product

# --- Componentes Reutilizables ---

def product_card(p: Product) -> rx.Component:
    """Componente de UI para mostrar una tarjeta de producto."""
    return rx.card(
        rx.vstack(
            rx.heading(p.title, size="5"),
            rx.text(f"${p.price.to_string()}"),
            rx.button("Añadir al carrito", on_click=lambda: AppState.add_to_cart(p.id))
        )
    )

def main_layout(child: rx.Component) -> rx.Component:
    """Layout principal con la barra de navegación."""
    return rx.vstack(
        rx.hstack(
            rx.link(rx.heading("Likemodas"), href="/"),
            rx.spacer(),
            rx.hstack(
                rx.link("Tienda", href="/"),
                rx.cond(
                    AppState.is_authenticated,
                    rx.menu.root(
                        rx.menu.trigger(rx.button(AppState.authenticated_user.username)),
                        rx.menu.content(
                            rx.menu.item("Mi Cuenta", on_click=rx.redirect("/my-account")),
                            rx.cond(AppState.is_admin, rx.menu.item("Admin", on_click=rx.redirect("/admin"))),
                            rx.menu.separator(),
                            rx.menu.item("Cerrar Sesión", on_click=AppState.do_logout),
                        ),
                    ),
                    rx.link(rx.button("Login"), href="/login")
                ),
                rx.link(
                    rx.hstack(
                        rx.icon("shopping-cart"),
                        rx.badge(AppState.cart_items_count),
                    ),
                    href="/cart"
                ),
                spacing="4",
                align="center"
            )
        ),
        rx.container(child, padding_y="2em", width="100%"),
        align="center",
    )

# --- Páginas Públicas ---
def index_page() -> rx.Component:
    """Página de la tienda."""
    return rx.flex(
        rx.foreach(AppState.products, product_card),
        wrap="wrap", spacing="4"
    )

def cart_page() -> rx.Component:
    """Página del carrito."""
    return rx.vstack(
        rx.heading("Carrito de Compras", size="8"),
        rx.heading(f"Total: {AppState.cart_total_cop}", size="5"),
        rx.button("Finalizar Compra", on_click=AppState.handle_checkout)
    )

@reflex_local_auth.require_login
def my_account_page() -> rx.Component:
    return rx.vstack(
        rx.heading("Mi Cuenta", size="8"),
        rx.heading("Mis Pedidos", size="5"),
    )

# --- Páginas de Administración ---
@reflex_local_auth.require_login
def admin_page() -> rx.Component:
    return rx.cond(
        AppState.is_admin,
        rx.vstack(
            rx.heading("Panel de Admin", size="8"),
            rx.link("Gestionar Productos", href="/admin/products"),
        ),
        rx.text("Acceso denegado.")
    )

# --- Páginas de Autenticación Personalizadas ---

def login_page() -> rx.Component:
    """Página de inicio de sesión personalizada."""
    return rx.vstack(
        rx.heading("Iniciar Sesión", size="7"),
        rx.form(
            rx.vstack(
                rx.input(placeholder="Username", name="username", required=True),
                rx.input(placeholder="Password", name="password", type="password", required=True),
                rx.button("Iniciar Sesión", type="submit"),
            ),
            on_submit=AppState.handle_login,
        ),
        rx.link("¿No tienes cuenta? Regístrate aquí.", href="/register"),
        rx.cond(
            reflex_local_auth.LoginState.error_message != "",
            rx.callout(reflex_local_auth.LoginState.error_message, color_scheme="red", icon="triangle_alert")
        )
    )

def register_page() -> rx.Component:
    """Página de registro personalizada."""
    return rx.vstack(
        rx.heading("Crear Cuenta", size="7"),
        rx.form(
            rx.vstack(
                rx.input(placeholder="Username", name="username", required=True),
                rx.input(placeholder="Email", name="email", type="email", required=True),
                rx.input(placeholder="Password", name="password", type="password", required=True),
                rx.button("Crear Cuenta", type="submit"),
            ),
            on_submit=AppState.handle_registration_custom,
        ),
        rx.link("¿Ya tienes cuenta? Inicia sesión.", href="/login"),
        rx.cond(
            AppState.error_message != "",
            rx.callout(AppState.error_message, color_scheme="red", icon="triangle_alert")
        ),
        rx.cond(
            AppState.success_message != "",
            # ▼▼▼ CORRECCIÓN DEL ICONO ▼▼▼
            rx.callout(AppState.success_message, color_scheme="green", icon="check")
        )
    )

# --- Inicialización y Rutas ---
app = rx.App()

app.add_page(main_layout(index_page()), route="/", on_load=AppState.load_products)
app.add_page(main_layout(cart_page()), route="/cart")
app.add_page(main_layout(my_account_page()), route="/my-account", on_load=AppState.load_my_purchases)
app.add_page(main_layout(admin_page()), route="/admin")

app.add_page(main_layout(login_page()), route=reflex_local_auth.routes.LOGIN_ROUTE)
app.add_page(main_layout(register_page()), route=reflex_local_auth.routes.REGISTER_ROUTE)

# ▼▼▼ LÍNEA ELIMINADA ▼▼▼
# app.compile()