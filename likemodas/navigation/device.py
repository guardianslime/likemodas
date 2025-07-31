# likemodas/navigation/device.py (CORRECCIÓN DE DETECCIÓN DE DISPOSITIVO)

import reflex as rx

class NavDeviceState(rx.State):
    """
    Maneja el estado del dispositivo de forma más explícita para evitar el flickering.
    'unknown' es el estado inicial antes de que el script del navegador se ejecute.
    """
    device_type: str = "unknown"

    @rx.event
    def on_load_check_device(self):
        """
        Evento que se llama al cargar la página para ejecutar el script que detecta el tamaño.
        """
        return rx.call_script(
            f"""
            const width = window.innerWidth;
            // Llama al setter correspondiente en el estado para actualizar device_type
            if (width < 768) {{
                {self.set_device_type.get_event_handler_name("mobile")}
            }} else {{
                {self.set_device_type.get_event_handler_name("desktop")}
            }}
            """
        )