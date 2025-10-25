# likemodas/ui/sidebar.py

import reflex as rx
from ..state import AppState
from .. import navigation

def sidebar_item(text: str, icon: str, href: str, has_notification: rx.Var[bool] = None) -> rx.Component:
    """Componente reutilizable para un enlace individual en el sidebar."""
    # Lógica avanzada: se activa si la ruta actual EMPIEZA con el href del enlace
    is_active = rx.cond(
        href == "/",
        AppState.current_path == "/",
        (AppState.current_path.startswith(href)) & (href != "/")
    )
    
    return rx.link(
        rx.hstack(
            rx.icon(icon, size=20),
            rx.text(text, size="3"),
            rx.spacer(),
            rx.cond(has_notification, rx.box(width="8px", height="8px", bg="red", border_radius="50%")),
            # Aplica el fondo morado si el enlace está activo
            bg=rx.cond(is_active, rx.color("violet", 4), "transparent"),
            # Cambia el color del texto y el grosor si está activo
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
    """
    [CORREGIDO] Genera los enlaces del sidebar, mostrando los elementos de
    gestión también a los empleados.
    """
    elementos_base = rx.fragment(
        sidebar_item("Mis Publicaciones", "newspaper", "/blog"),
        sidebar_item("Crear Publicación", "square-plus", navigation.routes.BLOG_POST_ADD_ROUTE),
        sidebar_item("Tienda (Punto de Venta)", "store", "/admin/store"),
    )

    elementos_gestion_vendedor = rx.fragment(
        sidebar_item("Finanzas", "line-chart", "/admin/finance"),
        sidebar_item("Gestión de Empleados", "user-cog", "/admin/employees"),
        sidebar_item("Mi Ubicación de Origen", "map-pin", "/admin/my-location"),
        sidebar_item("Confirmar Pagos", "dollar-sign", "/admin/confirm-payments", has_notification=AppState.new_purchase_notification),
        sidebar_item("Historial de Pagos", "history", "/admin/payment-history"),
        sidebar_item("Solicitudes de Soporte", "mailbox", navigation.routes.SUPPORT_TICKETS_ROUTE),
    )

    elementos_exclusivos_admin = rx.fragment(
        sidebar_item("Gestión de Usuarios", "users", "/admin/users"),
    )

    return rx.vstack(
        elementos_base,
        
        # --- ✨ CORRECCIÓN CLAVE: SE ELIMINA LA CONDICIÓN QUE OCULTABA ESTO ✨ ---
        # Ahora los empleados también verán estos elementos de gestión.
        elementos_gestion_vendedor,

        # La lógica para los elementos exclusivos de admin se mantiene igual
        rx.cond(
            AppState.is_admin & ~AppState.is_vigilando,
            elementos_exclusivos_admin
        ),
        spacing="2",
        width="100%",
    )


def sliding_admin_sidebar() -> rx.Component:
    """Componente del sidebar deslizable."""
    SIDEBAR_WIDTH = "16em"

    sidebar_content = rx.vstack(
        rx.hstack(
            # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
            # Envolvemos la imagen en un rx.link que apunta a la tienda del admin/vendedor
            rx.link(
                rx.image(src="/logo.png", width="9em", height="auto", border_radius="25%"),
                href="/admin/store" # <--- Esta es la ruta correcta
            ),
            # --- ✨ FIN DE LA CORRECCIÓN ✨ ---
            align="center", justify="center", width="100%",
        ),
        rx.cond(
            AppState.is_vigilando,
            rx.box(
                rx.hstack(
                    rx.icon("eye", size=16),
                    rx.text("Modo Vigilancia", size="2", weight="bold"),
                    rx.spacer(),
                    rx.icon_button(
                        rx.icon("circle-x", size=16),
                        on_click=AppState.stop_vigilancia,
                        size="1",
                        variant="ghost",
                        color_scheme="red",
                    ),
                    align="center",
                ),
                bg=rx.color("red", 4),
                padding="0.5em",
                border_radius="md",
                width="100%",
                margin_bottom="1em",
            )
        ),
        # --- ✨ INICIO DE LA MODIFICACIÓN: BANNER "MODO EMPLEADO" MEJORADO ✨ ---
        rx.cond(
            AppState.is_empleado,
            rx.box(
                rx.hstack(
                    rx.icon("briefcase", size=16),
                    rx.vstack(
                        rx.text("Modo Empleado", size="2", weight="bold"),
                        rx.text(
                            # Usamos rx.cond para evitar errores si la info no ha cargado
                            rx.cond(
                                AppState.mi_vendedor_info,
                                "Trabajando para: " + AppState.mi_vendedor_info.user.username,
                                "Cargando..."
                            ),
                            size="1"
                        ),
                        spacing="0",
                        align_items="start"
                    ),
                    rx.spacer(),
                    # Botón para salir del modo empleado (desvincularse)
                    rx.icon_button(
                        rx.icon("circle-x", size=16),
                        on_click=AppState.leave_employment, # <-- Llama a la nueva función
                        size="1",
                        variant="ghost",
                        color_scheme="red",
                    ),
                    align="center",
                ),
                bg=rx.color("cyan", 4),
                padding="0.5em",
                border_radius="md",
                width="100%",
                margin_bottom="1em",
            )
        ),
        # --- ✨ FIN DE LA MODIFICACIÓN ✨ ---

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
                href="/admin/profile", 
                underline="none", width="100%",
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

    sidebar_panel = rx.scroll_area(
        sidebar_content,
        height="100%",
        width="100%",
    )

    return rx.box(
        rx.hstack(
            rx.box(
                sidebar_panel,
                width=SIDEBAR_WIDTH,
                height="100dvh",
                bg=rx.color("gray", 2),
            ),
            rx.box(
                rx.text("LIKEMODAS", style={"writing_mode": "vertical-rl", "transform": "rotate(180deg)", "padding": "0.5em 0.2em", "font_weight": "bold", "letter_spacing": "2px", "color": "white"}),
                on_click=AppState.toggle_admin_sidebar,
                cursor="pointer", bg=rx.color("violet", 9), border_radius="0 8px 8px 0",
                height="150px", display="flex", align_items="center"
            ),
            align_items="center", spacing="0",
        ),
        
        # --- ✨ INICIO DE LA CORRECCIÓN CLAVE ✨ ---
        # Ahora, este sondeo se activa para CUALQUIER rol que vea el panel.
        rx.cond(
            AppState.is_admin | AppState.is_vendedor | AppState.is_empleado,
            rx.fragment(
                rx.button(
                    on_click=AppState.poll_admin_notifications, 
                    id="admin_notification_poller", 
                    display="none"
                ),
                rx.box(on_mount=rx.call_script("if (!window.likemodas_admin_poller) { window.likemodas_admin_poller = setInterval(() => { const trigger = document.getElementById('admin_notification_poller'); if (trigger) { trigger.click(); } }, 15000); }"), display="none")
            )
        ),
        # --- ✨ FIN DE LA CORRECCIÓN CLAVE ✨ ---

        position="fixed", top="0", left="0", height="100dvh",
        display="flex", align_items="center",
        transform=rx.cond(AppState.show_admin_sidebar, "translateX(0)", f"translateX(-{SIDEBAR_WIDTH})"),
        transition="transform 0.4s ease-in-out",
        z_index="1000",
    )