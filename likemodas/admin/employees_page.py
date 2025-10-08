# En likemodas/admin/employees_page.py (VERSIÓN FINAL CON DISEÑO MEJORADO)

import reflex as rx
from ..state import AppState, SentRequestDTO
from ..models import UserInfo, EmploymentRequest, RequestStatus
from ..auth.admin_auth import require_panel_access

def user_search_result_card(user: UserInfo) -> rx.Component:
    """Tarjeta para un usuario en los resultados de búsqueda."""
    return rx.card(
        rx.hstack(
            rx.avatar(fallback=rx.cond(user.user, user.user.username[0].upper(), "?")),
            rx.vstack(
                rx.text(rx.cond(user.user, user.user.username, "Usuario Inválido"), weight="bold"),
                rx.text(user.email, size="2", color_scheme="gray"),
                align_items="start"
            ),
            rx.spacer(),
            rx.button("Enviar Solicitud", on_click=AppState.enviar_solicitud_empleo(user.id), size="2", color_scheme="violet")
        )
    )

def current_employee_card(user: UserInfo) -> rx.Component:
    """Tarjeta para un empleado actual."""
    return rx.card(
        rx.hstack(
            rx.avatar(fallback=rx.cond(user.user, user.user.username[0].upper(), "?")),
            rx.vstack(
                rx.text(rx.cond(user.user, user.user.username, "Usuario Inválido"), weight="bold"),
                rx.text(user.email, size="2", color_scheme="gray"),
                align_items="start"
            ),
            rx.spacer(),
            rx.button("Desvincular", on_click=AppState.remove_empleado(user.id), color_scheme="red", variant="soft", size="2")
        )
    )

def sent_request_card(req: SentRequestDTO) -> rx.Component:
    """Tarjeta COMPACTA para una solicitud de empleo enviada, usando el DTO."""
    status_colors = {
        RequestStatus.PENDING.value: "yellow",
        RequestStatus.ACCEPTED.value: "green",
        RequestStatus.REJECTED.value: "red",
    }
    # Usamos rx.box con estilos en lugar de rx.card para más control
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(
                    "Enviada a: ",
                    rx.text.strong(req.candidate_name),
                    size="3"
                ),
                rx.text(req.created_at_formatted, size="2", color_scheme="gray"),
                align_items="start", spacing="1"
            ),
            rx.spacer(),
            rx.vstack(
                rx.badge(req.status.title(), color_scheme=status_colors.get(req.status, "gray")),
                rx.cond(
                    req.status == RequestStatus.PENDING.value,
                    rx.button("Descartar", on_click=AppState.descartar_solicitud_empleo(req.id), color_scheme="gray", variant="soft", size="1", margin_top="0.5em")
                ),
                align_items="end", spacing="2"
            ),
        ),
        padding="0.75em",
        border="1px solid",
        border_color=rx.color("gray", 5),
        border_radius="var(--radius-3)",
    )

@require_panel_access
def employees_management_page() -> rx.Component:
    """Página de gestión de empleados, con layout centrado y filtros de fecha."""
    
    # Columna Izquierda: Añadir y ver empleados
    left_column = rx.vstack(
        rx.card(
            rx.vstack(
                rx.heading("Añadir Nuevo Empleado", size="5"),
                rx.form(
                    rx.hstack(
                        rx.input(placeholder="Buscar por nombre o email...", value=AppState.search_query_users, on_change=AppState.set_search_query_users, width="100%"),
                        rx.button("Buscar", type="submit")
                    ),
                    on_submit=AppState.search_users_for_employment,
                    width="100%",
                ),
                rx.cond(
                    AppState.search_results_users,
                    rx.vstack(
                        rx.foreach(AppState.search_results_users, user_search_result_card),
                        spacing="3", margin_top="1em", width="100%"
                    )
                ),
                spacing="4", width="100%"
            ), width="100%"
        ),
        rx.heading("Mis Empleados Actuales", size="6", margin_top="1.5em"),
        rx.cond(
            AppState.empleados,
            rx.vstack(rx.foreach(AppState.empleados, current_employee_card), spacing="3", width="100%"),
            rx.text("Aún no tienes empleados asignados.", color_scheme="gray", margin_top="1em")
        ),
        spacing="5", align_items="stretch"
    )

    # Columna Derecha: Historial de solicitudes con filtros
    right_column = rx.vstack(
        rx.heading("Historial de Solicitudes", size="6"),
        rx.input(
            placeholder="Buscar por nombre de candidato...",
            value=AppState.search_query_sent_requests,
            on_change=AppState.set_search_query_sent_requests,
        ),
        rx.hstack(
            rx.vstack(
                rx.text("Desde:", size="2"),
                rx.input(type="date", value=AppState.request_history_start_date, on_change=AppState.set_request_history_start_date),
                align_items="stretch",
            ),
            rx.vstack(
                rx.text("Hasta:", size="2"),
                rx.input(type="date", value=AppState.request_history_end_date, on_change=AppState.set_request_history_end_date),
                align_items="stretch",
            ),
            spacing="3", width="100%",
        ),
        rx.scroll_area(
            rx.cond(
                AppState.filtered_solicitudes_enviadas,
                rx.vstack(rx.foreach(AppState.filtered_solicitudes_enviadas, sent_request_card), spacing="3", width="100%"),
                rx.text("No se encontraron solicitudes con los filtros actuales.", color_scheme="gray", padding="1em")
            ),
            height=["40vh", "40vh", "58vh"],
            type="auto", scrollbars="vertical", padding_right="1em"
        ),
        spacing="4", align_items="stretch"
    )

    # Contenedor principal que centra todo el contenido
    return rx.center(
        rx.vstack(
            rx.heading("Gestión de Empleados", size="8", text_align="center"),
            rx.text("Busca usuarios y asígnalos como empleados para que puedan gestionar tus publicaciones.", color_scheme="gray", text_align="center", max_width="600px"),
            rx.divider(margin_y="1.5em"),
            rx.grid(
                left_column,
                right_column,
                columns={"initial": "1", "lg": "2"},
                spacing="6",
                width="100%",
                align_items="start",
            ),
            width="100%",
            max_width="1400px",
            spacing="5",
        ),
        padding="2em",
        width="100%",
    )