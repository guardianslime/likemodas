# likemodas/admin/finance_page.py (VERSIÓN FINAL Y COMPLETA)

import reflex as rx
from ..state import AppState, ProductFinanceDTO, VariantDetailFinanceDTO
from ..auth.admin_auth import require_admin
from reflex.components.recharts import LineChart, Line, XAxis, YAxis, CartesianGrid, tooltip, Legend, ResponsiveContainer

def stat_card(title: str, value: str, icon: str) -> rx.Component:
    """Muestra una tarjeta de estadística en el dashboard."""
    # ✨ CORRECCIÓN DE SINTAXIS: Argumentos de palabra clave (width, height) al final.
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
            rx.heading("Tendencia de Ganancias Generales (Últimos Días)", size="5", margin_bottom="1em"),
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
                rx.center(rx.text("No hay suficientes datos para mostrar una tendencia.", color_scheme="gray"), height="300px")
            ),
            align_items="start", spacing="4", width="100%"
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
        rx.table.cell(
            rx.button(rx.icon("bar-chart-2"), size="2", on_click=AppState.show_product_detail(p_data.product_id), variant="soft"),
            text_align="center"
        ),
        align="center",
    )

def variant_detail_view() -> rx.Component:
    """Vista detallada para una variante seleccionada dentro del modal."""
    return rx.cond(
        AppState.selected_variant_detail,
        rx.vstack(
            rx.card(
                rx.hstack(
                    rx.image(
                        src=rx.get_upload_url(AppState.selected_variant_detail.image_url),
                        height="100px", width="100px", object_fit="cover", border_radius="lg"
                    ),
                    rx.vstack(
                        rx.text("Detalles de la Variante", size="4", weight="bold"),
                        rx.text(AppState.selected_variant_detail.attributes_str, size="2"),
                        rx.divider(),
                        rx.hstack(
                            rx.vstack(
                                rx.text("Unidades Vendidas", size="2"),
                                rx.heading(AppState.selected_variant_detail.units_sold, size="4"),
                                align_items="start", spacing="0"
                            ),
                            rx.vstack(
                                rx.text("Ingresos", size="2"),
                                rx.heading(AppState.selected_variant_detail.total_revenue_cop, size="4"),
                                align_items="start", spacing="0"
                            ),
                            rx.vstack(
                                rx.text("Costo", size="2"),
                                rx.heading(AppState.selected_variant_detail.total_cogs_cop, size="4"),
                                align_items="start", spacing="0"
                            ),
                            rx.vstack(
                                rx.text("Ganancia Neta", size="2"),
                                rx.heading(AppState.selected_variant_detail.total_net_profit_cop, size="4"),
                                align_items="start", spacing="0"
                            ),
                            spacing="5",
                        ),
                        align_items="start", spacing="2", width="100%"
                    ),
                    spacing="5", align="center", width="100%"
                ),
            ),
            rx.card(
                rx.vstack(
                    rx.heading("Tendencia de Ganancia de la Variante", size="4"),
                    rx.cond(
                        AppState.product_detail_chart_data,
                        rx.box(
                            ResponsiveContainer.create(
                                LineChart.create(
                                    CartesianGrid.create(stroke_dasharray="3 3", stroke=rx.color("gray", 6)),
                                    XAxis.create(data_key="date", stroke=rx.color("gray", 9)),
                                    YAxis.create(stroke=rx.color("gray", 9)),
                                    tooltip(content_style={"backgroundColor": "var(--gray-2)", "border": "1px solid var(--gray-5)"}),
                                    Line.create(type="monotone", data_key="Ganancia", stroke="var(--teal-9)", stroke_width=2, dot=False),
                                    data=AppState.product_detail_chart_data,
                                    margin={"top": 10, "right": 20, "left": 0, "bottom": 0},
                                ),
                            ),
                            height="250px", width="100%"
                        ),
                        rx.center(rx.text("No hay datos de ganancias para esta variante."), height="250px")
                    ),
                    align_items="start", width="100%"
                ),
            ),
            spacing="4", width="100%"
        ),
        rx.center(rx.text("Selecciona una variante de la lista para ver sus detalles."), height="400px")
    )

def product_detail_modal() -> rx.Component:
    """Modal con la sintaxis corregida para el detalle financiero."""
    return rx.dialog.root(
        # ✨ CORRECCIÓN DE SINTAXIS: Todos los componentes hijos van PRIMERO.
        rx.dialog.content(
            rx.cond(
                AppState.selected_product_detail,
                rx.vstack(
                    rx.dialog.title(AppState.selected_product_detail.title),
                    rx.dialog.description("Análisis detallado de ventas por variante."),
                    rx.tabs.root(
                        rx.tabs.list(
                            rx.tabs.trigger("Resumen General", value="summary"),
                            rx.tabs.trigger("Análisis por Variante", value="variants"),
                        ),
                        rx.tabs.content(
                            rx.vstack(
                                rx.grid(
                                    stat_card("Unidades Totales Vendidas", AppState.selected_product_detail.total_units_sold, "package-check"),
                                    stat_card("Ingresos Totales", AppState.selected_product_detail.total_revenue_cop, "trending-up"),
                                    stat_card("Ganancia Total", AppState.selected_product_detail.total_profit_cop, "piggy-bank"),
                                    columns={"initial": "1", "sm": "3"},
                                    spacing="3",
                                    width="100%"
                                ),
                                spacing="4",
                                padding_top="1em"
                            ),
                            value="summary"
                        ),
                        rx.tabs.content(
                            rx.grid(
                                rx.scroll_area(
                                    rx.vstack(
                                        rx.foreach(
                                            AppState.selected_product_detail.variants,
                                            lambda variant, index: rx.box(
                                                rx.hstack(
                                                    rx.image(src=rx.get_upload_url(variant.image_url), height="40px", width="40px", object_fit="cover", border_radius="md"),
                                                    rx.text(variant.attributes_str, size="2"),
                                                    align="center",
                                                    spacing="3",
                                                ),
                                                on_click=AppState.select_variant_for_detail(index),
                                                padding="0.5em",
                                                border_radius="md",
                                                cursor="pointer",
                                                bg=rx.cond(AppState.selected_variant_index == index, rx.color("violet", 3), "transparent"),
                                                _hover={"background_color": rx.color("gray", 3)}
                                            )
                                        ),
                                        spacing="2",
                                        padding_right="0.5em"
                                    ),
                                    type="auto",
                                    scrollbars="vertical",
                                    style={"height": "450px"}
                                ),
                                variant_detail_view(),
                                columns="1fr 2fr",
                                spacing="4",
                                width="100%",
                                padding_top="1em"
                            ),
                            value="variants"
                        ),
                        default_value="summary",
                        width="100%",
                    ),
                    rx.flex(
                        rx.dialog.close(rx.button("Cerrar", variant="soft", color_scheme="gray")),
                        justify="end",
                        width="100%",
                        margin_top="1em"
                    ),
                    spacing="4",
                ),
                rx.center(rx.spinner())
            )
        ),
        # ✨ CORRECCIÓN DE SINTAXIS: Todos los argumentos de palabra clave (props) van DESPUÉS de los hijos.
        open=AppState.show_product_detail_modal,
        on_open_change=AppState.set_show_product_detail_modal,
        style={"max_width": "900px", "width": "95%"}
    )

@require_admin
def finance_page_content() -> rx.Component:
    """Página del dashboard financiero con la UI mejorada y nuevas métricas."""
    return rx.fragment(
        rx.center(
            rx.vstack(
                rx.heading("Dashboard Financiero", size="8", margin_bottom="1.5em"),
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
                                rx.heading("Rendimiento por Producto", size="5"),
                                rx.input(
                                    placeholder="Buscar producto por nombre...",
                                    value=AppState.search_product_finance,
                                    on_change=AppState.set_search_product_finance,
                                    width="100%", max_width="400px",
                                ),
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("Producto"),
                                            rx.table.column_header_cell("Unidades Vendidas", text_align="center"),
                                            rx.table.column_header_cell("Ingresos", text_align="right"),
                                            rx.table.column_header_cell("Costo Total", text_align="right"),
                                            rx.table.column_header_cell("Ganancia Neta", text_align="right"),
                                            rx.table.column_header_cell("Ver Detalles", text_align="center"),
                                        )
                                    ),
                                    rx.table.body(
                                        rx.cond(
                                            AppState.filtered_product_finance_data,
                                            rx.foreach(AppState.filtered_product_finance_data, product_finance_table_row),
                                            rx.table.row(rx.table.cell("No se encontraron datos de productos.", col_span=6, text_align="center"))
                                        )
                                    ),
                                    variant="surface",
                                ),
                                align_items="stretch", spacing="4", width="100%",
                            )
                        ),
                        spacing="6", width="100%",
                    )
                ),
                padding_x="2em", padding_bottom="2em", width="100%", max_width="1400px", align="center", spacing="5",
            ),
            min_height="85vh", width="100%",
        ),
        product_detail_modal()
    )