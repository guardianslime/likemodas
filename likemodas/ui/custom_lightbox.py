# En: likemodas/ui/custom_lightbox.py

import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import List, Dict

class CustomLightbox(NoSSRComponent):
    """
    [VERSIÓN FINAL Y CORREGIDA] Componente que envuelve 'yet-another-react-lightbox'
    y utiliza un wrapper de JavaScript personalizado para manejar los plugins.
    """
    library = "yet-another-react-lightbox"
    
    tag = "LikemodasLightboxWrapper"

    open: rx.Var[bool]
    
    # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
    # Se utiliza la sintaxis lambda para definir un evento sin argumentos,
    # que es la forma más compatible para esta versión de Reflex.
    close: rx.EventHandler[lambda: []]
    # --- ✨ FIN DE LA CORRECCIÓN ✨ ---
    
    slides: rx.Var[List[Dict[str, str]]]
    index: rx.Var[int]
    plugins: rx.Var[List]
    zoom: rx.Var[Dict]
    styles: rx.Var[Dict]
    carousel: rx.Var[Dict]
    controller: rx.Var[Dict]
    no_scroll: rx.Var[Dict]

    def get_imports(self) -> dict:
        """Importa React, el Lightbox, el plugin Zoom y los estilos."""
        return {
            "react": "React",
            "yet-another-react-lightbox": "Lightbox",
            "yet-another-react-lightbox/plugins/zoom": "Zoom",
            "": [
                "yet-another-react-lightbox/styles.css",
                "yet-another-react-lightbox/plugins/zoom.css"
            ],
        }

    def get_custom_code(self) -> str:
        """
        Crea un componente intermedio en React para interceptar la prop 'plugins'
        y reemplazar el string 'zoom' por el objeto Zoom real.
        """
        return """
const LikemodasLightboxWrapper = (props) => {
  const newProps = { ...props };
  if (newProps.plugins && Array.isArray(newProps.plugins)) {
    newProps.plugins = newProps.plugins.map(p => {
      if (p === 'zoom') return Zoom;
      return p;
    });
  }
  return React.createElement(Lightbox, newProps);
};
"""

# Creamos la instancia para usarla
custom_lightbox = CustomLightbox.create