# likemodas/invoice/page.py (VERSIÓN CORREGIDA FINAL)

import reflex as rx
from ..state import AppState
from ..utils.formatting import format_to_cop

# Estilos específicos para la factura, incluyendo @media print
invoice_style = {
    "font_family": "Arial, sans-serif",
    "padding": "2em",
    "max_width": "800px",
    "margin": "auto",
    "border": "1px solid #ddd",
    "box_shadow": "0 0 10px rgba(0, 0, 0, 0.1)",
    "bg": "white",
    "color": "black",
    "@media print": {
        "body": {
            "-webkit-print-color-adjust": "exact",
        },
        ".no-print": {
            "display": "none !important",
        },
        "box_shadow": "none",
        "border": "none",
    },
}

def invoice_page_content() -> rx.Component:
    """Página que renderiza una factura lista para imprimir."""
    return rx.box(
        rx.cond(
            AppState.invoice_data,
            # Contenido que se muestra si la factura tiene datos
            rx.vstack(
                # --- Encabezado ---
                rx.hstack(
                    rx.image(src="/logo.png", width="120px", height="auto"),
                    rx.spacer(),
                    rx.vstack(
                        rx.heading("FACTURA", size="8"),
                        # --- ⬇️ CORRECCIÓN APLICADA AQUÍ ⬇️ ---
                        # Se pasa el texto y la variable como argumentos separados.
                        # Reflex se encarga de unirlos correctamente.
                        rx.text("#", AppState.invoice_data.id),
                        align_items="end",
                    ),
                    width="100%",
                    align_items="start",
                    margin_bottom="2em",
                ),
                # --- Remitente y Comprador ---
                rx.grid(
                    rx.vstack(
                        rx.heading("Remitente", size="4", margin_bottom="0.5em"),
                        rx.text("Likemodas Store"),
                        rx.text("Calle Falsa 123, Popayán, Cauca"),
                        rx.text("soporte@likemodas.com"),
                        align_items="start",
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.heading("Comprador", size="4", margin_bottom="0.5em"),
                        rx.text(AppState.invoice_data.customer_name, weight="bold"),
                        rx.text(AppState.invoice_data.shipping_full_address),
                        rx.text(AppState.invoice_data.customer_email),
                        align_items="start",
                        spacing="1",
                    ),
                    columns="2",
                    spacing="6",
                    width="100%",
                    margin_bottom="2em",
                ),
                # --- Tabla de Artículos ---
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Artículo"),
                            rx.table.column_header_cell("Cantidad", text_align="center"),
                            rx.table.column_header_cell("Precio Unitario", text_align="right"),
                            rx.table.column_header_cell("Total", text_align="right"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            AppState.invoice_data.items,
                            lambda item: rx.table.row(
                                rx.table.cell(item["name"]),
                                rx.table.cell(item["quantity"], text_align="center"),
                                rx.table.cell(format_to_cop(item["price"]), text_align="right"),
                                rx.table.cell(format_to_cop(item["price"] * item["quantity"]), text_align="right"),
                            )
                        )
                    ),
                    variant="striped",
                    width="100%",
                ),
                # --- Totales ---
                rx.vstack(
                    rx.hstack(
                        rx.text("Subtotal:", weight="bold"),
                        rx.spacer(),
                        rx.text(AppState.invoice_data.subtotal_cop),
                        width="100%",
                        max_width="300px",
                    ),
                    rx.hstack(
                        rx.heading("Total:", size="5"),
                        rx.spacer(),
                        rx.heading(AppState.invoice_data.total_price_cop, size="5"),
                        width="100%",
                        max_width="300px",
                    ),
                    align_items="end",
                    width="100%",
                    margin_top="2em",
                ),
                # --- Botón para imprimir (se oculta al imprimir) ---
                rx.button(
                    "Imprimir Factura",
                    on_click=rx.call_script("window.print()"),
                    class_name="no-print", # Clase para ocultarlo
                    margin_top="3em",
                ),
                align="center",
            ),
            # Pantalla de carga mientras se obtienen los datos
            rx.center(rx.spinner(size="3"), rx.text("Cargando factura..."), height="90vh"),
        ),
        style=invoice_style,
    )