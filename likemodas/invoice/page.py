# likemodas/invoice/page.py (VERSIÓN DE PRUEBA MÍNIMA)
import reflex as rx
from ..state import AppState

def invoice_page_content() -> rx.Component:
    """Página de prueba para aislar el error de la factura."""
    return rx.box(
        rx.cond(
            AppState.invoice_data,
            rx.vstack(
                rx.heading("Prueba de Factura - Datos Cargados"),
                rx.text("Intentando iterar sobre los artículos..."),
                rx.table.root(
                    rx.table.body(
                        # Aquí solo mostramos texto simple, sin usar ninguna variable
                        rx.foreach(
                            AppState.invoice_data.items,
                            lambda item: rx.table.row(
                                rx.table.cell("Fila de prueba - Artículo OK")
                            )
                        )
                    )
                ),
                rx.text("Prueba finalizada."),
            ),
            # Pantalla de carga
            rx.center(
                rx.spinner(size="3"), 
                rx.text("Cargando datos de factura para la prueba..."), 
                height="90vh"
            ),
        )
    )