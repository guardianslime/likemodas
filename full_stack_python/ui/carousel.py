# full_stack_python/ui/carousel.py (CORREGIDO)

import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import List, Set

class SwiperContainer(NoSSRComponent):
    """
    Wrapper de Reflex para el componente de React Swiper.
    Proporciona un carrusel de imágenes deslizable.
    """
    library = "swiper" # ✨ CORRECCIÓN 1: Usar el paquete principal.
    tag = "Swiper"
    is_default = True # Swiper es la exportación por defecto de 'swiper/react'.

    # ✨ CORRECCIÓN 2: Las dependencias ahora solo incluyen el paquete principal.
    # Los CSS se importan directamente en el componente de React.
    lib_dependencies: List[str] = [
        "swiper",
    ]

    # Propiedades de Swiper expuestas como Vars de Reflex.
    pagination: rx.Var[bool] = True
    navigation: rx.Var[bool] = False
    allow_touch_move: rx.Var[bool] = True
    loop: rx.Var[bool] = True

    # ✨ CORRECCIÓN 3: Se registran los eventos que Swiper puede emitir.
    # Esto resuelve el error de "ValueError: The Box does not take in an ... event trigger".
    def _get_custom_triggers(self) -> Set[str]:
        return super()._get_custom_triggers() | {
            "on_slide_change",
            "on_init",
            "on_touch_start",
            "on_touch_end",
        }
    
    # Se añaden importaciones de CSS directamente al componente.
    def _get_imports(self):
        imports = super()._get_imports()
        imports[""] = {
            "swiper/css",
            "swiper/css/pagination",
            "swiper/css/navigation",
        }
        # También se importa el módulo de paginación para que funcione `pagination=True`
        imports[self.library] = imports[self.library] | {"Pagination"}
        return imports

    # Se añaden los módulos que se usarán en el componente
    def _get_props(self) -> dict:
        props = super()._get_props()
        if "pagination" in props and props["pagination"]:
            props["modules"] = [rx.vars.Var.create_safe("Pagination", _var_is_local=False)]
        return props


class SwiperSlide(NoSSRComponent):
    """
    Wrapper de Reflex para el componente React SwiperSlide.
    """
    library = "swiper/react"
    tag = "SwiperSlide"
    is_default = False

# Creación de instancias simplificadas para facilitar su uso.
swiper_container = SwiperContainer.create
swiper_slide = SwiperSlide.create