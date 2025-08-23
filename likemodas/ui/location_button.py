# likemodas/ui/location_button.py (VERSIÓN FINAL Y CORRECTA)

import reflex as rx
from typing import List

class LocationButton(rx.Component):
    """
    Un componente personalizado que renderiza un botón y obtiene la ubicación del usuario,
    luego la envía de vuelta al estado de Reflex a través de un event handler.
    """
    # Al no especificar una 'library', Reflex entiende que el 'tag' es una etiqueta HTML nativa.
    tag = "div"

    on_location_success: rx.EventHandler[lambda lat, lon: [lat, lon]]
    on_location_error: rx.EventHandler

    def add_custom_code(self) -> List[str]:
        return [
            """
            function getLocation(on_success_handler, on_error_handler) {
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                        (position) => {
                            on_success_handler(position.coords.latitude, position.coords.longitude);
                        },
                        (error) => {
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

    def _render(self):
        self.children = [
            rx.button(
                rx.icon(tag="map-pin", margin_right="0.5em"),
                "Añadir mi ubicación con mapa",
                on_click=rx.call_script(
                    f"getLocation({self.on_location_success}, {self.on_location_error})"
                ),
                variant="outline",
                width="100%",
            )
        ]
        return super()._render()

# Creamos una instancia "fábrica" para que sea más fácil de usar.
location_button = LocationButton.create