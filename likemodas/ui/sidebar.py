# likemodas/ui/sidebar.py (VERSIÓN FINAL CON ALTURA DINÁMICA 'dvh')

import reflex as rx
from ..state import AppState
from .. import navigation

def sidebar_item(text: str, icon: str, href: str, has_notification: rx.Var[bool] = None) -> rx.Component:
    """Componente para un enlace individual en el sidebar (sin cambios)."""
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
            width="100%",
            padding="0.75em",
            align="center",
            _hover={"background_color": rx.color("violet", 5)},
        ),
        href=href,
        underline="none",
        width="100%",
    )

def sidebar_items() -> rx.Component:
    """Genera la lista de enlaces de navegación del sidebar (sin cambios)."""
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
        spacing="2",
        width="100%",
    )

def sliding_admin_sidebar() -> rx.Component:
    """
    Componente del sidebar deslizable con un diseño único y scrollable
    que respeta el área visible en todos los dispositivos.
    """
    SIDEBAR_WIDTH = "16em"

    # --- CONTENIDO COMPLETO DEL SIDEBAR ---
    # Un solo Vstack con todo el contenido, que será envuelto en un área de scroll.
    sidebar_content = rx.vstack(
        rx.hstack(
            rx.image(src="/logo.png", width="9em", height="auto", border_radius="25%"),
            align="center", justify="center", width="100%",
        ),
        sidebar_items(),
        rx.spacer(),
        rx.vstack(
            rx.divider(),
            rx.link(
                rx.hstack(
                    rx.avatar(
                        src=rx.get_upload_url(AppState.profile_info.avatar_url),
                        fallback=rx.cond(AppState.authenticated_user.username, AppState.authenticated_user.username[0].upper(), "?"),
                        size="2"
                    ),
                    rx.text(
                        AppState.authenticated_user.username,
                        size={"initial": "2", "lg": "3"}, weight="medium", no_of_lines=1, color="var(--violet-11)"
                    ),
                    align="center", spacing="3", width="100%", padding="0.75em",
                    border_radius="var(--radius-3)", _hover={"background_color": rx.color("violet", 4)},
                ),
                href="/admin/profile", underline="none", width="100%",
            ),
            rx.button(
                "Logout", rx.icon(tag="log-out", margin_left="0.5em"),
                on_click=AppState.do_logout, width="100%", variant="soft", color_scheme="red"
            ),
            width="100%", spacing={"initial": "2", "lg": "3"},
        ),
        spacing="4",
        padding={"initial": "1.5em 1em", "lg": "2.5em 1em"},
        min_height="100%",
    )

    # --- ENVOLTORIO DE SCROLL ---
    # El contenido se envuelve en un `scroll_area` para permitir el deslizamiento.
    sidebar_panel = rx.scroll_area(
        sidebar_content,
        height="100%",
        width="100%",
    )

    # --- ✨ INICIO DE LA CORRECCIÓN CLAVE ✨ ---
    # El contenedor principal ahora usa `100dvh` para ajustarse a la altura VISIBLE de la pantalla.
    return rx.box(
        rx.hstack(
            rx.box(
                sidebar_panel,
                width=SIDEBAR_WIDTH,
                height="100dvh", # <-- SOLUCIÓN: Usa la altura dinámica del viewport.
                bg=rx.color("gray", 2),
            ),
            rx.box( # La pestaña "LIKEMODAS"
                rx.text("LIKEMODAS", style={"writing_mode": "vertical-rl", "transform": "rotate(180deg)", "padding": "0.5em 0.2em", "font_weight": "bold", "letter_spacing": "2px", "color": "white"}),
                on_click=AppState.toggle_admin_sidebar,
                cursor="pointer", bg=rx.color("violet", 9), border_radius="0 8px 8px 0",
                height="150px", display="flex", align_items="center"
            ),
            align_items="center", spacing="0"
        ),
        # Lógica de polling (sin cambios)
        rx.cond(
            AppState.is_admin,
            rx.fragment(
                rx.button(on_click=AppState.poll_for_new_orders, id="admin_notification_poller", display="none"),
                rx.box(on_mount=rx.call_script("if (!window.likemodas_admin_poller) { window.likemodas_admin_poller = setInterval(() => { const trigger = document.getElementById('admin_notification_poller'); if (trigger) { trigger.click(); } }, 15000); }"), display="none")
            )
        ),
        # El contenedor exterior también usa 100dvh.
        position="fixed", top="0", left="0", height="100dvh", # <-- SOLUCIÓN
        display="flex", align_items="center",
        transform=rx.cond(AppState.show_admin_sidebar, "translateX(0)", f"translateX(-{SIDEBAR_WIDTH})"),
        transition="transform 0.4s ease-in-out",
        z_index="1000",
    )
    # --- ✨ FIN DE LA CORRECCIÓN CLAVE ✨ ---