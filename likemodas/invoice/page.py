# likemodas/invoice/page.py (VERSIÓN FINAL CON DETALLES DE VARIANTE)
import reflex as rx
from .state import InvoiceState

invoice_style = {
    "font_family": "Arial, sans-serif", "padding": "2em", "max_width": "800px", "margin": "auto",
    "border": "1px solid #ddd", "box_shadow": "0 0 10px rgba(0, 0, 0, 0.1)",
    "bg": "white", "color": "black",
    "@media print": {
        ".no-print": {"display": "none !important"}, "box_shadow": "none", "border": "none",
    },
}

def invoice_page_content() -> rx.Component:
    """Página que renderiza una factura con detalles de variante específicos."""
    return rx.box(
        rx.cond(
            InvoiceState.invoice_data,
            rx.vstack(
                rx.hstack(
                    rx.image(src="/logo.png", width="120px", height="auto"),
                    rx.spacer(),
                    rx.vstack(
                        rx.heading("FACTURA", size="6", weight="bold"),
                        rx.text("#", InvoiceState.invoice_data.id),
                        align_items="end",
                    ),
                    width="100%", align_items="start", margin_bottom="1em",
                ),
                rx.hstack(
                    rx.text(
                        "Fecha de Emisión: ",
                        rx.text.strong(InvoiceState.invoice_data.purchase_date_formatted),
                        font_size="0.9em",
                    ),
                    rx.spacer(),
                    width="100%",
                    margin_bottom="2em",
                ),
                rx.grid(
                    rx.vstack(
                        rx.heading("Remitente", size="4"), rx.text("Likemodas Store"),
                        rx.text("Calle 17 #5-40 Los Sauces, Popayán, Cauca"),
                        rx.text("soporte@likemodas.com"),
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
                            rx.table.column_header_cell("Artículo", style={"color": "black"}),
                            rx.table.column_header_cell("Cantidad", text_align="center", style={"color": "black"}),
                            rx.table.column_header_cell("Precio Unitario", text_align="right", style={"color": "black"}),
                            rx.table.column_header_cell("Subtotal", text_align="right", style={"color": "black"}),
                            rx.table.column_header_cell("IVA (19%)", text_align="right", style={"color": "black"}),
                            rx.table.column_header_cell("Total", text_align="right", style={"color": "black"}),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            InvoiceState.invoice_items,
                            lambda item: rx.table.row(
                                # --- ✨ INICIO DE LA MODIFICACIÓN ✨ ---
                                rx.table.cell(
                                    rx.vstack(
                                        rx.text(item.name, weight="bold", style={"color": "black"}),
                                        rx.text(item.variant_details_str, size="2", color_scheme="gray"),
                                        align_items="start", spacing="0"
                                    )
                                ),
                                # --- ✨ FIN DE LA MODIFICACIÓN ✨ ---
                                rx.table.cell(item.quantity, text_align="center", style={"color": "black"}),
                                rx.table.cell(item.price_cop, text_align="right", style={"color": "black"}),
                                rx.table.cell(item.subtotal_cop, text_align="right", style={"color": "black"}),
                                rx.table.cell(item.iva_cop, text_align="right", style={"color": "black"}),
                                rx.table.cell(item.total_con_iva_cop, text_align="right", style={"color": "black"}),
                            )
                        )
                    ),
                    variant="surface",
                    width="100%",
                ),
                rx.hstack(
                    rx.spacer(),
                    rx.vstack(
                        rx.hstack(
                            rx.text("Subtotal:", weight="bold", width="120px", text_align="right"),
                            rx.text(InvoiceState.invoice_data.subtotal_cop, width="120px", text_align="right"),
                            justify="between", width="100%"
                        ),
                        rx.hstack(
                            rx.text("Envío:", weight="bold", width="120px", text_align="right"),
                            rx.text(InvoiceState.invoice_data.shipping_applied_cop, width="120px", text_align="right"),
                            justify="between", width="100%"
                        ),
                        rx.hstack(
                            rx.text("IVA (19%):", weight="bold", width="120px", text_align="right"),
                            rx.text(InvoiceState.invoice_data.iva_cop, width="120px", text_align="right"),
                            justify="between", width="100%"
                        ),
                        rx.divider(width="100%"),
                        rx.hstack(
                            rx.heading("Total:", size="5", width="120px", text_align="right"),
                            rx.heading(InvoiceState.invoice_data.total_price_cop, size="5", width="120px", text_align="right"),
                            justify="between", width="100%"
                        ),
                        spacing="2",
                        margin_top="1.5em",
                        padding="1em",
                        border="1px solid #ddd",
                        border_radius="md",
                        min_width="300px",
                    ),
                    width="100%",
                    justify="end",
                ),
                rx.button(
                    "Imprimir Factura", on_click=rx.call_script("window.print()"),
                    class_name="no-print", margin_top="3em",
                ),
                align="stretch",
                spacing="5",
            ),
            rx.center(rx.spinner(size="3"), rx.text("Cargando factura..."), height="90vh"),
        ),
        style=invoice_style,
    )