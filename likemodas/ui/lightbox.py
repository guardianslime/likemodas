# likemodas/ui/lightbox.py (SOLUCIÓN DEFINITIVA)

import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import List

class FsLightboxWrapper(NoSSRComponent):
    """
    Wrapper personalizado para FsLightbox que construye las URLs en el frontend
    para evitar errores de hidratación.
    """
    library = "fslightbox-react"
    # ✨ Apuntamos a nuestro componente JS personalizado
    tag = "LikemodasFsLightbox"

    # Propiedades que nuestro wrapper recibirá desde Python
    toggler: rx.Var[bool]
    sources: rx.Var[List[str]]
    slide: rx.Var[int]
    on_close: rx.event.EventSpec
    
    # ✨ Añadimos una propiedad para recibir la ruta de subida
    upload_route: rx.Var[str]

    def _get_imports(self) -> dict[str, str | list[str]]:
        # Importamos el FsLightbox real para usarlo dentro de nuestro wrapper
        return {"react": "default as React", self.library: "default as FsLightbox"}

    def _get_custom_code(self) -> str:
        # ✨ Inyectamos el código JS que hace la transformación
        return """
const LikemodasFsLightbox = (props) => {
  // 1. Si estamos en el servidor, no renderizamos nada.
  if (typeof window === 'undefined') {
    return null;
  }

  // 2. En el cliente, procesamos los datos
  const { sources, upload_route, ...rest } = props;

  if (!sources || !upload_route) {
    return null;
  }

  // 3. Transformamos los nombres de archivo en URLs completas
  const finalSources = sources.map(src => `${upload_route}/${src}`);
  
  // 4. Renderizamos el FsLightbox real con los datos ya procesados
  return React.createElement(FsLightbox, {
    ...rest,
    sources: finalSources,
  });
};
"""

# La instancia que usaremos en nuestra app ahora es de nuestro wrapper
fslightbox = FsLightboxWrapper.create