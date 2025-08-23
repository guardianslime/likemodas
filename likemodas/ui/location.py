# likemodas/ui/location.py
import reflex as rx
from typing import Dict

class LocationButton(rx.Component):
    # La ruta al archivo JS que creamos, relativa a la carpeta assets
    library = "/js/LocationButton.js"

    # El nombre exacto del componente que exportamos en JS
    tag = "LocationButton"

    # Esto define un "evento" que nuestro componente puede emitir.
    # Lo usaremos para enviar los datos de vuelta a AppState.
    on_location_update: rx.EventHandler[lambda data: [data]]