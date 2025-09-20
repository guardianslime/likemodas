# Ruta: likemodas/admin/store_page.py
import reflex as rx
from ..auth.admin_auth import require_admin
from ..ui.components import product_gallery_component
from ..blog.public_page import product_detail_modal
from ..state import AppState
from ..ui.qr_scanner import qr_scanner_component
from .store_components import sliding_direct_sale_cart # <-- Importamos el carrito desde su nueva ubicación

@require_admin
def admin_store_page() -> rx.Component:
    """Página de Tienda para el administrador, incluyendo el activador del escáner QR."""
    main_content = rx.vstack(
        rx.vstack(
            rx.heading("Tienda (Punto de Venta)", size="8"),
            rx.text("Busca productos y añádelos al carrito de Venta Directa."),
            rx.hstack(
                rx.input(
                    placeholder="Buscar productos por nombre...",
                    value=AppState.search_term,
                    on_change=AppState.set_search_term,
                    width="100%",
                    max_width="500px",
                    variant="surface",
                    color_scheme="violet"
                ),
                rx.icon_button(
                    rx.icon(tag="qr-code", size=24),
                    on_click=AppState.toggle_qr_scanner_modal,
                    color_scheme="violet",
                    variant="soft",
                    size="3"
                ),
                spacing="3",
                align="center",
                width="100%",
                max_width="560px",
                margin_y="1.5em",
            ),
            align="center",
            width="100%",
            spacing="4",
        ),
        rx.cond(
            AppState.filtered_admin_store_posts,
            product_gallery_component(posts=AppState.filtered_admin_store_posts),
            rx.center(
                rx.text("No se encontraron productos."), 
                padding="4em", 
                width="100%"
            )
        ),
        width="100%",
        spacing="5"
    )

    return rx.fragment(
        rx.box(
            main_content,
            padding="2em",
        ),
        product_detail_modal(is_for_direct_sale=True),
        sliding_direct_sale_cart(),

        # --- MODAL DE ESCANEO QR ---
        rx.dialog.root(
            rx.dialog.content(
                rx.dialog.title("Escanear Código QR del Producto"),
                rx.dialog.description(
                    "Apunta la cámara al código QR o sube una imagen para añadir el producto a la venta."
                ),
                qr_scanner_component(
                    on_scan_success=AppState.handle_qr_scan_result,
                    fps=10,
                    qrbox=250,
                    verbose=False
                ),
                rx.flex(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray")
                    ),
                    spacing="3",
                    margin_top="1em",
                    justify="end",
                ),
            ),
            open=AppState.show_qr_scanner_modal,
            on_open_change=AppState.set_show_qr_scanner_modal,
        )
    )