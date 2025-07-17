# full_stack_python/ui/carousel.py (VERSIÓN FINAL CON rx.Component.create)

import reflex as rx

def swiper_container(*children, **props):
    """
    Crea un contenedor de carrusel usando el tag <swiper-container>.
    Se utiliza rx.Component.create(tag="...") para crear etiquetas con guiones.
    """
    # ✨ CORRECCIÓN: Se usa rx.Component.create en lugar de rx.el.component.
    return rx.Component.create(
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
    # ✨ CORRECCIÓN: Se usa rx.Component.create en lugar de rx.el.component.
    return rx.Component.create(
        tag="swiper-slide",
        *children,
        **props
    )