# full_stack_python/ui/carousel.py (VERSIÓN FINAL CORREGIDA)

import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import List, Set

class SwiperContainer(NoSSRComponent):
    """
    Wrapper de Reflex para el componente de React Swiper.
    Proporciona un carrusel de imágenes deslizable.
    """
    # La librería a instalar es 'swiper', el paquete principal.
    library = "swiper"
    # El tag del componente que vamos a usar.
    tag = "Swiper"
    # Las dependencias de npm. Solo necesitamos el paquete principal.
    lib_dependencies: List[str] = ["swiper"]

    # Propiedades de Swiper que expondremos en Python.
    pagination: rx.Var[bool] = True
    navigation: rx.Var[bool] = False
    allow_touch_move: rx.Var[bool] = True
    loop: rx.Var[bool] = True

    def _get_custom_triggers(self) -> Set[str]:
        """Registra los eventos que Swiper puede emitir para evitar errores de 'ValueError'."""
        return super()._get_custom_triggers() | {"on_slide_change", "on_init", "on_touch_start", "on_touch_end"}

    def _get_imports(self) -> dict:
        """
        Define las importaciones de JS y CSS necesarias.
        - El componente 'Swiper' se importa de 'swiper/react'.
        - Los módulos como 'Pagination' se importan de 'swiper'.
        - Los estilos se importan directamente.
        """
        return {
            "swiper/react": {rx.ImportVar(tag=self.tag, is_default=True)},
            "": {
                "swiper/css",
                "swiper/css/pagination",
                "swiper/css/navigation",
            },
            "swiper": {
                rx.ImportVar(tag="Pagination", is_default=False),
                rx.ImportVar(tag="Navigation", is_default=False),
            },
        }

    def _get_props(self) -> dict:
        """Pasa las props al componente de React, incluyendo los módulos activados."""
        props = super()._get_props()
        modules = []
        if self.pagination:
            modules.append(rx.vars.Var.create_safe("Pagination", _var_is_local=False))
        if self.navigation:
            modules.append(rx.vars.Var.create_safe("Navigation", _var_is_local=False))
        if modules:
            props["modules"] = modules
        return props


class SwiperSlide(NoSSRComponent):
    """Wrapper de Reflex para el componente React SwiperSlide."""
    # La librería a instalar también es 'swiper'.
    library = "swiper"
    tag = "SwiperSlide"

    def _get_imports(self) -> dict:
        """Se asegura de importar SwiperSlide desde 'swiper/react'."""
        return {"swiper/react": {rx.ImportVar(tag=self.tag, is_default=False)}}

# Creación de instancias simplificadas para facilitar su uso.
swiper_container = SwiperContainer.create
swiper_slide = SwiperSlide.create
