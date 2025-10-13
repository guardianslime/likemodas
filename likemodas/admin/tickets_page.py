# likemodas/admin/tickets_page.py (NUEVO ARCHIVO)

import reflex as rx
from ..state import AppState, SupportTicketAdminData
from ..auth.admin_auth import require_panel_access  # <-- CORRECCIÓN: Importa el decorador correcto

def ticket_list_item(ticket: SupportTicketAdminData) -> rx.Component:
    """Componente para mostrar un ticket en la lista del admin."""
    status_colors = {
        "OPEN": "orange",
        "IN_PROGRESS": "blue",
        "RESOLVED": "green",
        "CLOSED": "gray",
    }
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.heading(ticket.subject, size="4"),
                rx.text(f"Comprador: {ticket.buyer_name}"),
                rx.text(f"Compra ID: #{ticket.purchase_id}"),
                rx.text(f"Fecha: {ticket.created_at_formatted}", size="2", color_scheme="gray"),
                align_items="start",
            ),
            rx.spacer(),
            rx.badge(ticket.status.replace("_", " "), color_scheme=status_colors.get(ticket.status, "gray")),
        ),
        on_click=rx.redirect(f"/returns?purchase_id={ticket.purchase_id}"),
        cursor="pointer",
        width="100%",
        _hover={"background_color": rx.color("gray", 4)},
    )

@require_panel_access # <-- CORRECCIÓN: Usa el nuevo decorador
def admin_tickets_page_content() -> rx.Component:
    """Página para que el admin/vendedor vea y gestione los tickets de soporte."""
    return rx.container(
        rx.vstack(
            rx.heading("Solicitudes de Soporte", size="8"),
            rx.text("Gestiona las solicitudes de devolución y cambio de tus clientes."),
            rx.input(
                placeholder="Buscar por ID de compra, comprador o asunto...",
                value=AppState.search_query_tickets,
                on_change=AppState.set_search_query_tickets,
                width="100%",
                margin_y="1.5em",
            ),
            rx.cond(
                AppState.filtered_support_tickets,
                rx.vstack(
                    rx.foreach(AppState.filtered_support_tickets, ticket_list_item),
                    spacing="3",
                    width="100%",
                ),
                rx.center(rx.text("No se encontraron solicitudes."), padding="2em")
            ),
            align="stretch",
            width="100%",
            max_width="960px",
        ),
        padding_top="2em",
    )