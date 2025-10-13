# En: likemodas/ui/custom_lightbox.py

import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import List, Dict

class CustomLightbox(NoSSRComponent):
    """
    [VERSIÓN FINAL] Componente que envuelve 'yet-another-react-lightbox'
    y utiliza un wrapper de JavaScript personalizado para manejar los plugins.
    """
    library = "yet-another-react-lightbox"
    
    tag = "LikemodasLightboxWrapper"

    open: rx.Var[bool]
    
    # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
    # Cambiamos la lista vacía [] por una tupla vacía () para la correcta
    # definición de un evento sin argumentos en esta versión de Reflex.
    close: rx.EventHandler[()]
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
        Este código crea un componente intermedio en React.
        Intercepta la prop 'plugins', busca el string "zoom", y lo reemplaza
        por el objeto 'Zoom' real antes de pasárselo al componente Lightbox.
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