# likemodas/admin/page.py (VERSIÓN FINAL Y DEFINITIVA)

import reflex as rx
from ..auth.admin_auth import require_admin
from ..state import AppState, AdminPurchaseCardData, PurchaseItemCardData
from ..models import PurchaseStatus


# --- COMPONENTE REUTILIZABLE PARA MOSTRAR ITEMS (SIN CAMBIOS) ---
def purchase_item_display_admin(item: PurchaseItemCardData) -> rx.Component:
    """Muestra un item individual detallado, reutilizable en ambas vistas."""
    return rx.hstack(
        rx.image(
            src=rx.get_upload_url(item.image_url),
            alt=item.title,
            width="60px",
            height="60px",
            object_fit="cover",
            border_radius="sm",
        ),
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


# --- ✨ INICIO DE LA SOLUCIÓN DEFINITIVA ✨ ---

# PASO 1: CREAR UN COMPONENTE AISLADO
# Este decorador le dice a Reflex que trate esta función como un componente independiente.
@rx.component
def purchase_items_view(purchase_id: rx.Var[int], map_var: rx.Var[dict]) -> rx.Component:
    """
    Componente aislado que renderiza la lista de artículos para una compra.
    Recibe el ID y el mapa de datos, rompiendo el anidamiento que causa el bug.
    """
    return rx.vstack(
        rx.foreach(
            map_var.get(purchase_id, []), 
            purchase_item_display_admin
        ),
        spacing="2",
        width="100%",
    )
# --- ✨ FIN DE LA SOLUCIÓN ✨ ---


def purchase_card_admin(purchase: AdminPurchaseCardData) -> rx.Component:
    """Muestra los detalles de una compra activa y sus acciones dinámicas."""
    set_delivery_and_shipping_form = rx.vstack(
        rx.divider(),
        rx.grid(
            rx.vstack(
                rx.text("Establecer tiempo de entrega:", size="3", weight="medium"),
                rx.hstack(
                    rx.input(placeholder="Días", type="number", on_change=lambda val: AppState.set_admin_delivery_time(purchase.id, "days", val)),
                    rx.input(placeholder="Horas", type="number", on_change=lambda val: AppState.set_admin_delivery_time(purchase.id, "hours", val)),
                    rx.input(placeholder="Minutos", type="number", on_change=lambda val: AppState.set_admin_delivery_time(purchase.id, "minutes", val)),
                    spacing="2", width="100%",
                ),
                spacing="2", align_items="start",
            ),
            rx.vstack(
                rx.text("Costo de Envío Final (Opcional):", size="3", weight="medium"),
                rx.input(
                    placeholder=f"Inicial: {purchase.shipping_applied_cop}",
                    type="number",
                    on_change=lambda val: AppState.set_admin_final_shipping_cost(purchase.id, val)
                ),
                rx.text("Si se deja en blanco, se usará el costo inicial.", size="1", color_scheme="gray"),
                spacing="2", align_items="start",
            ),
            columns="2", spacing="4", width="100%",
        ),
        width="100%", spacing="2", margin_top="1em"
    )

    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(f"Compra #{purchase.id}", weight="bold", size="5"),
                    rx.text(f"Cliente: {purchase.customer_name} ({purchase.customer_email})", size="3"),
                    rx.text(f"Fecha: {purchase.purchase_date_formatted}", size="3"),
                    align_items="start",
                ),
                rx.spacer(),
                rx.vstack(
                    rx.badge(purchase.status, color_scheme="blue", variant="soft", size="2"),
                    rx.heading(purchase.total_price_cop, size="6"),
                    align_items="end",
                ), width="100%",
            ),
            rx.divider(),
            
            rx.vstack(
                rx.text("Artículos:", weight="medium", size="4"),
                # --- ✨ PASO 2: USAR EL NUEVO COMPONENTE AISLADO ---
                purchase_items_view(
                    purchase_id=purchase.id, 
                    map_var=AppState.active_purchase_items_map
                ),
                spacing="2", align_items="start", width="100%", margin_bottom="1em"
            ),
            
            # La lógica de botones se mantiene sin cambios
            rx.cond(
                purchase.status == PurchaseStatus.PENDING_CONFIRMATION.value,
                rx.vstack(
                    set_delivery_and_shipping_form,
                    rx.button("Enviar y Notificar al Cliente", on_click=AppState.ship_pending_cod_order(purchase.id), width="100%", margin_top="0.5em"),
                )
            ),
            # ... (resto de los botones sin cambios) ...
            rx.cond(
                purchase.status == PurchaseStatus.CONFIRMED.value,
                rx.vstack(
                    set_delivery_and_shipping_form,
                    rx.button(
                        "Establecer Tiempo y Notificar Envío", 
                        on_click=AppState.ship_confirmed_online_order(purchase.id),
                        width="100%", margin_top="0.5em"
                    ),
                )
            ),
            rx.cond(
                (purchase.status == PurchaseStatus.SHIPPED.value) | (purchase.status == PurchaseStatus.DELIVERED.value),
                rx.cond(
                    purchase.payment_method == "Contra Entrega",
                    rx.cond(
                        ~purchase.confirmed_at,
                        rx.button(
                            "Confirmar Pago Recibido", 
                            on_click=AppState.confirm_cod_payment_received(purchase.id), 
                            color_scheme="green", width="100%", margin_top="1em"
                        ),
                        rx.callout(
                            "Pago Recibido. Esperando confirmación del cliente.", 
                            icon="check", color_scheme="green", width="100%", margin_top="1em"
                        )
                    ),
                    rx.callout("Envío notificado. Esperando confirmación del cliente.", icon="check", width="100%", margin_top="1em")
                )
            ),
            spacing="4", width="100%",
        ), width="100%",
    )


def purchase_card_history(purchase: AdminPurchaseCardData) -> rx.Component:
    """Muestra los detalles de una compra en el historial."""
    return rx.card(
        rx.vstack(
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
                    rx.heading(purchase.total_price_cop, size="6"),
                    align_items="end",
                ), width="100%",
            ),
            rx.divider(),
            rx.vstack(
                rx.text("Detalles de Envío:", weight="medium", size="4"),
                rx.text(f"Nombre: {purchase.shipping_name}", size="3"),
                rx.text(f"Dirección: {purchase.shipping_full_address}", size="3"),
                rx.text(f"Teléfono: {purchase.shipping_phone}", size="3"),
                spacing="1", align_items="start", width="100%",
            ),
            rx.divider(),
            rx.vstack(
                rx.text("Artículos:", weight="medium", size="4"),
                # --- ✨ PASO 3: APLICAR EL MISMO PATRÓN AL HISTORIAL POR CONSISTENCIA ---
                purchase_items_view(
                    purchase_id=purchase.id,
                    map_var=AppState.purchase_history_items_map
                ),
                spacing="2", align_items="start", width="100%",
            ),
            rx.link(
                rx.button("Imprimir Factura", variant="soft", color_scheme="gray", width="100%", margin_top="1em"),
                href=f"/invoice?id={purchase.id}",
                target="_blank",
            ),
            spacing="4", width="100%",
        ), width="100%",
    )


@require_admin
def admin_confirm_content() -> rx.Component:
    """Página de admin para gestionar órdenes activas."""
    return rx.center(
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


@require_admin
def payment_history_content() -> rx.Component:
    """Página de admin para ver el historial de pagos."""
    return rx.center(
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