# full_stack_python/ui/carousel.py (VERSIÓN CANÓNICA Y CORRECTA)

import reflex as rx

# 1. Definimos una clase para el contenedor del carrusel.
# El nombre de la clase (_SwiperContainer) es un identificador válido en Python y JS.
class _SwiperContainer(rx.Component):
    # La variable 'tag' le dice a Reflex qué etiqueta HTML renderizar.
    # ¡Aquí es donde ponemos el nombre con guiones!
    tag = "swiper-container"

# 2. Definimos una clase para cada diapositiva.
class _SwiperSlide(rx.Component):
    tag = "swiper-slide"


# 3. Creamos funciones "fábrica" para que sea fácil usar nuestros nuevos componentes.
# Estas son las funciones que importarás y usarás en tus otras páginas.
def swiper_container(*children, **props):
    """Crea un componente <swiper-container>."""
    return _SwiperContainer.create(
        *children,
        # Propiedades por defecto para el carrusel
        pagination="true",
        navigation="false",
        loop="true",
        **props,
    )

def swiper_slide(*children, **props):
    """Crea un componente <swiper-slide>."""
    return _SwiperSlide.create(*children, **props)