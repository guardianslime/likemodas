# likemodas/ui/lightbox.py (SOLUCIÓN FINAL Y DEFINITIVA)

import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import List, Dict

class LightboxWrapper(NoSSRComponent):
    """
    Componente intermediario que ahora es consciente del servidor/cliente
    para evitar errores de hidratación en React.
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
        # Modificamos el componente JS para que devuelva 'null' si se ejecuta en el servidor.
        return """
const LikemodasLightbox = (props) => {
  // 1. Si 'window' no está definido, significa que estamos en el servidor.
  // En ese caso, no renderizamos nada (null). Esto soluciona el error de hidratación.
  if (typeof window === 'undefined') {
    return null;
  }

  // 2. El resto de la lógica solo se ejecuta en el navegador del cliente.
  const { slides, upload_route, ...rest } = props;

  if (!slides || !upload_route) {
    return null;
  }

  const finalSlides = slides.map(slide => ({
    ...slide,
    src: `${upload_route}/${slide.src}`
  }));
  
  // 3. Devolvemos el componente Lightbox real con los datos procesados.
  return React.createElement(Lightbox, {
    ...rest,
    slides: finalSlides,
  });
};
"""
        # ✨ --- FIN DE LA CORRECCIÓN CLAVE --- ✨

lightbox = LightboxWrapper.create