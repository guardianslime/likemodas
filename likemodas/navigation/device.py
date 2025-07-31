import reflex as rx

class NavDeviceState(rx.State):
    """
    Maneja el estado del dispositivo (móvil o escritorio) para la UI.
    'unknown' es el estado inicial para evitar el parpadeo.
    """
    device_type: str = "unknown"

    @rx.event
    def set_device_type(self, device_type: str):
        """Un event handler para establecer el tipo de dispositivo desde el frontend."""
        self.device_type = device_type

    @rx.event
    def on_load_check_device(self):
        """
        Evento que se llama al cargar la página para ejecutar el script que detecta el tamaño.
        Esta es la forma correcta de llamar a un event handler con argumentos desde JS.
        """
        handler_name = self.set_device_type.get_event_handler_name()
        return rx.call_script(
            f"""
            const width = window.innerWidth;
            if (width < 768) {{
                {handler_name}("mobile");
            }} else {{
                {handler_name}("desktop");
            }}
            """
        )
