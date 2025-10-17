# En: likemodas/ui/custom_carousel.py

import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import List

class CarouselComponent(NoSSRComponent):
    """
    Componente de Reflex que envuelve la biblioteca 'react-responsive-carousel'.
    Al heredar de NoSSRComponent, se asegura que solo se renderice en el cliente,
    evitando errores de hidratación.
    """
    # El nombre exacto del paquete en npm.
    library = "react-responsive-carousel"

    # El nombre del componente a importar desde la biblioteca.
    tag = "Carousel"

    # Propiedades (props) que el componente de React aceptará.
    # Estas se convierten en props en el componente de React.
    show_arrows: rx.Var[bool]
    show_status: rx.Var[bool]
    show_indicators: rx.Var[bool]
    show_thumbs: rx.Var[bool]
    infinite_loop: rx.Var[bool]
    auto_play: rx.Var[bool]
    stop_on_hover: rx.Var[bool]
    swipeable: rx.Var[bool]
    emulate_touch: rx.Var[bool]
    use_keyboard_arrows: rx.Var[bool]
    interval: rx.Var[int]
    width: rx.Var[str]
    selected_item: rx.Var[int]

    # Evento para notificar cambios en el slide seleccionado.
    on_change: rx.EventHandler[lambda index: [index]]

    def add_imports(self) -> dict[str, str] | None:
        """
        Importa el CSS necesario para que el carrusel se vea correctamente.
        """
        return {"": "react-responsive-carousel/lib/styles/carousel.min.css"}

# Crea una instancia para un uso más sencillo en otras partes de la aplicación.
carousel = CarouselComponent.create