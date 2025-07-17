# full_stack_python/ui/carousel.py

import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import List

class SwiperContainer(NoSSRComponent):
    """
    Wrapper de Reflex para el componente de React Swiper.
    Proporciona un carrusel de imágenes deslizable.
    """
    # Paquete NPM de la librería.
    library = "swiper/react"
    # Nombre del componente a importar.
    tag = "Swiper"
    # Es una exportación nombrada, no por defecto.
    is_default = False
    # Dependencias CSS necesarias para los estilos de Swiper.
    lib_dependencies: List[str] = [
        "swiper/css",
        "swiper/css/pagination",
        "swiper/css/navigation",
    ]

    # Propiedades de Swiper expuestas como Vars de Reflex.
    pagination: rx.Var[bool] = True
    navigation: rx.Var[bool] = False  # Desactivamos las flechas por defecto.
    allow_touch_move: rx.Var[bool] = True # Permite el deslizamiento con mouse y táctil.
    loop: rx.Var[bool] = True # Habilita el modo de bucle infinito.

class SwiperSlide(NoSSRComponent):
    """
    Wrapper de Reflex para el componente React SwiperSlide.
    Cada hijo de SwiperContainer debe ser un SwiperSlide.
    """
    library = "swiper/react"
    tag = "SwiperSlide"
    is_default = False

# Creación de instancias simplificadas para facilitar su uso.
swiper_container = SwiperContainer.create
swiper_slide = SwiperSlide.create