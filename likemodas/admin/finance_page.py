# likemodas/admin/finance_page.py (Versión con todas las funcionalidades)

import reflex as rx

from likemodas.blog.public_page import product_detail_modal
from ..state import AppState, ProductFinanceDTO, VariantDetailFinanceDTO
from ..auth.admin_auth import require_admin
from reflex.components.recharts import LineChart, Line, XAxis, YAxis, CartesianGrid, tooltip, Legend, ResponsiveContainer

def stat_card(title: str, value: str, icon: str) -> rx.Component:
    """Muestra una tarjeta de estadística en el dashboard."""
    return rx.card(
        rx.hstack(
            rx.box(rx.icon(icon, size=32), padding="0.75em", bg=rx.color("violet", 3), border_radius="50%"),
            rx.vstack(
                rx.text(title, size="3", color_scheme="gray"),
                rx.heading(value, size="6"),
                align_items="start", spacing="0"
            ),
            spacing="4", align="center"
        ),
        width="100%", height="100%"
    )

def general_finance_chart() -> rx.Component:
    """Componente para el gráfico de ganancias generales."""
    return rx.card(
        rx.vstack(
            rx.heading("Tendencia de Ganancias Generales", size="5", margin_bottom="1em"),
            rx.cond(
                AppState.profit_chart_data,
                rx.box(
                    ResponsiveContainer.create(
                        LineChart.create(
                            CartesianGrid.create(stroke_dasharray="3 3", stroke=rx.color("gray", 6)),
                            XAxis.create(data_key="date", stroke=rx.color("gray", 9)),
                            YAxis.create(stroke=rx.color("gray", 9)),
                            tooltip(content_style={"backgroundColor": "var(--gray-2)", "border": "1px solid var(--gray-5)"}),
                            Legend.create(),
                            Line.create(type="monotone", data_key="Ganancia", stroke="var(--violet-9)", stroke_width=2, dot=False),
                            data=AppState.profit_chart_data,
                            margin={"top": 10, "right": 30, "left": 0, "bottom": 0},
                        ),
                    ),
                    height="300px",
                    width="100%",
                ),
                rx.center(rx.text("No hay datos de ganancias para el rango de fechas seleccionado.", color_scheme="gray"), height="300px")
            ),
            align_items="start", spacing="4", width="100%"
        )
    )

def mobile_finance_card(p_data: ProductFinanceDTO) -> rx.Component:
    """Una tarjeta responsiva para mostrar el rendimiento de un producto en móvil."""
    return rx.card(
        rx.vstack(
            rx.heading(p_data.title, size="4"),
            rx.divider(margin_y="0.75em"),
            rx.grid(
                rx.vstack(rx.text("Unidades", size="2", color_scheme="gray"), rx.text(p_data.units_sold, weight="bold"), align="center"),
                rx.vstack(rx.text("Ingresos", size="2", color_scheme="gray"), rx.text(p_data.total_revenue_cop, weight="bold"), align="center"),
                rx.vstack(rx.text("Costo", size="2", color_scheme="gray"), rx.text(p_data.total_cogs_cop, weight="bold"), align="center"),
                rx.vstack(rx.text("Ganancia", size="2", color_scheme="gray"), rx.text(p_data.total_net_profit_cop, weight="bold"), align="center"),
                rx.vstack(rx.text("Margen", size="2", color_scheme="gray"), rx.text(p_data.profit_margin_str, weight="bold"), align="center"),
                columns="2",
                spacing_x="3",
                spacing_y="4",
                width="100%",
            ),
            rx.button(
                "Ver Detalles",
                rx.icon("bar-chart-2", margin_left="0.5em"),
                on_click=AppState.show_product_detail(p_data.product_id),
                variant="soft",
                width="100%",
                margin_top="1em"
            ),
            spacing="3",
            width="100%"
        )
    )

def product_finance_table_row(p_data: ProductFinanceDTO) -> rx.Component:
    """Define una fila en la tabla de rendimiento por producto."""
    return rx.table.row(
        rx.table.cell(p_data.title),
        rx.table.cell(p_data.units_sold, text_align="center"),
        rx.table.cell(p_data.total_revenue_cop, text_align="right"),
        rx.table.cell(p_data.total_cogs_cop, text_align="right", color_scheme="gray"),
        rx.table.cell(p_data.total_net_profit_cop, text_align="right", weight="bold"),
        rx.table.cell(p_data.profit_margin_str, text_align="right", weight="bold"),
        rx.table.cell(
            rx.button(rx.icon("bar-chart-2"), size="2", on_click=AppState.show_product_detail(p_data.product_id), variant="soft"),
            text_align="center"
        ),
        align="center",
    )

# ... (Las funciones `variant_detail_view` y `product_detail_modal` no cambian, puedes dejarlas como están)

@require_admin
def finance_page_content() -> rx.Component:
    """Página del dashboard financiero con la UI mejorada y nuevas métricas."""
    desktop_table = rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Producto"),
                    rx.table.column_header_cell("Unidades Vendidas", text_align="center"),
                    rx.table.column_header_cell("Ingresos", text_align="right"),
                    rx.table.column_header_cell("Costo Total", text_align="right"),
                    rx.table.column_header_cell("Ganancia Neta", text_align="right"),
                    rx.table.column_header_cell("Margen (%)", text_align="right"),
                    rx.table.column_header_cell("Ver Detalles", text_align="center"),
                )
            ),
            rx.table.body(
                rx.cond(
                    AppState.filtered_product_finance_data,
                    rx.foreach(AppState.filtered_product_finance_data, product_finance_table_row),
                    rx.table.row(rx.table.cell("No se encontraron datos para el rango de fechas seleccionado.", col_span=7, text_align="center"))
                )
            ),
            variant="surface",
        ),
        display=["none", "none", "block"]
    )

    mobile_card_list = rx.box(
        rx.vstack(
            rx.cond(
                AppState.filtered_product_finance_data,
                rx.foreach(AppState.filtered_product_finance_data, mobile_finance_card),
                rx.center(rx.text("No se encontraron datos para el rango de fechas seleccionado."), padding="2em")
            ),
            spacing="4", width="100%"
        ),
        display=["block", "block", "none"]
    )

    return rx.fragment(
        rx.center(
            rx.vstack(
                rx.heading("Dashboard Financiero", size="8", margin_bottom="0.5em"),
                
                rx.card(
                    rx.flex(
                        rx.vstack(
                            rx.text("Desde", size="2"),
                            rx.input(type="date", value=AppState.finance_start_date, on_change=AppState.set_finance_start_date),
                            align="start"
                        ),
                        rx.vstack(
                            rx.text("Hasta", size="2"),
                            rx.input(type="date", value=AppState.finance_end_date, on_change=AppState.set_finance_end_date),
                            align="start"
                        ),
                        rx.button("Filtrar", on_click=AppState.filter_finance_data, margin_top="1.25em"),
                        spacing="4",
                        direction={"initial": "column", "sm": "row"},
                        align={"initial": "stretch", "sm": "end"},
                        width="100%"
                    ),
                    width="100%"
                ),
                
                rx.cond(
                    AppState.is_loading,
                    rx.center(rx.spinner(size="3"), height="70vh"),
                    rx.vstack(
                        rx.grid(
                            stat_card("Ingresos Totales", AppState.finance_stats.total_revenue_cop, "trending-up"),
                            stat_card("Costo de Mercancía", AppState.finance_stats.total_cogs_cop, "receipt"),
                            stat_card("Ganancia Neta", AppState.finance_stats.total_profit_cop, "piggy-bank"),
                            stat_card("Total Ventas", AppState.finance_stats.total_sales_count, "package"),
                            stat_card("Envío Recaudado", AppState.finance_stats.total_shipping_cop, "truck"),
                            stat_card("Ganancia/Pérdida por Envío", AppState.finance_stats.shipping_profit_loss_cop, "percent"),
                            columns={"initial": "1", "sm": "2", "lg": "3"},
                            spacing="4",
                            width="100%",
                        ),
                        general_finance_chart(),
                        rx.card(
                            rx.vstack(
                                rx.hstack(
                                    rx.heading("Rendimiento por Producto", size="5"),
                                    rx.spacer(),
                                    rx.button("Exportar a CSV", on_click=AppState.export_product_finance_csv, variant="soft", size="2"),
                                    width="100%",
                                    justify="between"
                                ),
                                rx.input(
                                    placeholder="Buscar producto por nombre...",
                                    value=AppState.search_product_finance,
                                    on_change=AppState.set_search_product_finance,
                                    width="100%", max_width="400px",
                                ),
                                desktop_table,
                                mobile_card_list,
                                align_items="stretch", spacing="4", width="100%",
                            )
                        ),
                        spacing="6", width="100%",
                    )
                ),
                padding_x=["1em", "1.5em", "2em"],
                padding_bottom="2em",
                width="100%", max_width="1400px", align="center", spacing="5",
            ),
            min_height="85vh", width="100%",
        ),
        product_detail_modal()
    )