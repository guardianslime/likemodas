# Archivo: likemodas/ui/lightbox.py
import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import List, Dict

class Lightbox(NoSSRComponent):
    """Componente que envuelve yet-another-react-lightbox."""
    library = "yet-another-react-lightbox"
    tag = "Lightbox"

    # Propiedades que el componente aceptará desde Reflex
    open: rx.Var[bool]
    close: rx.event.EventSpec
    slides: rx.Var[List[Dict[str, str]]]
    index: rx.Var[int]

    # Evento para sincronizar el índice cuando el usuario navega dentro del lightbox
    on: rx.Var[Dict]

    def add_imports(self) -> dict[str, str] | None:
        # Importa los estilos base para el lightbox
        return {"": "yet-another-react-lightbox/styles.css"}

# Crea una instancia para un uso más sencillo
lightbox = Lightbox.create