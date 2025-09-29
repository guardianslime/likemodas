# Archivo: likemodas/admin/finance_page.py (CORREGIDO)

import reflex as rx
from ..state import AppState, ProductFinanceDTO
from ..auth.admin_auth import require_admin
from reflex.components.recharts import LineChart, Line, XAxis, YAxis, CartesianGrid, tooltip, Legend, ResponsiveContainer

def stat_card(title: str, value: str, icon: str) -> rx.Component:
    """Componente reutilizable para las tarjetas de estadísticas."""
    return rx.card(
        rx.hstack(
            rx.box(
                rx.icon(icon, size=32),
                padding="0.75em",
                bg=rx.color("violet", 3),
                border_radius="50%",
            ),
            rx.vstack(
                rx.text(title, size="3", color_scheme="gray"),
                rx.heading(value, size="6"),
                align_items="start",
                spacing="0",
            ),
            spacing="4",
            align="center",
        ),
        width="100%",
    )

def finance_chart() -> rx.Component:
    """Componente para el gráfico de ganancias."""
    return rx.box(
        rx.heading("Tendencia de Ganancias (Últimos 30 Días)", size="5", margin_bottom="1em"),
        ResponsiveContainer.create(
            # --- 👇 CORRECCIÓN AQUÍ 👇 ---
            # Se eliminó el argumento `children=[...]` y los componentes se listan directamente.
            LineChart.create(
                CartesianGrid.create(stroke_dasharray="3 3", stroke=rx.color("gray", 6)),
                XAxis.create(data_key="date", stroke=rx.color("gray", 9)),
                YAxis.create(stroke=rx.color("gray", 9)),
                tooltip(
                    content_style={"backgroundColor": "var(--gray-2)", "border": "1px solid var(--gray-5)"}
                ),
                Legend.create(),
                Line.create(type="monotone", data_key="Ganancia", stroke="var(--violet-9)", stroke_width=2),
                data=AppState.profit_chart_data,
                margin={"top": 5, "right": 20, "left": -10, "bottom": 5},
            ),
            # --- FIN DE LA CORRECCIÓN ---
            height="300px",
            width="100%",
        ),
        padding="1.5em",
        border="1px solid var(--gray-5)",
        border_radius="var(--radius-3)",
    )

def product_finance_table_row(p_data: ProductFinanceDTO) -> rx.Component:
    """Fila para la tabla de finanzas por producto."""
    return rx.table.row(
        rx.table.cell(p_data.title),
        rx.table.cell(p_data.units_sold, text_align="center"),
        rx.table.cell(p_data.total_revenue_cop, text_align="right"),
        rx.table.cell(p_data.total_profit_cop, text_align="right", weight="bold"),
        align="center",
    )

@require_admin
def finance_page_content() -> rx.Component:
    """Página del dashboard financiero."""
    return rx.vstack(
        rx.heading("Dashboard Financiero", size="8"),
        rx.cond(
            AppState.is_loading,
            rx.center(rx.spinner(size="3"), height="70vh"),
            rx.vstack(
                # Tarjetas de estadísticas
                rx.grid(
                    stat_card("Ingresos Totales", AppState.finance_stats.total_revenue_cop, "trending-up"),
                    stat_card("Ganancia Neta", AppState.finance_stats.total_profit_cop, "piggy-bank"),
                    stat_card("Total Ventas", AppState.finance_stats.total_sales_count.to_string(), "package"),
                    stat_card("Margen de Ganancia", AppState.finance_stats.profit_margin_percentage, "percent"),
                    stat_card("Envío Recaudado", AppState.finance_stats.total_shipping_cop, "truck"),
                    stat_card("Ticket Promedio", AppState.finance_stats.average_order_value_cop, "receipt"),
                    columns={"initial": "1", "sm": "2", "lg": "3"},
                    spacing="4",
                    width="100%",
                ),
                
                # Gráfico
                finance_chart(),

                # Tabla de productos
                rx.vstack(
                    rx.heading("Rendimiento por Producto", size="5"),
                    rx.input(
                        placeholder="Buscar producto por nombre...",
                        value=AppState.search_product_finance,
                        on_change=AppState.set_search_product_finance,
                        width="100%",
                        max_width="400px",
                    ),
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Producto"),
                                rx.table.column_header_cell("Unidades Vendidas", text_align="center"),
                                rx.table.column_header_cell("Ingresos", text_align="right"),
                                rx.table.column_header_cell("Ganancia", text_align="right"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(AppState.filtered_product_finance_data, product_finance_table_row)
                        ),
                        variant="surface",
                    ),
                    align_items="start",
                    spacing="4",
                    width="100%",
                ),
                spacing="6",
                width="100%",
            )
        ),
        padding="2em",
        width="100%",
        max_width="1400px",
        align="center",
    )