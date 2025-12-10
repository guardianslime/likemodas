import reflex as rx
from ..state import AppState, ReportAdminDTO
from ..auth.admin_auth import require_admin

def report_row(report: ReportAdminDTO) -> rx.Component:
    """Fila de la tabla de reportes."""
    return rx.table.row(
        rx.table.cell(report.created_at),
        rx.table.cell(
            rx.vstack(
                rx.badge(report.target_type, color_scheme="purple", variant="solid"),
                rx.text(report.content_preview, size="2", weight="bold"),
                align_items="start"
            )
        ),
        rx.table.cell(
            rx.vstack(
                rx.hstack(
                    rx.icon("user", size=14),
                    rx.text(f"Reporta: {report.reporter_name}", size="1"),
                ),
                rx.hstack(
                    rx.icon("triangle-alert", size=14, color="red"),
                    rx.text(f"Acusado: {report.offender_username}", size="1", color_scheme="red", weight="bold"),
                ),
                align_items="start", spacing="1"
            )
        ),
        rx.table.cell(rx.text(report.reason, size="2")),
        rx.table.cell(
            rx.hstack(
                rx.tooltip(
                    rx.icon_button(
                        rx.icon("trash-2"), 
                        on_click=AppState.resolve_report_and_delete_content(report.id), 
                        color_scheme="red", 
                        variant="soft"
                    ),
                    content="Borrar Contenido y Cerrar"
                ),
                rx.tooltip(
                    rx.icon_button(
                        rx.icon("ban"), 
                        on_click=AppState.resolve_report_and_ban(report.id, report.offender_id), 
                        color_scheme="orange", 
                        variant="soft"
                    ),
                    content="Vetar Usuario y Cerrar"
                ),
                rx.tooltip(
                    rx.icon_button(
                        rx.icon("check"), 
                        on_click=AppState.dismiss_report(report.id), 
                        color_scheme="green", 
                        variant="soft"
                    ),
                    content="Descartar (Falso Positivo)"
                ),
                spacing="2"
            )
        )
    )

@require_admin
def reports_page_content() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("Gestión de Reportes (Moderación)", size="8"),
            rx.text("Revisa y modera el contenido reportado por los usuarios para mantener la seguridad.", color_scheme="gray"),
            rx.divider(),
            
            rx.cond(
                AppState.admin_reports,
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Fecha"),
                            rx.table.column_header_cell("Contenido"),
                            rx.table.column_header_cell("Involucrados"),
                            rx.table.column_header_cell("Razón del Reporte"),
                            rx.table.column_header_cell("Acciones de Moderación"),
                        )
                    ),
                    rx.table.body(rx.foreach(AppState.admin_reports, report_row)),
                    variant="surface",
                    width="100%"
                ),
                rx.center(
                    rx.vstack(
                        rx.icon("shield-check", size=48, color="green"),
                        rx.text("No hay reportes pendientes. ¡La comunidad está segura!", color_scheme="green", size="4"),
                        spacing="3"
                    ),
                    padding="3em",
                    width="100%",
                    border="1px dashed var(--gray-6)",
                    border_radius="md"
                )
            ),
            width="100%",
            max_width="1200px",
            spacing="5",
            padding="2em"
        ),
        width="100%"
    )