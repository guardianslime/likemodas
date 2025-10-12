# likemodas/ui/lightbox.py (SOLUCIÓN DEFINITIVA Y FINAL)

import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import List

class FsLightboxWrapper(NoSSRComponent):
    """
    Wrapper final para FsLightbox que comprueba si ya existe
    globalmente para evitar errores de re-declaración.
    """
    library = "fslightbox-react"
    tag = "LikemodasFsLightbox"

    # Propiedades que nuestro wrapper recibirá desde Python
    toggler: rx.Var[bool]
    sources: rx.Var[List[str]]
    slide: rx.Var[int]
    on_close: rx.event.EventSpec
    upload_route: rx.Var[str]

    def _get_imports(self) -> dict[str, str | list[str]]:
        # Importamos el FsLightbox real para usarlo dentro de nuestro wrapper
        return {"react": "default as React", self.library: "default as FsLightbox"}

    def _get_custom_code(self) -> str:
        # ✨ --- INICIO DE LA CORRECCIÓN CLAVE --- ✨
        # Comprobamos si el componente YA ha sido declarado en el objeto global 'window'.
        # Si no existe, lo creamos y lo asignamos a 'window' para que las futuras
        # comprobaciones lo encuentren y no intenten re-declararlo.
        # Esto soluciona el error 'Identifier has already been declared'.
        return """
if (typeof window !== 'undefined' && !window.LikemodasFsLightbox) {
  window.LikemodasFsLightbox = (props) => {
    // Esta parte interna no cambia.
    const { sources, upload_route, ...rest } = props;

    if (!sources || !upload_route) {
      return null;
    }

    const finalSources = sources.map(src => `${upload_route}/${src}`);
    
    return React.createElement(FsLightbox, {
      ...rest,
      sources: finalSources,
    });
  };
}
"""
        # ✨ --- FIN DE LA CORRECCIÓN CLAVE --- ✨

# La instancia que usaremos en nuestra app ahora es de nuestro wrapper
fslightbox = FsLightboxWrapper.create