# likemodas/likemodas.py

import reflex as rx
import reflex_local_auth
from .state import AppState

# --- Componentes Reutilizables ---
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
                            rx.link(rx.menu.item("Mi Cuenta"), href="/my-account"),
                            rx.cond(AppState.is_admin, rx.link(rx.menu.item("Admin"), href="/admin")),
                            rx.menu.item("Cerrar Sesión", on_click=AppState.do_logout),
                        ),
                    ),
                    rx.link(rx.button("Login"), href="/login")
                ),
                rx.link(rx.badge(AppState.cart_items_count), href="/cart"),
                spacing="4"
            )
        ),
        rx.container(child, padding_y="2em"),
        align="center",
    )

# --- Páginas Públicas ---
def index_page() -> rx.Component:
    """Página de la tienda."""
    return rx.flex(
        rx.foreach(
            AppState.products,
            lambda p: rx.card(
                rx.vstack(
                    rx.heading(p.title, size="5"),
                    rx.text(p.price_cop),
                    rx.button("Añadir al carrito", on_click=lambda: AppState.add_to_cart(p.id))
                )
            )
        ),
        wrap="wrap", spacing="4", on_load=AppState.load_products
    )

def cart_page() -> rx.Component:
    """Página del carrito."""
    return rx.vstack(
        rx.heading("Carrito de Compras", size="8"),
        rx.button("Finalizar Compra", on_click=AppState.handle_checkout)
        # Aquí iría la tabla de items del carrito...
    )

@reflex_local_auth.require_login
def my_account_page() -> rx.Component:
    return rx.vstack(
        rx.heading("Mi Cuenta", size="8"),
        rx.heading("Mis Pedidos", size="5"),
        # Aquí iría la lista de pedidos...
        on_load=AppState.load_my_purchases,
    )

# --- Páginas de Administración ---
@reflex_local_auth.require_login
def admin_page() -> rx.Component:
    return rx.cond(
        AppState.is_admin,
        rx.vstack(
            rx.heading("Panel de Admin", size="8"),
            rx.link("Gestionar Productos", href="/admin/products"),
            rx.link("Gestionar Usuarios", href="/admin/users"),
            rx.link("Ver Órdenes", href="/admin/orders"),
        ),
        rx.text("Acceso denegado.")
    )

@reflex_local_auth.require_login
def admin_products_page():
    # El formulario para crear productos y la tabla de productos existentes.
    pass # La lógica ya está en el state, aquí va la UI

@reflex_local_auth.require_login
def admin_users_page():
    # La tabla para ver usuarios y amonestarlos (ban).
    pass # La lógica ya está en el state, aquí va la UI

@reflex_local_auth.require_login
def admin_orders_page():
    # La tabla para ver todas las órdenes.
    pass # La lógica ya está en el state, aquí va la UI


# --- Inicialización y Rutas ---
app = rx.App()
app.add_page(main_layout(index_page()), route="/")
app.add_page(main_layout(cart_page()), route="/cart")
app.add_page(main_layout(my_account_page()), route="/my-account")

# Rutas de Admin
app.add_page(main_layout(admin_page()), route="/admin")
# ... agregar aquí las páginas de admin_products, admin_users, etc.

# Rutas de Autenticación
app.add_page(
    main_layout(reflex_local_auth.login_page(on_submit=AppState.handle_login)),
    route=reflex_local_auth.routes.LOGIN_ROUTE
)
app.add_page(
    main_layout(reflex_local_auth.register_page(on_submit=AppState.handle_registration_custom)),
    route=reflex_local_auth.routes.REGISTER_ROUTE
)

app.compile()