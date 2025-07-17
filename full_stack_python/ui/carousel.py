import reflex as rx
from typing import List

def swiper_carousel(image_urls: rx.Var[List[str]]) -> rx.Component:
    """
    Un componente de carrusel de imágenes deslizable (swipe) usando Swiper.js.
    
    Args:
        image_urls: Una variable de estado que contiene la lista de URLs de las imágenes.
    """
    # El ID único es crucial para que cada carrusel en la página funcione de forma independiente.
    swiper_id = f"swiper-{rx.State.get_current_state().get_full_name()}"
    
    return rx.box(
        # Contenedor principal de Swiper
        rx.box(
            # Contenedor de slides
            rx.box(
                rx.foreach(
                    image_urls,
                    lambda url: rx.box(
                        rx.image(src=url, width="100%", height="auto", object_fit="contain"),
                        class_name="swiper-slide",
                    ),
                ),
                class_name="swiper-wrapper",
            ),
            # Botones de navegación (opcional, pero bueno tenerlos)
            rx.box(class_name="swiper-button-next", color="white"),
            rx.box(class_name="swiper-button-prev", color="white"),
            # Paginación (puntos en la parte inferior)
            rx.box(class_name="swiper-pagination"),
            
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
                    el: '#{swiper_id} .swiper-pagination',
                    clickable: true,
                }},
                navigation: {{
                    nextEl: '#{swiper_id} .swiper-button-next',
                    prevEl: '#{swiper_id} .swiper-button-prev',
                }},
                keyboard: true,
            }});
        """)
    )