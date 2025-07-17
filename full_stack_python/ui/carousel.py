# full_stack_python/ui/carousel.py (NUEVA VERSIÓN con react-responsive-carousel)

import reflex as rx
from reflex.components.component import NoSSRComponent

class Carousel(NoSSRComponent):
    """
    Wrapper para el componente react-responsive-carousel.
    """
    # La librería a instalar con npm
    library = "react-responsive-carousel"
    # El tag del componente principal
    tag = "Carousel"
    # Es una exportación nombrada
    is_default = False

    # Propiedades que podemos configurar
    show_arrows: rx.Var[bool] = True
    show_indicators: rx.Var[bool] = True
    show_status: rx.Var[bool] = False
    infinite_loop: rx.Var[bool] = True
    auto_play: rx.Var[bool] = True
    stop_on_hover: rx.Var[bool] = True
    use_keyboard_arrows: rx.Var[bool] = True
    swipeable: rx.Var[bool] = True
    emulate_touch: rx.Var[bool] = True # Permite arrastrar con el mouse

    def _get_imports(self) -> dict:
        """Añade la importación del CSS necesario."""
        imports = super()._get_imports()
        imports[""] = imports.get("", set()) | {"react-responsive-carousel/lib/styles/carousel.min.css"}
        return imports

# Creamos una instancia para usarla fácilmente
carousel = Carousel.create