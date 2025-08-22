# likemodas/invoice/page.py (VERSIÓN CORREGIDA)
import reflex as rx
from .state import InvoiceState # <-- Importamos el nuevo estado

# Estilos (sin cambios)
invoice_style = {
    "font_family": "Arial, sans-serif", "padding": "2em", "max_width": "800px", "margin": "auto",
    "border": "1px solid #ddd", "box_shadow": "0 0 10px rgba(0, 0, 0, 0.1)",
    "bg": "white", "color": "black",
    "@media print": {
        ".no-print": {"display": "none !important"}, "box_shadow": "none", "border": "none",
    },
}

def invoice_page_content() -> rx.Component:
    """Página que renderiza una factura usando su propio estado."""
    return rx.box(
        rx.cond(
            InvoiceState.invoice_data,
            rx.vstack(
                rx.hstack(
                    rx.image(src="/logo.png", width="120px", height="auto"),
                    rx.spacer(),
                    rx.vstack(
                        rx.heading("FACTURA", size="8"),
                        rx.text("#", InvoiceState.invoice_data.id),
                        align_items="end",
                    ),
                    width="100%", align_items="start", margin_bottom="2em",
                ),
                rx.grid(
                    rx.vstack(
                        rx.heading("Remitente", size="4"), rx.text("Likemodas Store"),
                        rx.text("Calle Falsa 123, Popayán, Cauca"), rx.text("soporte@likemodas.com"),
                        align_items="start", spacing="1",
                    ),
                    rx.vstack(
                        rx.heading("Comprador", size="4"),
                        rx.text(InvoiceState.invoice_data.customer_name, weight="bold"),
                        rx.text(InvoiceState.invoice_data.shipping_full_address),
                        rx.text(InvoiceState.invoice_data.customer_email),
                        align_items="start", spacing="1",
                    ),
                    columns="2", spacing="6", width="100%", margin_bottom="2em",
                ),
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
                            InvoiceState.invoice_items, # <-- LÍNEA CORREGIDA Y SEGURA
                            lambda item: rx.table.row(
                                rx.table.cell(item.name),
                                rx.table.cell(item.quantity, text_align="center"),
                                rx.table.cell(item.price_cop, text_align="right"),
                                rx.table.cell(item.total_cop, text_align="right"),
                            )
                        )
                    ),
                    variant="surface", width="100%", # <-- CORRECCIÓN FINAL AQUÍ
                ),
                rx.vstack(
                    rx.hstack(rx.text("Subtotal:", weight="bold"), rx.spacer(), rx.text(InvoiceState.invoice_data.subtotal_cop)),
                    rx.hstack(rx.heading("Total:", size="5"), rx.spacer(), rx.heading(InvoiceState.invoice_data.total_price_cop, size="5")),
                    align_items="end", width="100%", margin_top="2em", max_width="300px",
                ),
                rx.button(
                    "Imprimir Factura", on_click=rx.call_script("window.print()"),
                    class_name="no-print", margin_top="3em",
                ),
                align="center",
            ),
            rx.center(rx.spinner(size="3"), rx.text("Cargando factura..."), height="90vh"),
        ),
        style=invoice_style,
    )