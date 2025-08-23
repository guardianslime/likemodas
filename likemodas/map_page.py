import reflex as rx
import folium
from .. import navigation # --- ¡ESTA ES LA LÍNEA QUE FALTABA! ---

class MapPageState(rx.State):
    """Estado para manejar la página del mapa interactivo."""
    map_html: str = ""

    def on_load_map(self):
        """Genera el mapa interactivo con folium al cargar la página."""
        # Centra el mapa en Colombia
        m = folium.Map(location=[4.60971, -74.08175], zoom_start=6)

        # Añade un control para que el usuario pueda hacer clic y obtener un marcador
        # El popup mostrará las coordenadas para que el usuario las pueda copiar.
        m.add_child(folium.ClickForMarker(popup="<b>Coordenadas (Lat, Lng):</b><br><code>${lat}, ${lng}</code>"))

        # Convierte el mapa a HTML para mostrarlo en la página
        self.map_html = m._repr_html_()

def map_content() -> rx.Component:
    """Componente que muestra el mapa de folium."""
    return rx.center(
        rx.vstack(
            rx.heading("Selecciona tu Ubicación", size="8"),
            rx.text("1. Haz clic en tu ubicación exacta en el mapa."),
            rx.text("2. Copia las coordenadas (Latitud, Longitud) que aparecen."),
            rx.text("3. Pégalas en los campos correspondientes del formulario de dirección."),
            rx.box(
                # Usamos rx.html para renderizar el mapa generado por folium
                rx.html(MapPageState.map_html),
                height="60vh",
                width="100%",
                border="1px solid #ddd",
                border_radius="md",
                margin_top="1em"
            ),
            rx.link(rx.button("Volver al Formulario"), href=navigation.routes.SHIPPING_INFO_ROUTE),
            spacing="4",
            padding="2em",
            max_width="960px",
            align="center"
        ),
        width="100%",
    )