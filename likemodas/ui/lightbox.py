# likemodas/ui/lightbox.py (SOLUCIÓN FINAL Y DEFINITIVA)

import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import List, Dict

class LightboxWrapper(NoSSRComponent):
    """
    Componente intermediario que construye las URLs en el frontend
    y ahora comprueba si se está ejecutando en el navegador.
    """
    library = "yet-another-react-lightbox"
    tag = "LikemodasLightbox"

    open: rx.Var[bool]
    close: rx.event.EventSpec
    slides: rx.Var[List[Dict[str, str]]]
    index: rx.Var[int]
    upload_route: rx.Var[str]

    def add_imports(self) -> dict[str, str] | None:
        return {"": "yet-another-react-lightbox/styles.css"}

    def _get_imports(self) -> dict[str, str | list[str]]:
        return {"react": "default as React", self.library: "default as Lightbox"}

    def _get_custom_code(self) -> str:
        # ✨ --- INICIO DE LA CORRECCIÓN CLAVE --- ✨
        # Añadimos una comprobación inicial: "typeof window !== 'undefined'"
        # Esto asegura que el código que accede a 'window' solo se ejecute en el navegador
        # y no en el servidor durante la compilación, evitando el error 'window is not defined'.
        return """
if (typeof window !== 'undefined' && !window.LikemodasLightbox) {
  window.LikemodasLightbox = (props) => {
    const { slides, upload_route, ...rest } = props;

    if (!slides || !upload_route) {
      return null;
    }

    const finalSlides = slides.map(slide => ({
      ...slide,
      src: `${upload_route}/${slide.src}`
    }));

    return React.createElement(Lightbox, {
      ...rest,
      slides: finalSlides,
    });
  };
}
"""
        # ✨ --- FIN DE LA CORRECCIÓN CLAVE --- ✨

lightbox = LightboxWrapper.create