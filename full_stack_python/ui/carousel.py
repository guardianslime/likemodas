# full_stack_python/ui/carousel.py (VERSIÓN FINAL)

import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import List, Set

class SwiperContainer(NoSSRComponent):
    """
    Wrapper de Reflex para el componente de React Swiper.
    Proporciona un carrusel de imágenes deslizable.
    """
    # ✨ CORRECCIÓN: La librería a instalar es 'swiper'.
    library = "swiper"
    tag = "Swiper"
    lib_dependencies: List[str] = ["swiper"]

    pagination: rx.Var[bool] = True
    navigation: rx.Var[bool] = False
    allow_touch_move: rx.Var[bool] = True
    loop: rx.Var[bool] = True

    def _get_custom_triggers(self) -> Set[str]:
        return super()._get_custom_triggers() | {"on_slide_change", "on_init", "on_touch_start", "on_touch_end"}

    def _get_imports(self) -> dict:
        """
        ✨ CORRECCIÓN: Se especifica de dónde importar cada componente.
        Swiper y SwiperSlide vienen de 'swiper/react'.
        Los módulos vienen de 'swiper'.
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
    # ✨ CORRECCIÓN: La librería a instalar es 'swiper'.
    library = "swiper"
    tag = "SwiperSlide"

    def _get_imports(self) -> dict:
        # Se asegura de importar SwiperSlide desde 'swiper/react'.
        return {"swiper/react": {rx.ImportVar(tag=self.tag, is_default=False)}}

# Creación de instancias simplificadas
swiper_container = SwiperContainer.create
swiper_slide = SwiperSlide.create