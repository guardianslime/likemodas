# likemodas/ui/sidebar.py (CORREGIDO Y MEJORADO)

import reflex as rx
from reflex.style import toggle_color_mode
from ..state import AppState
from .. import navigation

def sidebar_item(text: str, icon: str, href: str, has_notification: rx.Var[bool] = None) -> rx.Component:
    """Un componente de enlace de sidebar rediseñado que resalta la página activa."""
    
    # --- LÓGICA PARA SABER SI EL ENLACE ESTÁ ACTIVO ---
    is_active = (AppState.current_path == href)

    return rx.link(
        rx.hstack(
            rx.icon(icon, size=20),
            rx.text(text, size="3"), # Tamaño de texto ajustado
            rx.spacer(),
            rx.cond(
                has_notification,
                rx.box(width="8px", height="8px", bg="red", border_radius="50%")
            ),
            # --- ESTILOS MEJORADOS ---
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
        # --- CORRECCIÓN CLAVE: SE ELIMINA EL ON_CLICK PARA QUE EL SIDEBAR NO SE CIERRE ---
        # on_click=lambda: AppState.set_show_admin_sidebar(False), # <--- LÍNEA ELIMINADA
    )

def sidebar_items() -> rx.Component:
    """La lista de vínculos del sidebar."""
    return rx.vstack(
        rx.cond(
            AppState.is_admin,
            rx.fragment(
                rx.vstack(
                    # --- INICIO DE LA MODIFICACIÓN ---
                    sidebar_item("Finanzas", "line-chart", "/admin/finance"), # <-- NUEVO
                    sidebar_item("Gestión de Usuarios", "users", "/admin/users"), # <-- RENOMBRADO
                    # --- FIN DE LA MODIFICACIÓN ---
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
    """El componente completo del sidebar con el nuevo diseño."""
    SIDEBAR_WIDTH = "16em"

    sidebar_panel = rx.vstack(
        # ... (La sección del logo y el scroll_area no cambian) ...
        rx.hstack(
            rx.image(src="/logo.png", width="9em", height="auto", border_radius="25%"),
            align="center", justify="center", width="100%", margin_bottom="1.5em",
        ),
        rx.scroll_area(
            sidebar_items(),
            type="auto",
            scrollbars="vertical",
            flex_grow="1",
        ),
        rx.vstack(
            rx.divider(),
            rx.hstack(
                rx.cond(
                    AppState.is_authenticated,
                    rx.hstack(
                        rx.avatar(fallback=AppState.authenticated_user.username[0].upper(), size="2"),
                        rx.text(AppState.authenticated_user.username, size="3", weight="medium"),
                        align="center",
                        spacing="3",
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
        # --- ✅ INICIO DE LA CORRECCIÓN ✅ ---
        # Se cambia 'padding' por 'padding_x' y 'padding_y' para poder añadir
        # un espacio extra en la parte inferior.
        padding_x="1em",
        padding_top="1em",
        padding_bottom="2.5em", # <-- ESTA LÍNEA EMPUJA TODO HACIA ARRIBA
        # --- ✅ FIN DE LA CORRECCIÓN ✅ ---
        bg=rx.color("gray", 2),
        align="start", height="100%", width=SIDEBAR_WIDTH,
    )

    # El resto de la función no cambia...
    return rx.box(
        rx.hstack(
            sidebar_panel,
            rx.box(
                rx.text(
                    "LIKEMODAS",
                    style={"writing_mode": "vertical-rl", "transform": "rotate(180deg)", "padding": "0.5em 0.2em", "font_weight": "bold", "letter_spacing": "2px", "color": "white"}
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
        transform=rx.cond(
            AppState.show_admin_sidebar,
            "translateX(0)",
            f"translateX(-{SIDEBAR_WIDTH})"
        ),
        transition="transform 0.4s ease-in-out",
        z_index="1000",
    )