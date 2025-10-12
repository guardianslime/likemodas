import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import Any, List, Dict, Union

# --- INICIO DE LA CORRECCIÓN 1: Importar los módulos ---
# Creamos wrappers simples para los módulos que Swiper necesita.
class SwiperNavigation(NoSSRComponent):
    library = "swiper/modules"
    tag = "Navigation"

class SwiperPagination(NoSSRComponent):
    library = "swiper/modules"
    tag = "Pagination"
# --- FIN DE LA CORRECCIÓN 1 ---

class SwiperGallery(NoSSRComponent):
    """
    Componente de Reflex que envuelve la biblioteca Swiper.js (swiper/react)
    """
    # --- INICIO DE LA CORRECCIÓN 2: Ruta de la librería ---
    # Apuntamos a 'swiper/react' en lugar de solo 'swiper'.
    library = "swiper/react"
    # --- FIN DE LA CORRECCIÓN 2 ---
    tag = "Swiper"

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
    # --- INICIO DE LA CORRECCIÓN 3: Ruta de la librería ---
    library = "swiper/react"
    # --- FIN DE LA CORRECCIÓN 3 ---
    tag = "SwiperSlide"

swiper_gallery = SwiperGallery.create
swiper_slide = SwiperSlide.create
# --- INICIO DE LA CORRECCIÓN 4: Exportar los módulos ---
swiper_navigation = SwiperNavigation.create
swiper_pagination = SwiperPagination.create
# --- FIN DE LA CORRECCIÓN 4 ---