# ============================================================================
# ARCHIVO: likemodas/ui/carousel.py
# REVISIÓN APLICADA: Se reemplaza el contenido con tu código para asegurar la definición correcta.
# ============================================================================
from reflex.components.component import NoSSRComponent
import reflex as rx

class Carousel(NoSSRComponent):
    """
    Un componente que envuelve react-responsive-carousel.
    Un error aquí puede causar un LookupError durante la compilación.
    """
    # VERIFICACIÓN CRÍTICA:
    # 1. 'library' debe coincidir EXACTAMENTE con el nombre del paquete en npm.
    # 2. 'tag' debe coincidir EXACTAMENTE con el nombre del componente exportado
    #    (usualmente en PascalCase).
    library: str = "react-responsive-carousel"
    tag: str = "Carousel"

    # Propiedades del carrusel
    show_arrows: rx.Var[bool]
    show_status: rx.Var[bool]
    show_indicators: rx.Var[bool]
    show_thumbs: rx.Var[bool]
    infinite_loop: rx.Var[bool]
    auto_play: rx.Var[bool]
    
    # Se añade el import del CSS necesario para el carrusel
    def add_imports(self) -> dict[str, str] | None:
        return {"": "react-responsive-carousel/lib/styles/carousel.min.css"}

    @classmethod
    def create(cls, *children, **props):
        # Aseguramos valores por defecto razonables
        props.setdefault("show_arrows", True)
        props.setdefault("show_status", False)
        props.setdefault("show_indicators", True)
        props.setdefault("show_thumbs", False)
        props.setdefault("infinite_loop", True)
        props.setdefault("auto_play", True)
        return super().create(*children, **props)