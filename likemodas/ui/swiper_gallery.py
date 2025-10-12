import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import Any, List, Dict, Union

# El paquete a instalar sigue siendo "swiper".
LIBRARY = "swiper"

class SwiperBase(NoSSRComponent):
    """Clase base que comparte la librería y el código JS personalizado."""
    library = LIBRARY

    def _get_custom_code(self) -> str | None:
        """
        Inyecta código JavaScript personalizado para importar los componentes
        de Swiper y exportarlos con nombres únicos para evitar colisiones.
        """
        return """
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Pagination } from 'swiper/modules';

// Exportamos los componentes originales PERO con un alias (un nuevo nombre único).
export { 
    Swiper as CustomSwiper, 
    SwiperSlide as CustomSwiperSlide, 
    Navigation as CustomSwiperNavigation, 
    Pagination as CustomSwiperPagination 
};
"""

class SwiperGallery(SwiperBase):
    """Wrapper para el componente principal de Swiper."""
    # Le decimos a Reflex que busque el componente con el nuevo nombre único.
    tag = "CustomSwiper"

    # Las props y handlers no cambian.
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
    tag = "CustomSwiperSlide"

class SwiperNavigation(SwiperBase):
    """Wrapper para el módulo de Navegación."""
    tag = "CustomSwiperNavigation"

class SwiperPagination(SwiperBase):
    """Wrapper para el módulo de Paginación."""
    tag = "CustomSwiperPagination"

# Las funciones "create" no necesitan cambiar. Reflex maneja los nombres internamente.
swiper_gallery = SwiperGallery.create
swiper_slide = SwiperSlide.create
swiper_navigation = SwiperNavigation.create
swiper_pagination = SwiperPagination.create