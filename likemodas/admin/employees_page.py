# likemodas/admin/employees_page.py (VERSIÓN FINAL CON DISEÑO VERTICAL)

import reflex as rx
from ..state import AppState, SentRequestDTO, ActivityLogDTO
from ..models import UserInfo, EmploymentRequest, RequestStatus
from ..auth.admin_auth import require_panel_access

# ... (Las funciones user_search_result_card, current_employee_card y sent_request_card no cambian)
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
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text("Enviada a: ", rx.text.strong(req.candidate_name), size="3"),
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
        padding="0.75em", border="1px solid", border_color=rx.color("gray", 5), border_radius="var(--radius-3)",
    )

def activity_log_card(log: ActivityLogDTO) -> rx.Component:
    """Tarjeta compacta para un registro de actividad."""
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(log.description, size="3", weight="bold"),
                rx.text(f"Realizado por: {log.actor_name}", size="2", color_scheme="gray"),
                align_items="start", spacing="1"
            ),
            rx.spacer(),
            rx.vstack(
                rx.badge(log.action_type),
                rx.text(log.created_at_formatted, size="1", color_scheme="gray"),
                align_items="end", spacing="2"
            ),
        ),
        padding="0.75em", border="1px solid", border_color=rx.color("gray", 5), border_radius="var(--radius-3)",
    )

@require_panel_access
def employees_management_page() -> rx.Component:
    """Página de gestión de empleados con layout vertical y centrado."""

    return rx.center(
        rx.vstack(
            rx.heading("Gestión de Empleados", size="8", text_align="center"),
            rx.text(
                "Busca usuarios y asígnalos como empleados para que puedan gestionar tus publicaciones.",
                color_scheme="gray", text_align="center", max_width="600px"
            ),
            rx.divider(margin_y="1.5em"),

            # --- SECCIONES SUPERIORES: Añadir y ver empleados (1 columna) ---
            rx.grid(
                rx.card(
                    rx.vstack(
                        rx.heading("Añadir Nuevo Empleado", size="5"),
                        rx.form(
                            rx.hstack(
                                rx.input(placeholder="Buscar por nombre o email...", value=AppState.search_query_users, on_change=AppState.set_search_query_users, width="100%"),
                                rx.button("Buscar", type="submit")
                            ),
                            on_submit=AppState.search_users_for_employment, width="100%",
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
                rx.vstack(
                    rx.heading("Mis Empleados Actuales", size="6"),
                    rx.cond(
                        AppState.empleados,
                        rx.vstack(rx.foreach(AppState.empleados, current_employee_card), spacing="3", width="100%"),
                        rx.text("Aún no tienes empleados asignados.", color_scheme="gray", margin_top="1em")
                    ),
                    align_items="stretch", spacing="4"
                ),
                columns={"initial": "1", "md": "2"},
                spacing="6",
                width="100%",
            ),

            rx.divider(margin_y="1.5em"),

            # --- ✨ INICIO DE LA CORRECCIÓN: Grid de 2 columnas para historiales ✨ ---
            rx.grid(
                # Columna Izquierda: Historial de Solicitudes
                rx.vstack(
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
                        spacing="3", width="100%", margin_top="0.5em",
                    ),
                    rx.scroll_area(
                        rx.cond(
                            AppState.filtered_solicitudes_enviadas,
                            rx.vstack(rx.foreach(AppState.filtered_solicitudes_enviadas, sent_request_card), spacing="3", width="100%"),
                            rx.text("No se encontraron solicitudes.", color_scheme="gray", padding="1em")
                        ),
                        height="50vh", type="auto", scrollbars="vertical", padding_right="1em",
                    ),
                    spacing="4", align_items="stretch", width="100%"
                ),

                # Columna Derecha: Historial de Actividad
                rx.vstack(
                    rx.heading("Historial de Actividad de Empleados", size="6"),
                    rx.input(
                        placeholder="Buscar en historial por acción o empleado...",
                        value=AppState.activity_search_query,
                        on_change=AppState.set_activity_search_query,
                    ),
                    # Aquí irían los filtros de fecha si decides añadirlos
                    rx.scroll_area(
                        rx.cond(
                            AppState.filtered_employee_activity,
                            rx.vstack(rx.foreach(AppState.filtered_employee_activity, activity_log_card), spacing="3", width="100%"),
                            rx.text("No hay actividad registrada.", color_scheme="gray", padding="1em")
                        ),
                        height="60vh", # Un poco más alto para aprovechar el espacio
                        type="auto", scrollbars="vertical", padding_right="1em", margin_top="1em"
                    ),
                    spacing="4", align_items="stretch", width="100%"
                ),
                
                # Configuración del Grid
                columns={"initial": "1", "lg": "2"}, # 1 columna en móvil/tablet, 2 en pantallas grandes
                spacing="8",
                width="100%",
                align_items="start",
            ),
            # --- ✨ FIN DE LA CORRECCIÓN ✨ ---

            width="100%",
            max_width="1600px", # Aumentamos el ancho máximo para dar más espacio a las columnas
            spacing="5",
        ),
        padding="2em",
        width="100%",
    )

def activity_log_section() -> rx.Component:
    """Sección completa para el historial de actividad de empleados."""
    return rx.vstack(
        rx.heading("Historial de Actividad de Empleados", size="6"),
        rx.input(
            placeholder="Buscar en historial por acción o empleado...",
            value=AppState.activity_search_query,
            on_change=AppState.set_activity_search_query,
            margin_bottom="1em",
        ),
        # Aquí irían los filtros de fecha, si los implementas
        rx.scroll_area(
            rx.cond(
                AppState.filtered_employee_activity,
                rx.vstack(rx.foreach(AppState.filtered_employee_activity, activity_log_card), spacing="3", width="100%"),
                rx.text("No hay actividad registrada.", color_scheme="gray", padding="1em")
            ),
            height=["40vh", "40vh", "65vh"],
            type="auto", scrollbars="vertical", padding_right="1em"
        ),
        spacing="4", align_items="stretch", width="100%"
    )