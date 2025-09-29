# likemodas/admin/finance_page.py

import reflex as rx
from ..state import AppState, ProductFinanceDTO, ProductDetailFinanceDTO, VariantDetailFinanceDTO
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
        height="100%", # Asegura que las tarjetas tengan la misma altura
    )

def general_finance_chart() -> rx.Component:
    """Componente para el gráfico de ganancias generales, ahora dentro de una tarjeta."""
    return rx.card(
        rx.vstack(
            rx.heading("Tendencia de Ganancias Generales (Últimos Días)", size="5", margin_bottom="1em"),
            rx.cond(
                AppState.profit_chart_data,
                ResponsiveContainer.create(
                    LineChart.create(
                        CartesianGrid.create(stroke_dasharray="3 3", stroke=rx.color("gray", 6)),
                        XAxis.create(data_key="date", stroke=rx.color("gray", 9)),
                        YAxis.create(stroke=rx.color("gray", 9)),
                        tooltip(
                            content_style={"backgroundColor": "var(--gray-2)", "border": "1px solid var(--gray-5)"}
                        ),
                        Legend.create(),
                        Line.create(type="monotone", data_key="Ganancia", stroke="var(--violet-9)", stroke_width=2, dot=False),
                        data=AppState.profit_chart_data,
                        margin={"top": 10, "right": 30, "left": 0, "bottom": 0},
                    ),
                    aspect=3, # Proporción para la gráfica general
                ),
                rx.text("No hay datos de ganancias para mostrar en la gráfica.", color_scheme="gray")
            ),
            align_items="start",
            spacing="4",
            width="100%",
        )
    )

def product_finance_table_row(p_data: ProductFinanceDTO) -> rx.Component:
    """Fila para la tabla de finanzas por producto."""
    return rx.table.row(
        rx.table.cell(p_data.title),
        rx.table.cell(p_data.units_sold, text_align="center"),
        rx.table.cell(p_data.total_revenue_cop, text_align="right"),
        rx.table.cell(p_data.total_profit_cop, text_align="right", weight="bold"),
        rx.table.cell(
            rx.button(
                rx.icon("eye"),
                size="2",
                on_click=AppState.show_product_detail(p_data.product_id),
                variant="soft"
            ),
            text_align="center"
        ),
        align="center",
    )

def product_detail_modal() -> rx.Component:
    """Modal para ver el detalle de un producto y sus variantes."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.dialog.title(AppState.selected_product_detail.title),
                rx.dialog.description("Análisis detallado de ventas por variante."),

                # Resumen del producto en el modal
                rx.hstack(
                    rx.image(
                        src=AppState.selected_product_detail.image_url,
                        height="80px",
                        width="80px",
                        object_fit="cover",
                        border_radius="lg",
                        fallback_src="/placeholder.png"
                    ),
                    rx.vstack(
                        rx.text(f"Unidades Totales Vendidas: {AppState.selected_product_detail.total_units_sold}"),
                        rx.text(f"Ingresos Totales: {AppState.selected_product_detail.total_revenue_cop}"),
                        rx.text(f"Ganancia Total: {AppState.selected_product_detail.total_profit_cop}", weight="bold"),
                        align_items="start",
                    ),
                    spacing="4",
                    align="center",
                    width="100%",
                    padding_bottom="1em",
                    border_bottom="1px solid var(--gray-4)"
                ),

                # Selector de variantes
                rx.text("Selecciona una variante:", size="3", weight="bold"),
                rx.scroll_area(
                    rx.hstack(
                        rx.foreach(
                            AppState.selected_product_detail.variants,
                            lambda variant_data, index: rx.card(
                                rx.vstack(
                                    rx.image(
                                        src=variant_data.image_url,
                                        height="60px",
                                        width="60px",
                                        object_fit="cover",
                                        border_radius="md",
                                        fallback_src="/placeholder.png"
                                    ),
                                    rx.text(variant_data.attributes_str, size="1"),
                                    align_items="center",
                                ),
                                on_click=AppState.select_variant_for_detail(index),
                                cursor="pointer",
                                border=rx.cond(
                                    AppState.selected_variant_index == index,
                                    "2px solid var(--violet-9)",
                                    "2px solid transparent"
                                ),
                                transition="all 0.2s ease-in-out",
                                padding="2",
                                min_width="90px",
                            )
                        ),
                        spacing="3",
                        padding_y="1",
                    ),
                    type="always",
                    scrollbars="horizontal",
                    size="2",
                    style={"width": "100%", "paddingBottom": "1em"}
                ),


                # Detalle de la variante seleccionada (imagen, datos, gráfico)
                rx.cond(
                    AppState.selected_variant_detail,
                    rx.vstack(
                        rx.hstack(
                            rx.image(
                                src=AppState.selected_variant_detail.image_url,
                                height="80px",
                                width="80px",
                                object_fit="cover",
                                border_radius="lg",
                                fallback_src="/placeholder.png"
                            ),
                            rx.vstack(
                                rx.text(f"Atributos: {AppState.selected_variant_detail.attributes_str}", weight="bold"),
                                rx.text(f"Unidades Vendidas: {AppState.selected_variant_detail.units_sold}"),
                                rx.text(f"Ingresos: {AppState.selected_variant_detail.total_revenue_cop}"),
                                rx.text(f"Ganancia: {AppState.selected_variant_detail.total_profit_cop}", weight="bold"),
                                align_items="start",
                            ),
                            spacing="4",
                            align="center",
                            width="100%",
                            padding_y="1em",
                        ),
                        rx.card( # Gráfico de la variante dentro de una tarjeta
                            rx.vstack(
                                rx.heading("Ganancia de la Variante (Últimos Días)", size="4"),
                                rx.cond(
                                    AppState.product_detail_chart_data,
                                    ResponsiveContainer.create(
                                        LineChart.create(
                                            CartesianGrid.create(stroke_dasharray="3 3", stroke=rx.color("gray", 6)),
                                            XAxis.create(data_key="date", stroke=rx.color("gray", 9)),
                                            YAxis.create(stroke=rx.color("gray", 9)),
                                            tooltip(
                                                content_style={"backgroundColor": "var(--gray-2)", "border": "1px solid var(--gray-5)"}
                                            ),
                                            Legend.create(),
                                            Line.create(type="monotone", data_key="Ganancia", stroke="var(--teal-9)", stroke_width=2, dot=False),
                                            data=AppState.product_detail_chart_data,
                                            margin={"top": 10, "right": 30, "left": 0, "bottom": 0},
                                        ),
                                        aspect=2, # Proporción para la gráfica de variante
                                    ),
                                    rx.text("No hay datos de ganancias para esta variante.", color_scheme="gray")
                                ),
                                align_items="start",
                                width="100%",
                                padding="1em",
                            ),
                            width="100%"
                        ),
                        spacing="4",
                        width="100%",
                        border_top="1px solid var(--gray-4)",
                        padding_top="1em"
                    ),
                    rx.text("Selecciona una variante para ver los detalles.", color_scheme="gray")
                ),

                rx.dialog.close(
                    rx.button("Cerrar", on_click=AppState.close_product_detail_modal, variant="soft", color_scheme="red"),
                ),
                align_items="start",
                spacing="5",
                width="100%",
            ),
            padding="1.5em",
            max_width="700px", # Limita el ancho del modal
            width="100%",
        ),
        open=AppState.show_product_detail_modal,
        on_open_change=AppState.set_show_product_detail_modal,
    )

@require_admin
def finance_page_content() -> rx.Component:
    """Página del dashboard financiero."""
    return rx.center(
        rx.vstack(
            rx.heading("Dashboard Financiero", size="8", margin_bottom="1.5em"),
            rx.cond(
                AppState.is_loading,
                rx.center(rx.spinner(size="3"), height="70vh"),
                rx.vstack(
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
                        height="auto", # Ajuste para que las tarjetas se adapten mejor
                    ),
                    
                    general_finance_chart(), # Gráfico general

                    rx.card( # Tabla de productos
                        rx.vstack(
                            rx.heading("Rendimiento por Producto", size="5", margin_bottom="1em"),
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
                                        rx.table.column_header_cell("Acciones", text_align="center"), # Nueva columna para el botón
                                    )
                                ),
                                rx.table.body(
                                    rx.cond(
                                        AppState.filtered_product_finance_data,
                                        rx.foreach(AppState.filtered_product_finance_data, product_finance_table_row),
                                        rx.table.row(rx.table.cell("No se encontraron datos de productos.", col_span=5, text_align="center"))
                                    )
                                ),
                                variant="surface",
                            ),
                            align_items="stretch",
                            spacing="4",
                            width="100%",
                        )
                    ),
                    spacing="6",
                    width="100%",
                )
            ),
            padding_x="2em",
            padding_bottom="2em",
            width="100%",
            max_width="1400px",
            align="center",
            spacing="5",
        ),
        min_height="85vh",
        width="100%", # Asegura que el centro ocupe todo el ancho disponible
    ),
    product_detail_modal() # Añadir el modal a la página