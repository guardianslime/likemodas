# full_stack_python/ui/carousel.py (VERSIÓN FINAL CON ACCESO DE DICCIONARIO)

import reflex as rx

def swiper_container(*children, **props):
    """
    Crea un contenedor de carrusel usando el tag <swiper-container>.
    Se utiliza el acceso de diccionario rx.el["tag-con-guion"] para crear la etiqueta.
    """
    # ✨ CORRECCIÓN FINAL: Usamos rx.el["..."] para crear la etiqueta con guion.
    return rx.el["swiper-container"](
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
    # ✨ CORRECCIÓN FINAL: Usamos rx.el["..."] para crear la etiqueta con guion.
    return rx.el["swiper-slide"](
        *children,
        **props
    )