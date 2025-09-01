# likemodas/ui/carousel.py (EJEMPLO CORRECTO)

import reflex as rx
# La importación correcta
from reflex.components.component import NoSSRComponent

# La clase hereda de NoSSRComponent
class Carousel(NoSSRComponent):
    """Un componente que envuelve react-responsive-carousel."""

    # --- VERIFICACIÓN CRÍTICA ---
    # 1. ¿Existe esta línea? Debe ser el nombre exacto del paquete en npm.
    library = "react-responsive-carousel"

    # 2. ¿Existe esta línea? Debe ser el nombre exacto del componente a importar.
    tag = "Carousel"
    # --- FIN DE LA VERIFICACIÓN ---

    # Las propiedades (props) que tu componente aceptará.
    show_arrows: rx.Var[bool]
    show_status: rx.Var[bool]
    show_indicators: rx.Var[bool]
    show_thumbs: rx.Var[bool]
    infinite_loop: rx.Var[bool]
    auto_play: rx.Var[bool]
    interval: rx.Var[int]
    width: rx.Var[str]

    # El método para importar el CSS necesario.
    def add_imports(self) -> dict[str, str] | None:
        return {"": "react-responsive-carousel/lib/styles/carousel.min.css"}

