# likemodas/pages/product.py (SOLUCIÓN DEFINITIVA PARA EL LAYOUT SHIFT)

import reflex as rx
from likemodas.state import ProductDetailState

def product_page() -> rx.Component:
    """
    Página de detalle con una estructura estable que evita los saltos de interfaz.
    """
    # Una variable para saber si la carga terminó y los datos existen.
    is_loaded_and_valid = ~ProductDetailState.is_loading & (ProductDetailState.product_detail is not None)

    return rx.container(
        rx.grid(
            # --- Columna de la Imagen ---
            # El esqueleto envuelve la imagen y le da una altura fija mientras carga.
            rx.skeleton(
                rx.image(
                    src=rx.get_upload_url(ProductDetailState.product_detail.image_urls[0]),
                    width="100%",
                    height="auto",
                    border_radius="md",
                ),
                is_loaded=is_loaded_and_valid,
                height="400px", # Altura fija para el esqueleto
                border_radius="md",
            ),
            
            # --- Columna de Información (Estructura Estable) ---
            rx.vstack(
                # Título
                rx.skeleton(
                    rx.heading(ProductDetailState.product_detail.title, size="8"),
                    is_loaded=is_loaded_and_valid,
                    height="38px", # Altura aproximada de un heading size="8"
                ),
                # Precio
                rx.skeleton(
                    rx.text(f"${ProductDetailState.product_detail.price:.0f} COP", size="6", color_scheme="gray", margin_y="1em"),
                    is_loaded=is_loaded_and_valid,
                    height="28px", # Altura aproximada de un text size="6"
                ),
                # Descripción
                rx.skeleton(
                    rx.text(ProductDetailState.product_detail.content, white_space="pre-wrap", no_of_lines=5),
                    is_loaded=is_loaded_and_valid,
                    height="105px", # Altura para 5 líneas de texto
                ),
                rx.spacer(),
                
                # ✨ EL BOTÓN A PRUEBA DE SALTOS ✨
                # El botón se renderiza siempre, pero se deshabilita mientras carga.
                # Su tamaño nunca cambia.
                rx.button(
                    "Añadir al Carrito",
                    on_click=lambda: ProductDetailState.add_to_cart(ProductDetailState.product_detail.id),
                    width="100%",
                    size="3",
                    margin_top="1em",
                    is_disabled=~is_loaded_and_valid, # Se deshabilita si está cargando o no hay datos
                ),
                align="start",
                height="100%",
            ),
            columns={"initial": "1", "md": "2"},
            spacing="6",
            width="100%",
        ),
        padding_top="8em",
    )