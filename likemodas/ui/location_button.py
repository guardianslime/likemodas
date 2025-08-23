# likemodas/ui/location_button.py (NUEVO ARCHIVO)

import reflex as rx
from typing import List

class LocationButton(rx.Component):
    """
    Un componente personalizado que renderiza un botón y obtiene la ubicación del usuario,
    luego la envía de vuelta al estado de Reflex a través de un event handler.
    """
    library = "react"  # Usamos una librería base, no necesitamos una externa
    tag = "div"        # Renderizamos un contenedor simple

    # --- ✨ LA CLAVE ESTÁ AQUÍ ✨ ---
    # 1. Definimos los "disparadores de eventos" (event triggers) que nuestro componente tendrá.
    #    Estos son los canales de comunicación hacia el AppState.
    
    # Este se activará en caso de éxito y enviará dos floats (latitud, longitud).
    on_location_success: rx.EventHandler[lambda lat, lon: [lat, lon]]
    
    # Este se activará en caso de error, sin enviar datos.
    on_location_error: rx.EventHandler

    # 2. Sobrescribimos el método para añadir nuestro propio código JavaScript.
    def add_custom_code(self) -> List[str]:
        # Este código se incluirá en el frontend.
        return [
            """
            function getLocation(on_success_handler, on_error_handler) {
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                        (position) => {
                            // En lugar de 'reflex.call_event', llamamos al handler que nos pasaron.
                            on_success_handler(position.coords.latitude, position.coords.longitude);
                        },
                        (error) => {
                            // Si hay un error, llamamos al otro handler.
                            on_error_handler();
                        }
                    );
                } else {
                    alert("La geolocalización no es soportada por este navegador.");
                    on_error_handler();
                }
            }
            """
        ]

    # 3. Definimos cómo se renderiza el componente.
    def _render(self):
        return rx.button(
            rx.icon(tag="map-pin", margin_right="0.5em"),
            "Añadir mi ubicación con mapa",
            # Al hacer clic, llamamos a NUESTRA función JS y le pasamos los event handlers.
            on_click=rx.call_script(
                f"getLocation({self.on_location_success}, {self.on_location_error})"
            ),
            variant="outline",
            width="100%",
        )._render()

# Creamos una instancia "fábrica" para que sea más fácil de usar.
location_button = LocationButton.create