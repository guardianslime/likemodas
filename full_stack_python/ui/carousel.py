# full_stack_python/ui/carousel.py (VERSIÓN FINAL CON rx.el.component)

import reflex as rx

def swiper_container(*children, **props):
    """
    Crea un contenedor de carrusel usando el tag <swiper-container>.
    Se utiliza rx.el.component(tag="...") para crear etiquetas con guiones.
    """
    # ✨ CORRECCIÓN: Usamos rx.el.component para crear la etiqueta con guion.
    return rx.el.component(
        tag="swiper-container",
        *children,
        # Propiedades por defecto para el carrusel
        pagination="true",
        navigation="false",
        loop="true",
        **props,
    )

def swiper_slide(*children, **props):
    """
    Crea una diapositiva del carrusel usando el tag <swiper-slide>.
    """
    # ✨ CORRECCIÓN: Usamos rx.el.component para crear la etiqueta con guion.
    return rx.el.component(
        tag="swiper-slide",
        *children,
        **props
    )