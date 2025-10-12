import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import Any, List, Dict, Union

# El único paquete que se necesita instalar desde npm.
LIBRARY = "swiper"

class SwiperBase(NoSSRComponent):
    """Una clase base que comparte la librería y el código JS personalizado."""
    library = LIBRARY

    def _get_custom_code(self) -> str | None:
        """
        Inyecta código JavaScript personalizado en el frontend.
        Esto nos da control total sobre las importaciones, evitando el error.
        """
        return """
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Pagination } from 'swiper/modules';

// Exportamos los componentes para que Reflex pueda encontrarlos por su 'tag'.
export { Swiper, SwiperSlide, Navigation, Pagination };
"""

class SwiperGallery(SwiperBase):
    """Wrapper para el componente principal de Swiper."""
    tag = "Swiper"

    # Las props y los handlers no cambian.
    modules: rx.Var[List[Any]]
    navigation: rx.Var[bool]
    pagination: rx.Var[Dict[str, bool]]
    loop: rx.Var[bool]
    space_between: rx.Var[int]
    slides_per_view: rx.Var[Union[int, str]]
    initial_slide: rx.Var[int]
    class_name: rx.Var[str]
    on_slide_change: rx.EventHandler[lambda swiper: [swiper.activeIndex]]
    on_click: rx.EventHandler[lambda swiper, event: [swiper.clickedIndex]]

    # La importación de CSS tampoco cambia.
    def add_imports(self) -> dict[str, str]:
        return {
            "": [
                "swiper/css",
                "swiper/css/navigation",
                "swiper/css/pagination",
            ]
        }

class SwiperSlide(SwiperBase):
    """Wrapper para el componente SwiperSlide."""
    tag = "SwiperSlide"

class SwiperNavigation(SwiperBase):
    """Wrapper para el módulo de Navegación."""
    tag = "Navigation"

class SwiperPagination(SwiperBase):
    """Wrapper para el módulo de Paginación."""
    tag = "Pagination"

# Las funciones "create" se mantienen igual para facilitar su uso.
swiper_gallery = SwiperGallery.create
swiper_slide = SwiperSlide.create
swiper_navigation = SwiperNavigation.create
swiper_pagination = SwiperPagination.create