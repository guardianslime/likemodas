import reflex as rx
import reflex_local_auth
from .. import navigation
from ..state import AppState
from ..models import Category

def notification_icon() -> rx.Component:
    """Componente para el icono y menú de notificaciones."""
    icon_color = rx.color_mode_cond("black", "white")
    return rx.menu.root(
        rx.menu.trigger(
            rx.box(
                rx.icon("bell", size=28, color=icon_color),
                rx.cond(
                    AppState.unread_count > 0,
                    rx.box(
                        rx.text(AppState.unread_count, size="1", weight="bold"),
                        position="absolute", top="-5px", right="-5px",
                        padding="0 0.4em", border_radius="full",
                        bg="red", color="white",
                    )
                ),
                position="relative", padding="0.5em", cursor="pointer"
            ),
        ),
        rx.menu.content(
            rx.cond(
                AppState.user_notifications,
                rx.menu.item(
                    rx.hstack(
                        rx.icon("trash_2", size=16),
                        rx.text("Limpiar todo")
                    ),
                    on_click=AppState.clear_all_notifications,
                    color_scheme="red",
                ),
            ),
            rx.divider(margin_y="0.25em"),
            rx.cond(
                AppState.user_notifications,
                rx.foreach(
                    AppState.user_notifications,
                    lambda n: rx.menu.item(
                        rx.vstack(
                            rx.text(
                                n.message,
                                weight=rx.cond(n.is_read, "regular", "bold"),
                                white_space="normal",
                                width="100%",
                                size="3"
                            ),
                            rx.hstack(
                                rx.spacer(),
                                rx.text(
                                    n.created_at_formatted,
                                    size="2",
                                    color_scheme="gray",
                                ),
                                width="100%",
                                margin_top="0.5em",
                            ),
                            align_items="start",
                            spacing="1",
                            width="100%",
                        ),
                        on_click=rx.cond(n.url, rx.redirect(n.url), AppState.do_nothing),
                        bg=rx.cond(n.is_read, rx.color("gray", 3), rx.color("violet", 4)),
                        _hover={
                            "background_color": rx.cond(n.is_read, rx.color("gray", 5), rx.color("violet", 5))
                        },
                        padding="0.75em",
                        margin="0.25em",
                        border_radius="md",
                        height="auto",
                    )
                ),
                rx.menu.item("No tienes notificaciones.")
            ),
            bg=rx.color("gray", 2),
            style={"backdrop_filter": "blur(10px)"},
            max_height="400px",
            overflow_y="auto",
            min_width="350px",
            padding="0.5em",
        ),
        on_open_change=lambda open: rx.cond(open, None, AppState.mark_all_as_read)
    )


def public_navbar() -> rx.Component:
    """La barra de navegación pública, corregida para búsqueda en vivo y sin bugs de diseño."""
    icon_color = rx.color_mode_cond("black", "white")
    
    hamburger_menu = rx.menu.root(
        rx.menu.trigger(
            rx.icon("menu", size=28, cursor="pointer", color=icon_color)
        ),
        rx.menu.content(
            rx.menu.item("Inicio", on_click=lambda: rx.redirect("/"), color_scheme="violet"),
            rx.menu.sub(
                rx.menu.sub_trigger("Categorías", color_scheme="violet"),
                rx.menu.sub_content(
                    rx.menu.item("Ropa", on_click=lambda: rx.redirect(f"/?category={Category.ROPA.value}"), color_scheme="violet"),
                    rx.menu.item("Calzado", on_click=lambda: rx.redirect(f"/?category={Category.CALZADO.value}"), color_scheme="violet"),
                    rx.menu.item("Mochilas", on_click=lambda: rx.redirect(f"/?category={Category.MOCHILAS.value}"), color_scheme="violet"),
                    rx.menu.item("Ver Todo", on_click=lambda: rx.redirect("/"), color_scheme="violet"),
                ),
            ),
            rx.menu.separator(),
            rx.cond(
                AppState.is_authenticated,
                rx.fragment(
                    rx.menu.item("Mi Cuenta", on_click=lambda: rx.redirect("/my-account/profile"), color_scheme="violet"),
                    rx.menu.item("Mis Compras", on_click=lambda: rx.redirect("/my-purchases"), color_scheme="violet"),
                    rx.menu.item(
                        "Cerrar Sesión", 
                        # --- CORRECCIÓN AQUÍ ---
                        on_click=rx.redirect(navigation.routes.LOGOUT_ROUTE),
                        color_scheme="red"
                    ),
                )
            ),
            rx.cond(
                ~AppState.is_authenticated,
                rx.fragment(
                    rx.menu.separator(),
                    rx.menu.item("Iniciar Sesión", on_click=lambda: rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE), color_scheme="violet"),
                    rx.menu.item("Registrarse", on_click=lambda: rx.redirect(reflex_local_auth.routes.REGISTER_ROUTE), color_scheme="violet"),
                )
            ),
        ),
    )
    
    authenticated_icons = rx.hstack(
        notification_icon(),
        rx.link(
            rx.box(
                rx.icon("shopping-cart", size=22, color=icon_color),
                rx.cond(
                    AppState.cart_items_count > 0,
                    rx.box(
                        rx.text(AppState.cart_items_count, size="1", weight="bold"),
                        position="absolute", top="-5px", right="-5px",
                        padding="0 0.4em", border_radius="full", bg="red", color="white",
                    )
                ),
                position="relative", padding="0.5em"
            ),
            href="/cart"
        ),
        align="center",
        spacing="3",
        justify="end",
    )
    
    placeholder_icons = rx.hstack(
        rx.box(width="44px", height="44px", padding="0.5em"),
        rx.box(width="38px", height="44px", padding="0.5em"),
        align="center",
        spacing="3",
        justify="end",
    )

    return rx.box(
        rx.grid(
            rx.hstack(
                hamburger_menu,
                rx.image(src="/logo.png", width="8em", height="auto", border_radius="md"),
                align="center", spacing="4", justify="start",
            ),
            rx.input(
                placeholder="Buscar productos...",
                value=AppState.search_term,
                on_change=AppState.set_search_term,
                width="100%",
                radius="medium",
                
                # --- INICIO DE LA CORRECCIÓN ---
                # La causa del error está aquí. Tu código local probablemente tiene "..."
                # en lugar de los valores correctos de rx.color(...).
                
                # 1. Usamos una variante neutral que se adapta bien al fondo.
                variant="surface", 
                
                # 2. ¡ESTA ES LA LÍNEA CLAVE!
                # Le decimos al componente que use "violet" para todos sus estados interactivos.
                color_scheme="violet",

                # 3. Mantenemos el estilo de fondo para que coincida con la barra
                style={
                    "background_color": rx.color_mode_cond(
                        light=rx.color("gray", 3),
                        dark=rx.color("gray", 2)
                    ),
                    # Borde sutil por defecto
                    "border": f"1.5px solid {rx.color('gray', 6)}",
                    # Transición suave para los cambios de color
                    "transition": "border-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out",
                    # Estilo al pasar el mouse por encima
                    "_hover": {
                        "border_color": rx.color("violet", 7),
                    },
                    # Estilo al hacer clic (focus), aquí aplicamos el color morado
                    "_focus": {
                        "border_color": rx.color("violet", 9),
                        "box_shadow": f"0 0 0 1px {rx.color('violet', 9)}",
                        "outline": "none",  # Quita el borde azul por defecto del navegador
                    },
                },
            ),
            rx.cond(
                AppState.is_authenticated,
                authenticated_icons,
                placeholder_icons
            ),
            columns="auto 1fr auto",
            align_items="center",
            width="100%",
            gap="1.5rem",
        ),
        
        # ✨ CORRECCIÓN CLAVE 2: Lógica de polling oculta ✨
        # Esta sección ahora está correctamente estructurada para ser invisible
        # y no afectar el diseño de la página.
        rx.cond(
            AppState.is_authenticated,
            rx.fragment(
                rx.button(
                    "Polling Trigger",
                    on_click=AppState.poll_notifications,
                    id="notification_poller_button",
                    display="none",
                ),
                rx.box(
                    on_mount=rx.call_script(
                        """
                        if (!window.likemodas_notification_poller) {
                            window.likemodas_notification_poller = setInterval(() => {
                                const trigger = document.getElementById('notification_poller_button');
                                if (trigger) {
                                    trigger.click();
                                }
                            }, 15000);
                        }
                        """
                    ),
                    display="none",
                )
            )
        ),

        position="fixed", top="0", left="0", right="0",
        width="100%", padding="0.75rem 1.5rem", z_index="999",
        bg=rx.color("gray", 2),
        style={"backdrop_filter": "blur(10px)"},
        on_mount=[AppState.load_notifications],
    )