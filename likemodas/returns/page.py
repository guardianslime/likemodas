# likemodas/returns/page.py (NUEVO ARCHIVO)

import reflex as rx
import reflex_local_auth
from ..state import AppState, SupportMessageData
from ..ui.skeletons import skeleton_block
from ..models import TicketStatus # <-- AÑADE ESTA LÍNEA

# --- Opciones para la devolución o cambio ---
RETURN_REASONS = [
    "El pedido no cumple con las características",
    "El pedido tiene defectos de fábrica",
    "El pedido no es el correcto",
]
EXCHANGE_REASON = "La talla, medida o número del pedido no es lo que esperabas"

def purchase_summary_header() -> rx.Component:
    """Muestra un resumen de la compra en la parte superior."""
    return rx.cond(
        AppState.current_ticket_purchase,
        rx.box(
            rx.heading(f"Solicitud para la Compra #{AppState.current_ticket_purchase.id}", size="6"),
            rx.text(f"Realizada el: {AppState.current_ticket_purchase.purchase_date_formatted}"),
            rx.text(f"Total: {AppState.current_ticket_purchase.total_price_cop}"),
            rx.divider(margin_y="1em"),
            width="100%",
            padding="1em",
            border="1px solid",
            border_color=rx.color("gray", 6),
            border_radius="md",
        ),
        skeleton_block(height="120px") # Muestra un esqueleto mientras carga
    )

def reason_selection_view() -> rx.Component:
    """Vista para que el usuario seleccione el motivo de su solicitud."""
    return rx.vstack(
        purchase_summary_header(),
        rx.heading("¿Cuál es el motivo de tu solicitud?", size="5", margin_top="1.5em"),
        rx.heading("Devolución", size="4", color_scheme="gray", margin_top="1em"),
        rx.vstack(
            rx.foreach(
                RETURN_REASONS,
                lambda reason: rx.button(
                    reason,
                    on_click=AppState.create_support_ticket(reason),
                    width="100%",
                    variant="outline",
                )
            ),
            spacing="3",
            width="100%",
        ),
        rx.heading("Cambio", size="4", color_scheme="gray", margin_top="1.5em"),
        rx.button(
            EXCHANGE_REASON,
            on_click=AppState.create_support_ticket(EXCHANGE_REASON),
            width="100%",
            variant="outline",
        ),
        spacing="3",
        width="100%",
        max_width="700px",
    )

def chat_message_bubble(message: SupportMessageData) -> rx.Component:
    """Muestra una burbuja de chat, alineada según el autor."""
    is_author_buyer = message.author_id == AppState.current_ticket_purchase.userinfo_id
    return rx.box(
        rx.vstack(
            rx.text(message.author_username, weight="bold", size="2"),
            rx.text(message.content, white_space="pre-wrap"),
            rx.text(message.created_at_formatted, size="1", color_scheme="gray", text_align="right"),
            align_items="start",
            spacing="1",
        ),
        bg=rx.cond(is_author_buyer, rx.color("accent", 4), rx.color("gray", 4)),
        padding="0.75em 1em",
        border_radius="lg",
        max_width="80%",
        align_self=rx.cond(is_author_buyer, "flex-end", "flex-start"),
    )

def chat_view() -> rx.Component:
    """Vista que muestra la conversación del ticket de soporte."""
    # --- INICIO DE LA CORRECCIÓN ---
    is_ticket_open = (AppState.current_ticket.status != TicketStatus.RESOLVED.value) & (AppState.current_ticket.status != TicketStatus.CLOSED.value)
    # --- FIN DE LA CORRECCIÓN ---

    return rx.vstack(
        purchase_summary_header(),
        rx.hstack(
            rx.heading(f"Asunto: {AppState.current_ticket.subject}", size="5", text_align="left"),
            rx.spacer(),
            # --- BOTÓN PARA CERRAR SOLICITUD ---
            rx.cond(
                is_ticket_open,
                rx.alert_dialog.root(
                    rx.alert_dialog.trigger(
                        rx.button("Cerrar Solicitud", color_scheme="red", variant="soft")
                    ),
                    rx.alert_dialog.content(
                        rx.alert_dialog.title("Confirmar Cierre"),
                        rx.alert_dialog.description(
                            "¿Estás seguro de que quieres cerrar esta solicitud? Esta acción no se puede deshacer."
                        ),
                        rx.flex(
                            rx.alert_dialog.cancel(rx.button("Cancelar")),
                            rx.alert_dialog.action(
                                rx.button("Sí, Cerrar", on_click=AppState.close_ticket(AppState.current_ticket.id))
                            ),
                            spacing="3", margin_top="1em", justify="end",
                        ),
                    ),
                ),
            ),
            width="100%",
            margin_top="1.5em"
        ),
        rx.vstack(
            rx.foreach(AppState.ticket_messages, chat_message_bubble),
            spacing="3",
            width="100%",
            max_height="60vh",
            overflow_y="auto",
            padding="1em",
        ),
        rx.cond(
            is_ticket_open,
            # --- FORMULARIO DE MENSAJE (solo si el ticket está abierto) ---
            rx.form(
                rx.hstack(
                    rx.input(
                        name="message_content",
                        placeholder="Escribe tu mensaje...",
                        value=AppState.new_message_content,
                        on_change=AppState.set_new_message_content,
                        flex_grow="1",
                    ),
                    rx.button("Enviar", type="submit"),
                    width="100%",
                ),
                on_submit=AppState.post_support_message,
                reset_on_submit=True,
                width="100%",
            ),
            # --- MENSAJE DE TICKET CERRADO ---
            rx.callout("Esta solicitud ha sido cerrada y ya no se pueden enviar mensajes.", icon="info", width="100%")
        ),
        spacing="4",
        width="100%",
        max_width="800px",
    )

@reflex_local_auth.require_login
def return_exchange_page_content() -> rx.Component:
    """Página principal para devoluciones y cambios."""
    return rx.center(
        rx.cond(
            AppState.is_loading,
            rx.spinner(size="3"),
            rx.cond(
                AppState.current_ticket,
                chat_view(),
                reason_selection_view()
            )
        ),
        min_height="85vh",
        padding="2em",
    )