import reflex as rx
from ..state import AppState, ReportData
from ..auth.admin_auth import require_panel_access

def report_row(report: ReportData) -> rx.Component:
    """Fila de la tabla de reportes."""
    return rx.table.row(
        rx.table.cell(report.created_at),
        rx.table.cell(
            rx.vstack(
                rx.badge(report.type, color_scheme="purple", variant="solid"),
                rx.text(report.target_name, size="2", weight="bold"),
                align_items="start"
            )
        ),
        rx.table.cell(
            rx.vstack(
                rx.hstack(
                    rx.icon("user", size=14),
                    rx.text(f"Reporta: {report.reporter_name}", size="1"),
                ),
                align_items="start", spacing="1"
            )
        ),
        rx.table.cell(rx.text(report.reason, size="2", color="red")),
        rx.table.cell(
            rx.hstack(
                rx.tooltip(
                    rx.icon_button(
                        rx.icon("trash-2"), 
                        on_click=AppState.resolve_report(report.id, "ban"), 
                        color_scheme="red", 
                        variant="soft"
                    ),
                    content="Borrar Contenido y Cerrar Reporte"
                ),
                rx.tooltip(
                    rx.icon_button(
                        rx.icon("check"), 
                        on_click=AppState.resolve_report(report.id, "dismiss"), 
                        color_scheme="green", 
                        variant="soft"
                    ),
                    content="Descartar (Falso Positivo)"
                ),
                spacing="2"
            )
        )
    )

@require_panel_access
def reports_page_content() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("Gestión de Reportes (Moderación)", size="8"),
            rx.text("Revisa y modera el contenido reportado por los usuarios para mantener la seguridad.", color_scheme="gray"),
            rx.divider(),
            
            rx.cond(
                AppState.admin_reports_list,
                # Si hay reportes, mostramos la tabla
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Fecha"),
                            rx.table.column_header_cell("Contenido"),
                            rx.table.column_header_cell("Reportado Por"),
                            rx.table.column_header_cell("Razón"),
                            rx.table.column_header_cell("Acciones"),
                        )
                    ),
                    rx.table.body(rx.foreach(AppState.admin_reports_list, report_row)),
                    variant="surface",
                    width="100%"
                ),
                # Si NO hay reportes, mostramos el escudo verde (tu diseño original)
                rx.center(
                    rx.vstack(
                        rx.icon("shield-check", size=64, color="green"),
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
        width="100%",
        on_mount=AppState.load_admin_reports
    )