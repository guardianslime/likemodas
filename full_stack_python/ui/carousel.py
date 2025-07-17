import reflex as rx
from typing import List

def swiper_carousel(image_urls: rx.Var[List[str]], carousel_id: str) -> rx.Component:
    """
    Un componente de carrusel de imágenes deslizable (swipe) usando Swiper.js.
    
    Args:
        image_urls: Una variable de estado que contiene la lista de URLs de las imágenes.
        carousel_id: Un ID único y estático para esta instancia del carrusel.
    """
    # El ID único para el contenedor de Swiper se construye a partir del parámetro.
    swiper_id = f"swiper-container-{carousel_id}"
    
    return rx.box(
        # Contenedor principal de Swiper
        rx.box(
            # Contenedor de slides
            rx.box(
                rx.foreach(
                    image_urls,
                    lambda url: rx.box(
                        rx.image(src=url, width="100%", height="auto", object_fit="contain", loading="lazy"),
                        class_name="swiper-slide",
                    ),
                ),
                class_name="swiper-wrapper",
            ),
            # Botones de navegación
            rx.box(class_name=f"swiper-button-next swiper-nav-{carousel_id}", color="white"),
            rx.box(class_name=f"swiper-button-prev swiper-nav-{carousel_id}", color="white"),
            # Paginación
            rx.box(class_name=f"swiper-pagination swiper-pag-{carousel_id}"),
            
            # Estilos y configuración
            class_name="swiper",
            id=swiper_id,
            width="100%",
            height="auto",
            max_height="550px",
            border_radius="md",
            overflow="hidden",
        ),
        # Script para inicializar Swiper en este componente específico
        rx.script(f"""
            new Swiper('#{swiper_id}', {{
                loop: true,
                pagination: {{
                    el: '.swiper-pag-{carousel_id}',
                    clickable: true,
                }},
                navigation: {{
                    nextEl: '.swiper-nav-{carousel_id}.swiper-button-next',
                    prevEl: '.swiper-nav-{carousel_id}.swiper-button-prev',
                }},
                keyboard: true,
            }});
        """)
    )