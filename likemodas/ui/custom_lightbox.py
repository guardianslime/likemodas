# En: likemodas/ui/custom_lightbox.py

import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import List, Dict

class CustomLightbox(NoSSRComponent):
    """
    [VERSIÓN SIMPLIFICADA DE PRUEBA]
    Componente que envuelve 'yet-another-react-lightbox' SIN plugins.
    """
    library = "yet-another-react-lightbox"
    tag = "Lightbox"

    # Propiedades básicas para mostrar el lightbox
    open: rx.Var[bool]
    close: rx.EventHandler[lambda: []]
    slides: rx.Var[List[Dict[str, str]]]
    index: rx.Var[int]

    # Props de configuración que no dependen de plugins
    styles: rx.Var[Dict]
    controller: rx.Var[Dict]

    def get_imports(self) -> dict:
        """Importa solo los estilos básicos de la biblioteca."""
        return {"": "yet-another-react-lightbox/styles.css"}

# La instancia se mantiene igual
custom_lightbox = CustomLightbox.create