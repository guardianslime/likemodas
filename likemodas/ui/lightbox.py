# Archivo: likemodas/ui/lightbox.py (CORRECCIÓN FINAL)

import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import List, Dict

class Lightbox(NoSSRComponent):
    """Componente que envuelve yet-another-react-lightbox."""
    library = "yet-another-react-lightbox"
    tag = "Lightbox"

    open: rx.Var[bool]
    close: rx.event.EventSpec
    slides: rx.Var[List[Dict[str, str]]]
    index: rx.Var[int]

    # ✨ --- INICIO DE LA CORRECCIÓN --- ✨
    # Volvemos a la propiedad 'on' que espera un diccionario.
    # Esto coincide exactamente con el prop 'on' de la librería de React.
    on: rx.Var[Dict]
    # ✨ --- FIN DE LA CORRECCIÓN --- ✨

    def add_imports(self) -> dict[str, str] | None:
        return {"": "yet-another-react-lightbox/styles.css"}

lightbox = Lightbox.create