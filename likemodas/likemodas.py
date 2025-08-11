# likemodas/likemodas.py (CORREGIDO)

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
                            rx.cond(
                                AppState.is_admin,
                                rx.menu.item("Admin", on_click=rx.redirect("/admin"))
                            ),
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
        rx.foreach(
            AppState.products,
            product_card
        ),
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
    # ▼▼▼ CORRECCIÓN 1: Se elimina el on_load de aquí ▼▼▼
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

@reflex_local_auth.require_login
def admin_products_page() -> rx.Component:
    """Página para gestionar productos."""
    return rx.cond(
        AppState.is_admin,
        rx.vstack(
            rx.heading("Gestionar Productos", size="7"),
            rx.card(
                rx.form(
                    rx.vstack(
                        rx.heading("Crear Nuevo Producto", size="5"),
                        rx.input(placeholder="Título", name="title", required=True),
                        rx.text_area(placeholder="Descripción", name="content"),
                        rx.input(placeholder="Precio", name="price", type="number", required=True),
                        rx.button("Crear Producto", type="submit"),
                    ),
                    on_submit=AppState.handle_product_create
                )
            ),
            rx.table.root(
                rx.table.header(
                    rx.table.row(rx.table.column_header_cell("ID"), rx.table.column_header_cell("Título"), rx.table.column_header_cell("Acciones"))
                ),
                rx.table.body(
                    rx.foreach(
                        AppState.products,
                        lambda p: rx.table.row(
                            rx.table.cell(p.id),
                            rx.table.cell(p.title),
                            rx.table.cell(
                                rx.button("Eliminar", on_click=lambda: AppState.delete_product(p.id), color_scheme="red")
                            )
                        )
                    )
                )
            ),
            on_load=AppState.load_products,
            align_items="start"
        ),
        rx.text("No tienes permiso.")
    )


# --- Inicialización y Rutas ---
app = rx.App()

app.add_page(
    main_layout(index_page()),
    route="/",
    on_load=AppState.load_products
)
app.add_page(main_layout(cart_page()), route="/cart")

# ▼▼▼ CORRECCIÓN 2: Se añade el on_load a la definición de la página ▼▼▼
app.add_page(
    main_layout(my_account_page()),
    route="/my-account",
    on_load=AppState.load_my_purchases # <--- Este es el lugar correcto
)

app.add_page(main_layout(admin_page()), route="/admin")
# ... (Aquí irían tus otras rutas de admin)

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