# likemodas/ui/sidebar.py (VERSIÓN HÍBRIDA Y DEFINITIVA)

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
    Componente del sidebar deslizable que ahora usa dos layouts diferentes
    para asegurar la compatibilidad en móvil sin afectar la vista de PC.
    """
    SIDEBAR_WIDTH = "16em"

    # --- LAYOUT #1: VERSIÓN PARA MÓVIL Y TABLET (CORREGIDA) ---
    mobile_layout = rx.vstack(
        # Sección Superior Fija (Logo)
        rx.vstack(
            rx.hstack(
                rx.image(src="/logo.png", width="9em", height="auto", border_radius="25%"),
                align="center", justify="center", width="100%",
            ),
            padding_x="1em", padding_top="1.5em", width="100%",
        ),
        # Sección Media Flexible (Links con scroll)
        rx.scroll_area(
            sidebar_items(),
            flex_grow="1", # La clave para que ocupe el espacio sobrante
            padding_x="1em", margin_y="1em", width="100%",
        ),
        # Sección Inferior Fija (Perfil y Logout)
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
                        size="2", weight="medium", no_of_lines=1, color="var(--violet-11)"
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
            width="100%", spacing="2", padding_x="1em", padding_bottom="1.5em",
        ),
        spacing="0", height="100%", width="100%",
    )

    # --- LAYOUT #2: VERSIÓN PARA PC (TU CÓDIGO ORIGINAL) ---
    desktop_layout = rx.vstack(
        # Sección superior que se expande (el comportamiento que te gusta en PC)
        rx.vstack(
            rx.hstack(
                rx.image(src="/logo.png", width="9em", height="auto", border_radius="25%"),
                align="center", justify="center", width="100%", margin_bottom="1em",
            ),
            rx.scroll_area(sidebar_items(), flex_grow="1"),
            rx.spacer(),
            spacing="4", padding_x="1em", padding_top="2.5em", width="100%",
            flex_grow="1",
        ),
        # Sección inferior
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
                        size="3", weight="medium", no_of_lines=1, color="var(--violet-11)"
                    ),
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
            width="100%", spacing="3", padding_x="1em", padding_bottom="2.5em",
        ),
        spacing="0", height="100%", width="100%",
    )

    # --- Contenedor que elige qué layout mostrar ---
    sidebar_panel = rx.fragment(
        # Muestra el layout de móvil en pantallas pequeñas y medianas
        rx.box(
            mobile_layout,
            display=["flex", "flex", "flex", "none"], # flex porque es un vstack
            height="100%", width="100%",
        ),
        # Muestra el layout de PC solo en pantallas grandes
        rx.box(
            desktop_layout,
            display=["none", "none", "none", "flex"], # flex porque es un vstack
            height="100%", width="100%",
        ),
    )

    # Lógica del contenedor deslizable (sin cambios)
    return rx.box(
        rx.hstack(
            rx.box( # Contenedor del panel
                sidebar_panel,
                bg=rx.color("gray", 2),
                height="100%",
                width=SIDEBAR_WIDTH,
            ),
            rx.box( # Pestaña para abrir/cerrar
                rx.text("LIKEMODAS", style={"writing_mode": "vertical-rl", "transform": "rotate(180deg)", "padding": "0.5em 0.2em", "font_weight": "bold", "letter_spacing": "2px", "color": "white"}),
                on_click=AppState.toggle_admin_sidebar,
                cursor="pointer", bg=rx.color("violet", 9), border_radius="0 8px 8px 0",
                height="150px", display="flex", align_items="center"
            ),
            align_items="center", spacing="0"
        ),
        rx.cond( # Lógica de polling (sin cambios)
            AppState.is_admin,
            rx.fragment(
                rx.button(on_click=AppState.poll_for_new_orders, id="admin_notification_poller", display="none"),
                rx.box(on_mount=rx.call_script("if (!window.likemodas_admin_poller) { window.likemodas_admin_poller = setInterval(() => { const trigger = document.getElementById('admin_notification_poller'); if (trigger) { trigger.click(); } }, 15000); }"), display="none")
            )
        ),
        position="fixed", top="0", left="0", height="100%", display="flex", align_items="center",
        transform=rx.cond(AppState.show_admin_sidebar, "translateX(0)", f"translateX(-{SIDEBAR_WIDTH})"),
        transition="transform 0.4s ease-in-out",
        z_index="1000",
    )