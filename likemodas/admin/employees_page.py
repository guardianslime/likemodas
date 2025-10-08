# likemodas/admin/employees_page.py

import reflex as rx
from ..state import AppState
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

def sent_request_card(req: EmploymentRequest) -> rx.Component:
    """Tarjeta para una solicitud de empleo enviada."""
    status_colors = {
        RequestStatus.PENDING: "yellow",
        RequestStatus.ACCEPTED: "green",
        RequestStatus.REJECTED: "red",
    }
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.text(
                    "Enviada a: ",
                    rx.text.strong(
                        rx.cond(
                            # --- ✨ INICIO DE LA CORRECCIÓN CLAVE ✨ ---
                            # Se reemplaza 'and' por el operador de bits '&'
                            req.candidate & req.candidate.user,
                            # --- ✨ FIN DE LA CORRECCIÓN CLAVE ✨ ---
                            req.candidate.user.username,
                            f"(Usuario #{req.candidate_id})"
                        )
                    )
                ),
                rx.text(f"Fecha: {req.created_at_formatted}", size="2", color_scheme="gray"),
                align_items="start"
            ),
            rx.spacer(),
            rx.badge(req.status.title(), color_scheme=status_colors.get(req.status, "gray")),
            rx.cond(
                req.status == RequestStatus.PENDING,
                rx.button("Descartar", on_click=AppState.descartar_solicitud_empleo(req.id), color_scheme="gray", variant="soft", size="1")
            )
        )
    )

@require_panel_access
def employees_management_page() -> rx.Component:
    """Página de gestión de empleados, rediseñada para ser más estética y funcional."""
    
    # Vista para móvil
    mobile_view = rx.vstack(
        rx.card(
            rx.vstack(
                rx.heading("Añadir Nuevo Empleado", size="5"),
                rx.form(
                    rx.vstack(
                        rx.input(
                            placeholder="Buscar por nombre de usuario o email...",
                            value=AppState.search_query_users,
                            on_change=AppState.set_search_query_users,
                        ),
                        rx.button("Buscar", type="submit", width="100%"),
                        spacing="3",
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
        
        rx.heading("Mis Empleados Actuales", size="6", margin_top="2em"),
        rx.cond(
            AppState.empleados,
            rx.vstack(rx.foreach(AppState.empleados, current_employee_card), spacing="3", width="100%"),
            rx.text("Aún no tienes empleados asignados.", color_scheme="gray", margin_top="1em")
        ),

        rx.heading("Solicitudes Enviadas", size="6", margin_top="2em"),
        rx.input(
            placeholder="Buscar solicitud por nombre...",
            value=AppState.search_query_sent_requests,
            on_change=AppState.set_search_query_sent_requests,
            margin_bottom="1em",
        ),
        rx.cond(
            AppState.filtered_solicitudes_enviadas,
            rx.vstack(rx.foreach(AppState.filtered_solicitudes_enviadas, sent_request_card), spacing="3", width="100%"),
            rx.text("No has enviado ninguna solicitud.", color_scheme="gray", margin_top="1em")
        ),
        # --- ✨ FIN: MODIFICACIÓN EN VISTA MÓVIL ✨ ---

        spacing="6", width="100%",
        display=["flex", "flex", "none"]
    )

    # Vista para PC
    desktop_view = rx.grid(
        rx.vstack(
            rx.card(
                rx.vstack(
                    rx.heading("Añadir Nuevo Empleado", size="5"),
                    rx.form(
                        rx.hstack(
                            rx.input(
                                placeholder="Buscar por nombre de usuario o email...",
                                value=AppState.search_query_users,
                                on_change=AppState.set_search_query_users,
                                width="100%"
                            ),
                            rx.button("Buscar", type="submit")
                        ),
                        on_submit=AppState.search_users_for_employment
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
            rx.heading("Mis Empleados Actuales", size="6", margin_top="2em"),
            rx.cond(
                AppState.empleados,
                rx.vstack(rx.foreach(AppState.empleados, current_employee_card), spacing="3", width="100%"),
                rx.text("Aún no tienes empleados asignados.", color_scheme="gray", margin_top="1em")
            ),
            spacing="5", align_items="start"
        ),
        rx.vstack(
            rx.heading("Historial de Solicitudes", size="6"),
            rx.input(
                placeholder="Buscar por nombre de candidato...",
                value=AppState.search_query_sent_requests,
                on_change=AppState.set_search_query_sent_requests,
                margin_bottom="1em",
            ),
            rx.scroll_area(
                rx.cond(
                    AppState.filtered_solicitudes_enviadas,
                    rx.vstack(rx.foreach(AppState.filtered_solicitudes_enviadas, sent_request_card), spacing="3", width="100%"),
                    rx.text("No has enviado ninguna solicitud.", color_scheme="gray", margin_top="1em")
                ),
                max_height="60vh", type="auto", scrollbars="vertical", padding_right="1em"
            ),
            spacing="4", align_items="start"
        ),
        # --- ✨ FIN: MODIFICACIÓN EN VISTA DE ESCRITORIO ✨ ---
        columns="2",
        spacing="8",
        width="100%",
        display=["none", "none", "grid"]
    )

    return rx.vstack(
        rx.heading("Gestión de Empleados", size="8", text_align="center"),
        rx.text("Busca usuarios y asígnalos como empleados para que puedan gestionar tus publicaciones.", text_align="center"),
        rx.divider(margin_y="1.5em"),
        mobile_view,
        desktop_view,
        spacing="6",
        width="100%",
        max_width="1400px",
        align="center",
        padding="2em"
    )
