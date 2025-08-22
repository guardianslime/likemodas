# likemodas/purchases/page.py (VERSIÓN CON COMPONENTE AUXILIAR)
import reflex as rx
import reflex_local_auth
from ..state import AppState, UserPurchaseHistoryCardData, PurchaseHistoryItemData
from ..account.layout import account_layout
from ..models import PurchaseStatus
from ..blog.public_page import product_detail_modal

def purchase_item_card(item: PurchaseHistoryItemData) -> rx.Component:
    """
    Una tarjeta visual para un solo artículo comprado. (Esta función no cambia)
    """
    return rx.box(
        rx.vstack(
            rx.box(
                rx.cond(
                    item.image_url != "",
                    rx.image(
                        src=rx.get_upload_url(item.image_url), 
                        width="100%", 
                        height="130px", 
                        object_fit="cover"
                    ),
                    rx.box(
                        rx.icon("image_off", size=32), 
                        width="100%", 
                        height="130px", 
                        bg=rx.color("gray", 3), 
                        display="flex", 
                        align_items="center", 
                        justify_content="center"
                    )
                ),
                height="130px",
                width="100%",
                border_radius="md",
                overflow="hidden"
            ),
            rx.vstack(
                rx.text(item.title, weight="bold", size="3", no_of_lines=1, title=item.title),
                rx.text(f"Cantidad: {item.quantity}", size="2"),
                rx.text(
                    "Precio pagado: ",
                    rx.text.strong(item.price_at_purchase_cop),
                    size="2"
                ),
                spacing="1",
                align_items="start",
                width="100%",
                padding_x="0.2em"
            ),
            spacing="2",
            align_items="stretch"
        ),
        on_click=lambda: AppState.open_product_detail_modal(item.id),
        cursor="pointer",
        padding="0.5em",
        border_radius="lg",
        border="1px solid",
        border_color=rx.color("gray", 6),
        width="180px",
        _hover={"box_shadow": "0 0 10px rgba(128, 128, 128, 0.5)", "transform": "scale(1.03)"},
        transition="all 0.2s ease-in-out",
    )

# --- NUEVO COMPONENTE AUXILIAR ---
# Esta función toma la lista de artículos y la renderiza, aislando el foreach.
def purchase_items_gallery(items: rx.Var[list[PurchaseHistoryItemData]]) -> rx.Component:
    """Renderiza la galería de miniaturas de los artículos comprados."""
    return rx.vstack(
        rx.text("Artículos Comprados:", weight="medium", size="4"),
        rx.flex(
            rx.foreach(items, purchase_item_card),
            spacing="4",
            wrap="wrap",
            padding_y="0.5em",
        ),
        align_items="start",
        width="100%",
    )


@reflex_local_auth.require_login
def purchase_history_content() -> rx.Component:
    """
    Página del historial de compras del usuario, con miniaturas y modales.
    """
    page_content = rx.center(
        rx.vstack(
            rx.heading("Mi Historial de Compras", size="7"),
            rx.text("Aquí puedes ver todas tus compras y los artículos que adquiriste."),
            rx.input(
                placeholder="Buscar por ID de compra...",
                value=AppState.search_query_user_history,
                on_change=AppState.set_search_query_user_history,
                width="100%", max_width="400px", margin_y="1.5em",
            ),
            
            rx.cond(
                AppState.filtered_user_purchases,
                rx.foreach(
                    AppState.filtered_user_purchases, 
                    lambda purchase: rx.card(
                        rx.vstack(
                            # Encabezado (sin cambios)
                            rx.hstack(
                                rx.vstack(
                                    rx.text(f"Compra del: {purchase.purchase_date_formatted}", weight="bold", size="5"),
                                    rx.text(f"ID de Compra: #{purchase.id}", size="2", color_scheme="gray"),
                                    align_items="start",
                                ),
                                rx.spacer(),
                                rx.badge(purchase.status, color_scheme="blue", variant="soft", size="2"),
                                justify="between",
                                width="100%",
                            ),
                            rx.divider(),
                            
                            # Detalles de envío (sin cambios)
                            rx.vstack(
                                rx.text("Detalles de Envío:", weight="medium", size="4"),
                                rx.text(f"Nombre: {purchase.shipping_name}", size="3"),
                                rx.text(f"Dirección: {purchase.shipping_address}, {purchase.shipping_neighborhood}, {purchase.shipping_city}", size="3"),
                                rx.text(f"Teléfono: {purchase.shipping_phone}", size="3"),
                                spacing="1", align_items="start", width="100%",
                            ),
                            rx.divider(),
                            
                            # --- CAMBIO CLAVE AQUÍ ---
                            # En lugar de poner el rx.flex y rx.foreach aquí, llamamos a nuestro nuevo componente auxiliar.
                            purchase_items_gallery(items=purchase.items),
                            
                            rx.divider(),
                            # Total de la compra (sin cambios)
                            rx.hstack(
                                rx.spacer(),
                                rx.heading("Total de la Compra:", size="5", weight="medium"),
                                rx.heading(purchase.total_price_cop, size="6"),
                                justify="end",
                                width="100%",
                                padding_top="0.5em",
                            ),
                            
                            # Botón de factura (sin cambios)
                            rx.cond(
                                purchase.status != PurchaseStatus.PENDING.value,
                                rx.link(
                                    rx.button("Imprimir Factura", variant="outline", width="100%", margin_top="1em"),
                                    href=f"/invoice?id={purchase.id}",
                                    is_external=False,
                                    target="_blank",
                                ),
                            ),
                            spacing="4", width="100%"
                        ),
                        width="100%", padding="1.5em",
                    )
                ),
                rx.center(
                    rx.text("No se encontraron compras para tu búsqueda."),
                    padding_y="2em",
                )
            ),
            
            product_detail_modal(),
            
            spacing="6", width="100%", max_width="960px", align="center"
        ),
        width="100%"
    )
    return account_layout(page_content)
