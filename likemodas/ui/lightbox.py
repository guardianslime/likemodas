# Archivo: likemodas/ui/lightbox.py (CORREGIDO)

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

    # ✨ --- INICIO DE LA CORRECCIÓN --- ✨
    # En lugar de la propiedad genérica 'on', declaramos un disparador de evento específico.
    # Esto es más claro para el compilador de Reflex.
    on_view: rx.event.EventSpec
    # ✨ --- FIN DE LA CORRECCIÓN --- ✨

    def add_imports(self) -> dict[str, str] | None:
        return {"": "yet-another-react-lightbox/styles.css"}

# La instancia se mantiene igual
lightbox = Lightbox.create