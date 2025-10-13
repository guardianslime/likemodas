import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import List

class Carousel(NoSSRComponent):
    """
    Un wrapper robusto para react-responsive-carousel que maneja los hijos
    dinámicamente y acepta props comunes de la librería.
    Hereda de NoSSRComponent para garantizar la compatibilidad con SSR.
    """
    library = "react-responsive-carousel"
    tag = "Carousel"

    # Props comunes de la librería
    show_arrows: rx.Var[bool]
    show_status: rx.Var[bool]
    show_indicators: rx.Var[bool]
    show_thumbs: rx.Var[bool]
    infinite_loop: rx.Var[bool]
    auto_play: rx.Var[bool]
    interval: rx.Var[int]
    width: rx.Var[str]
    selected_item: rx.Var[int]
    
    # Maneja la importación del CSS necesario
    def add_imports(self) -> dict[str, str]:
        return {"": "react-responsive-carousel/lib/styles/carousel.min.css"}

    # --- ✨ INICIO DE LA CORRECCIÓN CLAVE ✨ ---
    # Este método ahora simplemente pasa los argumentos a la clase base,
    # que es la forma correcta de hacerlo.
    @classmethod
    def create(cls, *children, **props):
        """Crea el componente de carrusel."""
        return super().create(*children, **props)
    # --- ✨ FIN DE LA CORRECCIÓN CLAVE ✨ ---