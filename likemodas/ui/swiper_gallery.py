import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import Any, List, Dict, Union

# El único paquete que se necesita instalar desde npm.
LIBRARY = "swiper"

class SwiperGallery(NoSSRComponent):
    """
    Wrapper para el componente principal de Swiper.
    Esta clase es la única que contiene la lógica de importación de JavaScript.
    """
    library = LIBRARY
    tag = "CustomSwiper"

    # Las props y los handlers no cambian.
    navigation: rx.Var[bool]
    pagination: rx.Var[Dict[str, bool]]
    loop: rx.Var[bool]
    space_between: rx.Var[int]
    slides_per_view: rx.Var[Union[int, str]]
    initial_slide: rx.Var[int]
    class_name: rx.Var[str]
    on_slide_change: rx.EventHandler[lambda swiper: [swiper.activeIndex]]
    on_click: rx.EventHandler[lambda swiper, event: [swiper.clickedIndex]]

    def add_imports(self) -> dict:
        # El CSS se importa en el JS, por lo que esto se deja vacío.
        return {}

    def _get_custom_code(self) -> str | None:
        """
        Inyecta el código JavaScript UNA SOLA VEZ.
        Importa todo lo necesario y lo exporta con alias únicos.
        """
        return """
import React from 'react';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Pagination } from 'swiper/modules';

// Importamos el CSS directamente en el JavaScript.
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';

// Exportamos los componentes originales PERO con un alias (un nuevo nombre único).
export { 
    Swiper as CustomSwiper, 
    SwiperSlide as CustomSwiperSlide, 
    Navigation as CustomSwiperNavigation, 
    Pagination as CustomSwiperPagination 
};
"""

# Las otras clases ahora son simples punteros. No necesitan heredar de SwiperBase
# ni tener su propio _get_custom_code, porque SwiperGallery ya provee todo.
class SwiperSlide(NoSSRComponent):
    """Wrapper para el componente SwiperSlide."""
    library = LIBRARY
    tag = "CustomSwiperSlide"

class SwiperNavigation(NoSSRComponent):
    """Wrapper para el módulo de Navegación."""
    library = LIBRARY
    tag = "CustomSwiperNavigation"

class SwiperPagination(NoSSRComponent):
    """Wrapper para el módulo de Paginación."""
    library = LIBRARY
    tag = "CustomSwiperPagination"

# Las funciones "create" no necesitan cambiar.
swiper_gallery = SwiperGallery.create
swiper_slide = SwiperSlide.create
swiper_navigation = SwiperNavigation.create
swiper_pagination = SwiperPagination.create