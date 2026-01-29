# likemodas/admin/page.py (VERSIÓN FINAL CON AUDITORÍA)

import reflex as rx
from ..state import AppState, AdminPurchaseCardData, PurchaseItemCardData, format_to_cop
from ..models import PurchaseStatus
from ..auth.admin_auth import require_panel_access
# ✨ IMPORTA EL MODAL AQUÍ ✨
from ..blog.public_page import product_detail_modal

# ... (purchase_item_display_admin y purchase_items_view no cambian) ...
def purchase_item_display_admin(item: PurchaseItemCardData) -> rx.Component:
    """Muestra un item individual y abre el modal del producto al hacer clic en la imagen."""
    return rx.hstack(
        # ✨ INICIO DE LA CORRECCIÓN ✨
        rx.box(
            rx.image(
                src=rx.get_upload_url(item.image_url),
                alt=item.title,
                width="60px",
                height="60px",
                object_fit="cover",
                border_radius="sm",
            ),
            # Se añade el evento on_click para abrir el modal
            on_click=AppState.open_product_detail_modal(item.id),
            cursor="pointer",
            _hover={"opacity": 0.8},
            transition="opacity 0.2s"
        ),
        # ✨ FIN DE LA CORRECCIÓN ✨
        rx.vstack(
            rx.text(item.title, weight="bold", size="3"),
            rx.text(item.variant_details_str, size="2", color_scheme="gray"),
            align_items="start",
            spacing="0",
        ),
        rx.spacer(),
        rx.text(
            item.quantity.to_string(), "x ", item.price_at_purchase_cop,
            size="3"
        ),
        spacing="3",
        align="center",
        width="100%",
    )


def purchase_items_view(purchase_id: rx.Var[int], map_var: rx.Var[dict]) -> rx.Component:
    """Renderiza la lista de artículos para una compra específica."""
    return rx.vstack(
        rx.foreach(
            map_var.get(purchase_id, []), 
            purchase_item_display_admin
        ),
        spacing="2",
        width="100%",
    )

# --- ✨ INICIO: COMPONENTES DE COMPRA CORREGIDOS CON AUDITORÍA ✨ ---
def purchase_card_admin(purchase: AdminPurchaseCardData) -> rx.Component:
    """Tarjeta de pedido para el panel de administración."""
    
    # Formulario de Envío (Guía vs Manual)
    set_delivery_and_shipping_form = rx.tabs.root(
        rx.tabs.list(
            rx.tabs.trigger("Guía Nacional", value="guide"),
            rx.tabs.trigger("Entrega Manual", value="manual"),
        ),
        rx.tabs.content(
            rx.vstack(
                rx.text("Empresa de Envíos:", size="2", weight="bold"),
                rx.select(["Servientrega", "Interrapidísimo", "Coordinadora", "Envia", "Deprisa"], placeholder="Selecciona empresa", default_value="Servientrega", on_change=lambda val: AppState.set_admin_tracking_carrier(purchase.id, val), width="100%"),
                rx.text("Número de Guía:", size="2", weight="bold"),
                rx.input(placeholder="Ej: 2050123...", on_change=lambda val: AppState.set_admin_tracking_guide(purchase.id, val), width="100%"),
                rx.button("Confirmar Envío con Guía", on_click=lambda: AppState.ship_order_with_guide(purchase.id), color_scheme="violet", width="100%", margin_top="1em"),
                spacing="3", padding="1em", border="1px solid #EAEAEA", border_radius="0 0 8px 8px"
            ),
            value="guide"
        ),
        rx.tabs.content(
            rx.vstack(
                rx.text("Tiempo estimado de entrega:", size="2", weight="bold"),
                rx.hstack(
                    rx.input(placeholder="Días", type="number", on_change=lambda val: AppState.set_admin_delivery_time(purchase.id, "days", val)),
                    rx.input(placeholder="Horas", type="number", on_change=lambda val: AppState.set_admin_delivery_time(purchase.id, "hours", val)),
                    rx.input(placeholder="Min", type="number", on_change=lambda val: AppState.set_admin_delivery_time(purchase.id, "minutes", val)),
                    spacing="2", width="100%",
                ),
                rx.text("Costo Final (Opcional):", size="2", weight="bold"),
                rx.input(placeholder=f"Inicial: {purchase.shipping_applied_cop}", type="number", on_change=lambda val: AppState.set_admin_final_shipping_cost(purchase.id, val)),
                rx.button("Confirmar Entrega Manual", on_click=lambda: AppState.confirm_delivery_time(purchase.id), color_scheme="gray", width="100%", margin_top="1em"),
                spacing="3", padding="1em", border="1px solid #EAEAEA", border_radius="0 0 8px 8px"
            ),
            value="manual"
        ),
        default_value="guide", width="100%", margin_top="1em"
    )

    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(f"Compra #{purchase.id}", weight="bold", size="5"),
                    rx.text(f"Cliente: {purchase.customer_name}", size="2"),
                    rx.text(purchase.purchase_date_formatted, size="1", color_scheme="gray"),
                    align_items="start", spacing="1"
                ),
                rx.spacer(),
                rx.badge(purchase.status, color_scheme=rx.cond(purchase.status == "confirmed", "blue", "green")),
                width="100%", align_items="start"
            ),
            rx.divider(),
            rx.foreach(purchase.items, purchase_item_display_admin),
            rx.divider(),
            rx.vstack(
                rx.text("Datos de Envío:", weight="bold", size="2"),
                rx.text(rx.cond(purchase.shipping_name, purchase.shipping_name, "N/A"), size="2"),
                rx.text(rx.cond(purchase.shipping_full_address, purchase.shipping_full_address, "N/A"), size="2"),
                rx.text(rx.cond(purchase.shipping_phone, purchase.shipping_phone, "N/A"), size="2"),
                spacing="1", width="100%", bg="gray.50", padding="0.5em", border_radius="md"
            ),
            
            # --- FORMULARIO DE ENVÍO (Solo si está confirmado o pendiente) ---
            rx.cond(
                (purchase.status == PurchaseStatus.CONFIRMED.value) | (purchase.status == PurchaseStatus.PENDING_CONFIRMATION.value),
                set_delivery_and_shipping_form
            ),

            # --- GESTIÓN DE PAGO (CORREGIDO PARA MANUAL) ---
            # Aparece si es Venta Directa O si es Envío Manual
            rx.cond(
                ((purchase.is_direct_sale) | (purchase.shipping_type == "manual")) & 
                ((purchase.status == PurchaseStatus.SHIPPED.value) | (purchase.status == PurchaseStatus.DELIVERED.value)),
                rx.vstack(
                    rx.divider(),
                    rx.text("Gestión de Pago (Contra Entrega / Manual)", weight="bold", color_scheme="orange"),
                    rx.text("Confirma cuando hayas recibido el dinero.", size="2"),
                    rx.button(
                        "CONFIRMAR PAGO RECIBIDO",
                        on_click=AppState.confirm_direct_payment(purchase.id),
                        color_scheme="green", width="100%", size="3"
                    ),
                    spacing="3", width="100%", padding="1em", bg="orange.50", border_radius="md"
                )
            ),
            spacing="4", width="100%"
        ),
        width="100%", box_shadow="lg"
    )

def purchase_card_history(purchase: AdminPurchaseCardData) -> rx.Component:
    """
    [CORRECCIÓN DEFINITIVA] Muestra los detalles de una compra en el historial, 
    con desglose completo de costos y formato seguro.
    """
    
    # Calculamos el subtotal aquí de forma segura para el frontend
    subtotal_var = purchase.total_price - rx.cond(
        purchase.shipping_applied, purchase.shipping_applied, 0.0
    )

    return rx.card(
        rx.vstack(
            # --- Encabezado (ID, Cliente, Fecha) ---
            rx.hstack(
                rx.vstack(
                    rx.text(f"Compra #{purchase.id}", weight="bold", size="5"),
                    rx.text(f"Cliente: {purchase.customer_name} ({purchase.customer_email})", size="3"),
                    rx.text(f"Fecha: {purchase.purchase_date_formatted}", size="3"),
                    align_items="start",
                ),
                rx.spacer(),
                rx.vstack(
                    rx.badge(purchase.status, color_scheme="green", variant="soft", size="2"),
                    # ✨ CORRECCIÓN APLICADA: Usar la propiedad pre-calculada 'total_price_cop'
                    rx.heading(purchase.total_price_cop, size="6"), 
                    align_items="end",
                ), width="100%",
            ),
            rx.divider(),
            
            # --- Detalles de Envío ---
            rx.vstack(
                rx.text("Detalles de Envío:", weight="medium", size="4"),
                rx.text(f"Nombre: {purchase.shipping_name}", size="3"),
                rx.text(f"Dirección: {purchase.shipping_full_address}", size="3"),
                rx.text(f"Teléfono: {purchase.shipping_phone}", size="3"),
                spacing="1", align_items="start", width="100%",
            ),
            rx.divider(),

            # --- Artículos ---
            rx.vstack(
                rx.text("Artículos:", weight="medium", size="4"),
                purchase_items_view(
                    purchase_id=purchase.id,
                    map_var=AppState.purchase_history_items_map
                ),
                spacing="2", align_items="start", width="100%",
            ),

            # --- ✨ SECCIÓN DE TOTALES CORREGIDA Y COMPLETA ✨ ---
            rx.divider(margin_y="0.75em"),
            rx.vstack(
                rx.hstack(
                    rx.text("Subtotal:", size="3", color_scheme="gray"),
                    rx.spacer(),
                    # El DTO ya tiene este valor formateado por el backend
                    rx.text(purchase.subtotal_cop, size="3"),
                ),
                rx.hstack(
                    rx.text("Envío:", size="3", color_scheme="gray"), 
                    rx.spacer(),
                    # El DTO ya tiene este valor formateado por el backend
                    rx.text(purchase.shipping_applied_cop, size="3"),
                ),
                rx.hstack(
                    rx.text("IVA (19%):", size="3", color_scheme="gray"),
                    rx.spacer(),
                    rx.text(purchase.iva_cop, size="3"), # Este ya venía formateado del DTO
                ),
                rx.divider(border_style="dashed"),
                rx.hstack(
                    rx.text("Total Pagado:", weight="bold", size="4"),
                    rx.spacer(),
                    # El DTO ya tiene este valor formateado por el backend
                    rx.text(purchase.total_price_cop, weight="bold", size="4"),
                ),
                spacing="2",
                align_items="stretch",
                width="100%",
                padding_y="0.5em",
            ),
            # --- ✨ FIN DE LA SECCIÓN DE TOTALES ✨ ---

            # --- Auditoría y Botón de Imprimir ---
            rx.cond(
                purchase.action_by_name,
                rx.box(
                    rx.hstack(
                        rx.icon("user-check", size=12, color_scheme="gray"),
                        rx.text(
                            "Venta procesada por: ",
                            rx.text.strong(purchase.action_by_name),
                            size="2", color_scheme="gray"
                        ),
                        spacing="2"
                    ),
                    width="100%", margin_y="0.5em",
                )
            ),
            rx.link(
                rx.button("Imprimir Factura", variant="soft", color_scheme="gray", width="100%", margin_top="0.5em"),
                href=f"/invoice?id={purchase.id}",
                target="_blank",
            ),
            spacing="4", width="100%",
        ), width="100%",
    )

@require_panel_access 
def admin_confirm_content() -> rx.Component:
    """Página de admin para gestionar órdenes activas."""
    page_content = rx.center(
        rx.vstack(
            rx.heading("Gestionar Órdenes Activas", size="8"),
            rx.cond(
                AppState.active_purchases,
                rx.foreach(AppState.active_purchases, purchase_card_admin),
                rx.center(rx.text("No hay compras activas para gestionar."), padding_y="2em")
            ),
            align="center", spacing="5", padding="2em", width="100%", max_width="960px", 
        ), width="100%"
    )
    
    # ✨ CORRECCIÓN: Envolvemos la página en un fragmento y añadimos el modal ✨
    return rx.fragment(
        page_content,
        product_detail_modal(is_for_direct_sale=True)
    )


@require_panel_access 
def payment_history_content() -> rx.Component:
    """Página de admin para ver el historial de pagos."""
    page_content = rx.center(
        rx.vstack(
            rx.heading("Historial de Pagos", size="8"),
            rx.input(
                placeholder="Buscar por ID, cliente o email...",
                value=AppState.search_query_admin_history,
                on_change=AppState.set_search_query_admin_history,
                width="100%", max_width="400px", margin_y="1.5em",
            ),
            rx.cond(
                AppState.filtered_admin_purchases,
                rx.foreach(AppState.filtered_admin_purchases, purchase_card_history),
                rx.center(rx.text("No se encontró historial para la búsqueda."), padding_y="2em")
            ),
            align="center", spacing="6", padding="2em", width="100%", max_width="960px",
        ), width="100%"
    )
    
    # ✨ CORRECCIÓN: Hacemos lo mismo para la página de historial ✨
    return rx.fragment(
        page_content,
        product_detail_modal(is_for_direct_sale=True)
    )