# likemodas/ui/carousel.py (CORREGIDO)

import reflex as rx
from reflex.components.component import NoSSRComponent

class Carousel(NoSSRComponent):
    """Un componente que envuelve react-responsive-carousel."""

    library = "react-responsive-carousel"
    tag = "Carousel"

    # Propiedades (props) que tu componente ya aceptaba
    show_arrows: rx.Var[bool]
    show_status: rx.Var[bool]
    show_indicators: rx.Var[bool]
    show_thumbs: rx.Var[bool]
    infinite_loop: rx.Var[bool]
    auto_play: rx.Var[bool]
    interval: rx.Var[int]
    width: rx.Var[str]

    # ✨ LÍNEA AÑADIDA: Declaramos el disparador de eventos ✨
    # Esto le dice a Reflex que "on_click_item" es un evento válido que
    # enviará un argumento (el índice de la imagen clickeada).
    on_click_item: rx.event.EventSpec[lambda index: [index]]

    # El método para importar el CSS necesario (sin cambios)
    def add_imports(self) -> dict[str, str] | None:
        return {"": "react-responsive-carousel/lib/styles/carousel.min.css"}

# La creación de la instancia se mantiene igual
carousel = Carousel.create