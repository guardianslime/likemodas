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
    # El nombre 'on_view' es solo un ejemplo, lo importante es que sea un EventSpec.
    # El nombre real del evento en la librería de React es 'on.view', por lo que
    # debemos indicar a Reflex cómo mapearlo.
    #
    # CORRECCIÓN IMPORTANTE: El nombre de la propiedad en Python no puede tener puntos.
    # Reflex convertirá automáticamente 'on_view' a 'onView' en JavaScript.
    # Sin embargo, la librería de lightbox espera una propiedad anidada 'on={{ view: ... }}'.
    # La solución más simple es volver a la propiedad genérica 'on', pero usar un
    # manejador intermediario en AppState.
    
    # Vamos a usar un nombre de propiedad que no dé conflictos.
    on_view: rx.event.EventSpec

    # ✨ --- FIN DE LA CORRECCIÓN --- ✨

    def add_imports(self) -> dict[str, str] | None:
        return {"": "yet-another-react-lightbox/styles.css"}

# La instancia se mantiene igual
lightbox = Lightbox.create