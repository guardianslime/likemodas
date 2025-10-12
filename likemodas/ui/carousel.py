# likemodas/ui/carousel.py (CORREGIDO PARA REFLEX 0.8.5)

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

    # ✨ LÍNEA CORREGIDA: Se elimina la parte '[...]' ✨
    # Para la versión 0.8.5 de Reflex, solo necesitas declarar el tipo del evento.
    # Reflex pasará automáticamente el argumento 'index' a tu manejador en AppState.
    on_click_item: rx.event.EventSpec

    # El método para importar el CSS necesario (sin cambios)
    def add_imports(self) -> dict[str, str] | None:
        return {"": "react-responsive-carousel/lib/styles/carousel.min.css"}

# La creación de la instancia se mantiene igual
carousel = Carousel.create