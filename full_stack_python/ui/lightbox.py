# full_stack_python/ui/lightbox.py

import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import List

class Lightbox(NoSSRComponent):
    """
    Wrapper para el componente yet-another-react-lightbox.
    Muestra una vista ampliada de las imágenes.
    """
    # La librería que se instalará con npm
    library = "yet-another-react-lightbox"
    # El tag del componente principal
    tag = "Lightbox"
    # Es la exportación por defecto de la librería
    is_default = True

    # Propiedades que el componente necesita
    open: rx.Var[bool]
    close: rx.event.EventHandler[lambda: []]
    slides: rx.Var[List[dict]]

    def _get_imports(self) -> dict:
        """Añade la importación de los estilos CSS necesarios."""
        imports = super()._get_imports()
        imports[""] = imports.get("", set()) | {"yet-another-react-lightbox/styles.css"}
        return imports

# Creamos una instancia para usarla fácilmente
lightbox = Lightbox.create