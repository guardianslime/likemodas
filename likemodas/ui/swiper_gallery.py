import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import Any, List, Dict, Union

# Hereda de NoSSRComponent para compatibilidad en producción.
class SwiperGallery(NoSSRComponent):
    """
    Componente de Reflex que envuelve la biblioteca Swiper.js (swiper/react)
    para crear carruseles de imágenes interactivos y personalizables.
    """
    # El nombre exacto del paquete en npm.
    library = "swiper"
    
    # El nombre del componente principal que se importará.
    tag = "Swiper"

    # --- Mapeo de props de React a Vars de Reflex ---
    # Esto define la API de nuestro componente en Python.
    modules: rx.Var[List[Any]]
    navigation: rx.Var[bool]
    pagination: rx.Var[Dict[str, bool]]
    loop: rx.Var[bool]
    space_between: rx.Var[int]
    slides_per_view: rx.Var[Union[int, str]]
    initial_slide: rx.Var[int]
    class_name: rx.Var[str]

    # --- Mapeo de manejadores de eventos ---
    # Permite la comunicación desde el frontend (JS) hacia el backend (Python).
    
    # Se dispara cuando la diapositiva activa cambia. Envía el nuevo índice.
    on_slide_change: rx.EventHandler[lambda swiper: [swiper.activeIndex]]
    
    # Se dispara al hacer clic. Envía el índice de la diapositiva clickeada.
    on_click: rx.EventHandler[lambda swiper, event: [swiper.clickedIndex]]

    # Este método le dice a Reflex qué archivos CSS son necesarios.
    def add_imports(self) -> dict[str, str]:
        return {
            "": [
                "swiper/css",
                "swiper/css/navigation",
                "swiper/css/pagination",
            ]
        }

# Clase separada para las diapositivas individuales.
class SwiperSlide(NoSSRComponent):
    library = "swiper"
    tag = "SwiperSlide"

# Funciones "create" para una API más limpia.
swiper_gallery = SwiperGallery.create
swiper_slide = SwiperSlide.create