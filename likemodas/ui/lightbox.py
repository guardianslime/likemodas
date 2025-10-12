# likemodas/ui/lightbox.py (SOLUCIÓN DEFINITIVA)

import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import List, Dict

class LightboxWrapper(NoSSRComponent):
    """
    Este es nuestro componente intermediario personalizado.
    Recibe los nombres de archivo desde Python y construye las URLs completas en JavaScript
    antes de pasarlas al componente Lightbox real.
    """
    library = "yet-another-react-lightbox"
    
    # ✨ CAMBIO 1: Apuntamos a nuestro componente JS personalizado que definiremos abajo.
    tag = "LikemodasLightbox"

    # Propiedades que nuestro wrapper recibirá desde Python
    open: rx.Var[bool]
    close: rx.event.EventSpec
    slides: rx.Var[List[Dict[str, str]]]
    index: rx.Var[int]

    # ✨ CAMBIO 2: Añadimos una propiedad para recibir la ruta de subida de archivos.
    upload_route: rx.Var[str]

    def add_imports(self) -> dict[str, str] | None:
        return {"": "yet-another-react-lightbox/styles.css"}

    def _get_imports(self) -> dict[str, str | list[str]]:
        # Importamos el componente Lightbox real para usarlo DENTRO de nuestro wrapper.
        return {"react": "default as React", self.library: "default as Lightbox"}

    # ✨ CAMBIO 3: Añadimos el código JavaScript personalizado.
    def _get_custom_code(self) -> str:
        return """
const LikemodasLightbox = (props) => {
  // Sacamos las propiedades que vienen de Python
  const { slides, upload_route, ...rest } = props;

  // 1. Verificamos que tengamos los datos necesarios.
  if (!slides || !upload_route) {
    return null;
  }

  // 2. Transformamos los datos: añadimos la ruta de subida a cada nombre de archivo.
  const finalSlides = slides.map(slide => ({
    ...slide,
    src: `${upload_route}/${slide.src}`
  }));

  // 3. Renderizamos el componente Lightbox REAL con los datos ya procesados.
  return React.createElement(Lightbox, {
    ...rest,
    slides: finalSlides,
  });
};
"""

# La instancia que usaremos en nuestra app ahora es de nuestro wrapper.
lightbox = LightboxWrapper.create