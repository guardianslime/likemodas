# likemodas/ui/lightbox.py (NUEVA VERSIÓN CON FSLIGHTBOX)

import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import List

class FsLightbox(NoSSRComponent):
    """Componente que envuelve la librería fslightbox-react."""
    library = "fslightbox-react"
    tag = "FsLightbox"

    # Propiedades que el componente aceptará desde Reflex
    
    # Booleano para abrir/cerrar el lightbox
    toggler: rx.Var[bool]

    # Lista de URLs de las imágenes a mostrar
    sources: rx.Var[List[str]]

    # El índice de la imagen con la que debe empezar (importante: empieza en 1)
    slide: rx.Var[int]

    # Evento que se dispara al cerrar el lightbox
    on_close: rx.event.EventSpec

# Creamos una instancia para usarla fácilmente
fslightbox = FsLightbox.create