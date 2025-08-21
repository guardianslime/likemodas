# likemodas/purchases/page.py (VERSIÓN FINAL CON FACTURA)

import reflex as rx
import reflex_local_auth
from ..state import AppState, UserPurchaseHistoryCardData
from ..account.layout import account_layout

def purchase_invoice_card(purchase: UserPurchaseHistoryCardData) -> rx.Component:
    """Componente que muestra el detalle de una compra como una factura."""
    return rx.box(
        rx.vstack(
            # --- Encabezado de la factura ---
            rx.hstack(
                rx.image(src="/logo.png", width="100px", height="auto"),
                rx.spacer(),
                rx.vstack(
                    rx.heading(f"Factura #{purchase.id}", size="6"),
                    rx.text(f"Compra del: {purchase.purchase_date_formatted}"),
                    rx.badge(purchase.status, color_scheme="blue", variant="soft", size="2"),
                    align_items="end",
                ),
                width="100%",
                padding_bottom="1em",
            ),
            rx.divider(),
            
            # --- Detalles de envío ---
            rx.grid(
                rx.vstack(
                    rx.heading("Vendido Por", size="4"),
                    rx.text("Likemodas"),
                    rx.text("ventas@likemodas.com"),
                    align_items="start",
                ),
                rx.vstack(
                    rx.heading("Facturado A", size="4"),
                    rx.text(purchase.shipping_name),
                    rx.text(f"{purchase.shipping_address}, {purchase.shipping_city}"),
                    align_items="start",
                ),
                columns="2", spacing="4", width="100%", padding_y="1em",
            ),
            rx.divider(),

            # --- Tabla de Artículos ---
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Producto"),
                        rx.table.column_header_cell("Cantidad"),
                        rx.table.column_header_cell("Precio Unit."),
                        rx.table.column_header_cell("Subtotal", text_align="right"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        purchase.items, # <-- Se accede directamente a la lista `items` de la variable
                        lambda item: rx.table.row(
                            rx.table.cell(item["title"]),
                            rx.table.cell(item["quantity"]),
                            rx.table.cell(item["price_cop"]),
                            rx.table.cell(item["subtotal_cop"], text_align="right"),
                        )
                    )
                ),
                variant="surface",
                width="100%",
            ),

            # --- Total y Botón de Descarga ---
            rx.hstack(
                rx.spacer(),
                rx.heading(f"Total: {purchase.total_price_cop}", size="6"),
                width="100%",
                padding_top="1em"
            ),
            rx.button(
                "Descargar Factura", 
                on_click=rx.download(f"/api/invoice/{purchase.id}"),
                width="100%", 
                margin_top="1em"
            ),

            spacing="4",
        ),
        border="1px solid",
        border_color=rx.color("gray", 6),
        border_radius="md",
        padding="1.5em",
        width="100%",
    )

@reflex_local_auth.require_login
def purchase_history_content() -> rx.Component:
    """Página del historial de compras del usuario."""
    page_content = rx.center(
        rx.vstack(
            rx.heading("Mi Historial de Compras", size="7"),
            rx.input(
                placeholder="Buscar por ID o producto...",
                value=AppState.search_query_user_history,
                on_change=AppState.set_search_query_user_history,
                width="100%", max_width="400px", margin_y="1.5em",
            ),
            rx.cond(
                AppState.filtered_user_purchases,
                rx.foreach(AppState.filtered_user_purchases, purchase_invoice_card), # Usa el nuevo componente
                rx.center(
                    rx.text("No se encontraron compras para tu búsqueda."),
                    padding_y="2em",
                )
            ),
            spacing="6", width="100%", max_width="960px", align="center"
        ),
        width="100%"
    )
    return account_layout(page_content)