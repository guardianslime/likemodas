# likemodas/ui/carousel.py (SIMPLIFICADO)

import reflex as rx
from reflex.components.component import NoSSRComponent

class Carousel(NoSSRComponent):
    """Un componente que envuelve react-responsive-carousel."""

    library = "react-responsive-carousel"
    tag = "Carousel"

    show_arrows: rx.Var[bool]
    show_status: rx.Var[bool]
    show_indicators: rx.Var[bool]
    show_thumbs: rx.Var[bool]
    infinite_loop: rx.Var[bool]
    auto_play: rx.Var[bool]
    interval: rx.Var[int]
    width: rx.Var[str]
    height: rx.Var[str]

    # ✨ SE ELIMINA LA PROPIEDAD on_click_item DE AQUÍ ✨

    def add_imports(self) -> dict[str, str] | None:
        return {"": "react-responsive-carousel/lib/styles/carousel.min.css"}

carousel = Carousel.create