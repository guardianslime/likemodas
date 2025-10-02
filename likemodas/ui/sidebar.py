# likemodas/ui/sidebar.py

import reflex as rx
from ..state import AppState
from .. import navigation

# Las funciones sidebar_item y sidebar_items se mantienen igual
def sidebar_item(text: str, icon: str, href: str, has_notification: rx.Var[bool] = None) -> rx.Component:
    is_active = (AppState.current_path == href)
    return rx.link(
        rx.hstack(
            rx.icon(icon, size=20),
            rx.text(text, size="3"),
            rx.spacer(),
            rx.cond(has_notification, rx.box(width="8px", height="8px", bg="red", border_radius="50%")),
            bg=rx.cond(is_active, rx.color("violet", 4), "transparent"),
            color=rx.cond(is_active, rx.color("violet", 11), rx.color_mode_cond("black", "white")),
            font_weight=rx.cond(is_active, "bold", "normal"),
            border_radius="var(--radius-3)",
            width="100%", padding="0.75em", align="center",
            _hover={"background_color": rx.color("violet", 5)},
        ),
        href=href, underline="none", width="100%",
    )

def sidebar_items() -> rx.Component:
    return rx.vstack(
        sidebar_item("Finanzas", "line-chart", "/admin/finance"),
        sidebar_item("Gestión de Usuarios", "users", "/admin/users"),
        sidebar_item("Mis Publicaciones", "newspaper", "/blog"),
        sidebar_item("Crear Publicación", "square-plus", navigation.routes.BLOG_POST_ADD_ROUTE),
        sidebar_item("Mi Ubicación de Origen", "map-pin", "/admin/my-location"),
        sidebar_item("Confirmar Pagos", "dollar-sign", "/admin/confirm-payments", has_notification=AppState.new_purchase_notification),
        sidebar_item("Historial de Pagos", "history", "/admin/payment-history"),
        sidebar_item("Solicitudes de Soporte", "mailbox", navigation.routes.SUPPORT_TICKETS_ROUTE),
        rx.divider(margin_y="1em"),
        sidebar_item("Tienda (Punto de Venta)", "store", "/admin/store"),
        spacing="2", width="100%",
    )

def sliding_admin_sidebar() -> rx.Component:
    SIDEBAR_WIDTH = "16em"
    sidebar_panel = rx.vstack(
        rx.hstack(
            rx.image(src="/logo.png", width="9em", height="auto", border_radius="25%"),
            align="center", justify="center", width="100%", margin_bottom={"initial": "0.5em", "lg": "1em"},
        ),
        rx.scroll_area(sidebar_items(), flex_grow="1"),
        rx.vstack(
            rx.divider(),
            rx.link(
                rx.hstack(
                    rx.avatar(
                        src=rx.get_upload_url(AppState.profile_info.avatar_url),
                        fallback=rx.cond(AppState.authenticated_user.username, AppState.authenticated_user.username[0].upper(), "?"),
                        size="2"
                    ),
                    # --- 4. CAMBIAR COLOR DEL NOMBRE DE USUARIO ---
                    rx.text(
                        AppState.authenticated_user.username,
                        size={"initial": "2", "lg": "3"},
                        weight="medium",
                        no_of_lines=1,
                        # Se establece el color directamente para que coincida con el tema
                        color="var(--violet-11)"
                    ),
                    # --- FIN DE LA CORRECCIÓN 4 ---
                    align="center", spacing="3", width="100%",
                    padding="0.75em", border_radius="var(--radius-3)",
                    _hover={"background_color": rx.color("violet", 4)},
                ),
                href="/admin/profile", underline="none", width="100%",
            ),
            rx.button(
                "Logout", rx.icon(tag="log-out", margin_left="0.5em"),
                on_click=AppState.do_logout, width="100%", variant="soft", color_scheme="red"
            ),
            width="100%", spacing={"initial": "2", "lg": "3"},
        ),
        spacing={"initial": "2", "lg": "4"}, padding_x="1em", padding_y={"initial": "1.5em", "lg": "2.5em"},
        bg=rx.color("gray", 2), align="start", height="100%", width=SIDEBAR_WIDTH,
    )
    
    # El resto del código para el panel deslizable y el polling se mantiene igual...
    return rx.box(
        rx.hstack(sidebar_panel, rx.box(rx.text("LIKEMODAS", style={"writing_mode": "vertical-rl", "transform": "rotate(180deg)", "padding": "0.5em 0.2em", "font_weight": "bold", "letter_spacing": "2px", "color": "white"}), on_click=AppState.toggle_admin_sidebar, cursor="pointer", bg=rx.color("violet", 9), border_radius="0 8px 8px 0", height="150px", display="flex", align_items="center"), align_items="center", spacing="0"),
        rx.cond(AppState.is_admin, rx.fragment(rx.button(on_click=AppState.poll_for_new_orders, id="admin_notification_poller", display="none"), rx.box(on_mount=rx.call_script("if (!window.likemodas_admin_poller) { window.likemodas_admin_poller = setInterval(() => { const trigger = document.getElementById('admin_notification_poller'); if (trigger) { trigger.click(); } }, 15000); }"), display="none"))),
        position="fixed", top="0", left="0", height="100%", display="flex", align_items="center",
        transform=rx.cond(AppState.show_admin_sidebar, "translateX(0)", f"translateX(-{SIDEBAR_WIDTH})"),
        transition="transform 0.4s ease-in-out", z_index="1000",
    )