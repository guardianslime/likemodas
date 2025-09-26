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
        # La sección de admin sigue igual
        rx.cond(
            AppState.is_admin,
            rx.fragment(
                rx.vstack(
                    sidebar_item("Dashboard", "layout-dashboard", "/admin/users"),
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
        # --- CORRECCIÓN: SE ELIMINA EL VÍNCULO DE CONTACTO ---
        # sidebar_item("Contacto", "mail", navigation.routes.CONTACT_US_ROUTE),
        spacing="2", 
        width="100%",
    )

def sliding_admin_sidebar() -> rx.Component:
    """El componente completo del sidebar con el nuevo diseño."""
    SIDEBAR_WIDTH = "16em"

    sidebar_panel = rx.vstack(
        rx.hstack(
            rx.image(src="/logo.png", width="9em", height="auto", border_radius="25%"),
            align="center", justify="center", width="100%", margin_bottom="1.5em",
        ),
        sidebar_items(),
        rx.spacer(),
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
        padding="1em",
        bg=rx.color("gray", 2),
        align="start", 
        height="100vh", # Asegura que el panel ocupe toda la altura
        width=SIDEBAR_WIDTH,
    )

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
            # --- INICIO DE LA CORRECCIÓN CLAVE ---
            # Se quita la alineación vertical para que el hstack ocupe toda la altura
            align_items="start", 
            spacing="0",
            height="100%",
            # --- FIN DE LA CORRECCIÓN CLAVE ---
        ),
        position="fixed",
        top="0",
        left="0",
        height="100vh",
        display="flex",
        # Se elimina 'align_items="center"' que causaba el corte vertical
        transform=rx.cond(
            AppState.show_admin_sidebar,
            "translateX(0)",
            f"translateX(-{SIDEBAR_WIDTH})"
        ),
        transition="transform 0.4s ease-in-out",
        z_index="1000",
    )