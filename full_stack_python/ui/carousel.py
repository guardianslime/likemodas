# full_stack_python/ui/carousel.py (VERSIÓN FINAL CORREGIDA)

import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import List, Set

class SwiperContainer(NoSSRComponent):
    """
    Wrapper de Reflex para el componente de React Swiper.
    Proporciona un carrusel de imágenes deslizable.
    """
    library = "swiper/react"
    tag = "Swiper"
    is_default = True
    lib_dependencies: List[str] = ["swiper"]

    pagination: rx.Var[bool] = True
    navigation: rx.Var[bool] = False
    allow_touch_move: rx.Var[bool] = True
    loop: rx.Var[bool] = True

    def _get_custom_triggers(self) -> Set[str]:
        return super()._get_custom_triggers() | {"on_slide_change", "on_init", "on_touch_start", "on_touch_end"}

    def _get_imports(self) -> dict:
        """
        ✨ CORRECCIÓN: Se elimina el uso de 'ImportVar' y se simplifica la
        adición de los módulos 'Pagination' y 'Navigation' como strings.
        """
        imports = super()._get_imports()
        
        # Añadir importaciones de CSS
        imports[""] = imports.get("", set()) | {
            "swiper/css",
            "swiper/css/pagination",
            "swiper/css/navigation",
        }
        
        # Añadir importaciones de módulos JS desde la librería 'swiper'
        imports["swiper"] = ["Pagination", "Navigation"]
        
        return imports

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
    library = "swiper/react"
    tag = "SwiperSlide"
    is_default = False

# Creación de instancias simplificadas
swiper_container = SwiperContainer.create
swiper_slide = SwiperSlide.create