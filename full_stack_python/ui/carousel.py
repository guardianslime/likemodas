# full_stack_python/ui/carousel.py (VERSIÓN FINAL CON CDN)

import reflex as rx

def swiper_container(*children, **props):
    """
    Crea un contenedor de carrusel usando el tag <swiper-container> de la CDN.
    Reflex convierte rx.el.lo_que_sea en una etiqueta HTML <lo-que-sea>.
    """
    return rx.el.swiper_container(
        *children,
        # Propiedades por defecto para el carrusel.
        # Se pasan como strings porque son atributos HTML.
        pagination="true",
        navigation="false", # Las flechas de navegación están desactivadas
        loop="true",
        # Permite que se pasen otras propiedades personalizadas.
        **props,
    )

def swiper_slide(*children, **props):
    """
    Crea una diapositiva del carrusel usando el tag <swiper-slide> de la CDN.
    """
    return rx.el.swiper_slide(*children, **props)
