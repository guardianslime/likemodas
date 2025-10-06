# likemodas/admin/employees_page.py
import reflex as rx
from ..state import AppState
from ..models import UserInfo

def user_search_result_card(user: UserInfo) -> rx.Component:
    """Tarjeta para un usuario en los resultados de búsqueda."""
    return rx.card(
        rx.hstack(
            rx.avatar(fallback=user.user.username[0].upper() if user.user else "?"),
            rx.vstack(
                rx.text(user.user.username, weight="bold"),
                rx.text(user.email, size="2", color_scheme="gray"),
                align_items="start"
            ),
            rx.spacer(),
            rx.button("Añadir como Empleado", on_click=AppState.add_empleado(user.id), size="2", color_scheme="violet")
        )
    )

def current_employee_card(user: UserInfo) -> rx.Component:
    """Tarjeta para un empleado actual."""
    return rx.card(
        rx.hstack(
            rx.avatar(fallback=user.user.username[0].upper() if user.user else "?"),
            rx.vstack(
                rx.text(user.user.username, weight="bold"),
                rx.text(user.email, size="2", color_scheme="gray"),
                align_items="start"
            ),
            rx.spacer(),
            rx.button("Desvincular", on_click=AppState.remove_empleado(user.id), color_scheme="red", variant="soft", size="2")
        )
    )

def employees_management_page() -> rx.Component:
    """Página de gestión de empleados para el vendedor."""
    return rx.vstack(
        rx.heading("Gestión de Empleados", size="8", text_align="center"),
        rx.text("Busca usuarios y asígnalos como empleados para que puedan gestionar tus publicaciones.", text_align="center"),
        
        # Sección para añadir nuevos empleados
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
                        spacing="3",
                        margin_top="1em"
                    )
                ),
                spacing="4"
            ),
            width="100%"
        ),
        
        # Sección para ver empleados actuales
        rx.heading("Mis Empleados Actuales", size="6", margin_top="2em"),
        rx.cond(
            AppState.empleados,
            rx.vstack(
                rx.foreach(AppState.empleados, current_employee_card),
                spacing="3",
                width="100%"
            ),
            rx.text("Aún no tienes empleados asignados.", color_scheme="gray", margin_top="1em")
        ),
        
        spacing="6",
        width="100%",
        max_width="960px",
        align="center",
        padding="2em"
    )