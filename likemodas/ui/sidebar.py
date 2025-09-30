# likemodas/ui/sidebar.py (Versión Restaurada y Corregida)

import reflex as rx
from reflex.style import toggle_color_mode
from ..state import AppState
from .. import navigation

def sidebar_item(text: str, icon: str, href: str, has_notification: rx.Var[bool] = None) -> rx.Component:
    """Un componente de enlace con tamaños responsivos que no afectan la estructura."""
    is_active = (AppState.current_path == href)

    return rx.link(
        rx.hstack(
            rx.icon(icon, size=20),
            rx.text(text, size="3"),
            rx.spacer(),
            rx.cond(
                has_notification,
                rx.box(width="8px", height="8px", bg="red", border_radius="50%")
            ),
            bg=rx.cond(is_active, rx.color("violet", 4), "transparent"),
            color=rx.cond(is_active, rx.color("violet", 11), rx.color_mode_cond("black", "white")),
            font_weight=rx.cond(is_active, "bold", "normal"),
            border_radius="var(--radius-3)",
            width="100%",
            padding="0.75em",
            align="center",
            _hover={
                "background_color": rx.color("violet", 5),
            },
        ),
        href=href,
        underline="none",
        width="100%",
    )

def sidebar_items() -> rx.Component:
    """La lista de vínculos del sidebar."""
    return rx.vstack(
        rx.cond(
            AppState.is_admin,
            rx.fragment(
                rx.vstack(
                    sidebar_item("Finanzas", "line-chart", "/admin/finance"),
                    sidebar_item("Gestión de Usuarios", "users", "/admin/users"),
                    sidebar_item("Mis Publicaciones", "newspaper", "/blog"),
                    sidebar_item("Crear Publicación", "square-plus", navigation.routes.BLOG_POST_ADD_ROUTE),
                    sidebar_item("Mi Ubicación de Envío", "map-pin", "/admin/my-location"),
                    sidebar_item("Confirmar Pagos", "dollar-sign", "/admin/confirm-payments", has_notification=AppState.new_purchase_notification),
                    sidebar_item("Historial de Pagos", "history", "/admin/payment-history"),
                    sidebar_item("Solicitudes de Soporte", "mailbox", navigation.routes.SUPPORT_TICKETS_ROUTE),
                    spacing="2",
                    width="100%"
                ),
                rx.divider(margin_y="1em"),
            )
        ),
        sidebar_item("Tienda", "store", "/admin/store"),
        spacing="2",
        width="100%",
    )

def sliding_admin_sidebar() -> rx.Component:
    """
    Sidebar restaurado a su funcionalidad original de PC,
    con una adaptación sutil y correcta para móvil.
    """
    # --- ✅ 1. RESTAURADO: Ancho fijo para que la animación de PC funcione perfectamente ✅ ---
    SIDEBAR_WIDTH = "16em"

    sidebar_panel = rx.vstack(
        rx.hstack(
            rx.image(src="/logo.png", width="9em", height="auto", border_radius="25%"),
            align="center", justify="center", width="100%", margin_bottom="1.5em",
        ),
        
        # En इpantallas muy cortas, el scroll es la única opción segura.
        # En la mayoría de móviles, no será necesario gracias a la reducción de espacios.
        rx.scroll_area(
            sidebar_items(),
        ),
        
        rx.spacer(),
        
        rx.vstack(
            rx.divider(),
            rx.hstack(
                rx.cond(
                    AppState.is_authenticated,
                    rx.hstack(
                        rx.avatar(fallback=AppState.authenticated_user.username[0].upper(), size="2"),
                        rx.text(AppState.authenticated_user.username, size="3", weight="medium"),
                        align="center", spacing="3",
                    ),
                ),
                rx.spacer(),
                width="100%",
                justify="between",
            ),
            rx.cond(
                AppState.is_authenticated,
                rx.button(
                    "Logout", 
                    rx.icon(tag="log-out", margin_left="0.5em"),
                    on_click=AppState.do_logout,
                    width="100%", 
                    variant="soft", 
                    color_scheme="red"
                )
            ),
            width="100%",
            spacing="3",
        ),
        spacing="5",
        padding="1em",
        bg=rx.color("gray", 2),
        align="start", 
        height="100%", 
        width=SIDEBAR_WIDTH,
    )

    return rx.box(
        rx.hstack(
            sidebar_panel,
            # --- ✅ 2. RESTAURADO: El botón vuelve a su diseño original ✅ ---
            rx.box(
                rx.text(
                    "LIKEMODAS",
                    style={
                        "writing_mode": "vertical-rl", 
                        "transform": "rotate(180deg)", 
                        "padding": "0.5em 0.2em", 
                        "font_weight": "bold", 
                        "letter_spacing": "2px", 
                        "color": "white"
                    }
                ),
                on_click=AppState.toggle_admin_sidebar,
                cursor="pointer",
                bg=rx.color("violet", 9),
                border_radius="0 8px 8px 0",
                height="150px",
                display="flex",
                align_items="center"
            ),
            align_items="center",
            spacing="0",
        ),
        position="fixed",
        top="0",
        left="0",
        height="100vh",
        display="flex",
        align_items="center",
        # --- ✅ 3. RESTAURADO: La lógica original y funcional para ocultar/mostrar ✅ ---
        transform=rx.cond(
            AppState.show_admin_sidebar,
            "translateX(0)",
            f"translateX(-{SIDEBAR_WIDTH})"
        ),
        transition="transform 0.4s ease-in-out",
        z_index="1000",
        # --- ✅ 4. ADAPTACIÓN SUTIL PARA MÓVIL (oculta el sidebar fijo) ✅ ---
        # Este es el truco: en PC (lg), si está abierto, le damos un estilo.
        # En móvil, nunca aplicamos ese estilo, por lo que siempre se puede ocultar.
        className=rx.cond(
            AppState.show_admin_sidebar,
            "expanded-sidebar", # Un nombre de clase para CSS
            ""
        ),
        # Estilos que se aplican con la clase anterior SOLO en pantallas grandes
        _light={
            "& .expanded-sidebar": {
                "@media (min-width: 1024px)": {
                    "transform": "translateX(0) !important",
                },
            },
        },
        _dark={
            "& .expanded-sidebar": {
                "@media (min-width: 1024px)": {
                    "transform": "translateX(0) !important",
                },
            },
        }
    )