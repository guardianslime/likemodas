import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import Any, List, Dict, Union

# El nombre del paquete que se instalará con npm/bun.
# Esto es lo que se pasará a `npm install`.
# Ahora es el correcto y no causará el error de git.
LIBRARY = "swiper"

class SwiperNavigation(NoSSRComponent):
    # 1. Se especifica el paquete principal a instalar.
    library = LIBRARY
    tag = "Navigation"

    def _get_imports(self) -> dict[str, str]:
        # 2. Se especifica la ruta de importación correcta para el JS.
        return {"swiper/modules": [self.tag]}

class SwiperPagination(NoSSRComponent):
    library = LIBRARY
    tag = "Pagination"

    def _get_imports(self) -> dict[str, str]:
        return {"swiper/modules": [self.tag]}

class SwiperGallery(NoSSRComponent):
    library = LIBRARY
    tag = "Swiper"

    def _get_imports(self) -> dict[str, str]:
        # Le decimos a Reflex que importe este componente desde la sub-ruta 'swiper/react'.
        return {"swiper/react": [self.tag]}

    # Las props y los handlers se mantienen exactamente igual.
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

class SwiperSlide(NoSSRComponent):
    library = LIBRARY
    tag = "SwiperSlide"

    def _get_imports(self) -> dict[str, str]:
        # Le decimos a Reflex que importe este componente desde la sub-ruta 'swiper/react'.
        return {"swiper/react": [self.tag]}

# Las funciones "create" se mantienen igual.
swiper_gallery = SwiperGallery.create
swiper_slide = SwiperSlide.create
swiper_navigation = SwiperNavigation.create
swiper_pagination = SwiperPagination.create