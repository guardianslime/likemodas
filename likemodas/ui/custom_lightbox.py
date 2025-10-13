# En: likemodas/ui/custom_lightbox.py
import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import List, Dict

class CustomLightbox(NoSSRComponent):
    """Componente que envuelve la biblioteca 'yet-another-react-lightbox' con el plugin de Zoom."""
    
    library = "yet-another-react-lightbox"
    tag = "Lightbox"

    # Propiedades que el componente de React espera
    open: rx.Var[bool]
    close: rx.EventHandler[[]]
    slides: rx.Var[List[Dict[str, str]]]
    index: rx.Var[int]
    plugins: rx.Var[List]

    def add_imports(self) -> dict[str, str] | None:
        """Importa los CSS de la biblioteca y del plugin de zoom."""
        return {
            "": "yet-another-react-lightbox/styles.css",
            "yet-another-react-lightbox/plugins/zoom": "Zoom"
        }

# Creamos una instancia para usarla fácilmente
custom_lightbox = CustomLightbox.create