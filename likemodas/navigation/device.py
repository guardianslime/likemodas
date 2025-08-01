# ============================================================================
# ARCHIVO: likemodas/navigation/device.py
# CORRECCIÓN: Soluciona el AttributeError en producción
# ============================================================================
import reflex as rx

class NavDeviceState(rx.State):
    """Maneja el estado del dispositivo (móvil o escritorio) para la UI."""
    device_type: str = "unknown"

    @rx.event
    def set_device_type(self, device_type: str):
        """Event handler para establecer el tipo de dispositivo desde el frontend."""
        self.device_type = device_type

    @rx.event
    def on_load_check_device(self):
        """
        Evento que se llama al cargar la página para ejecutar el script que detecta el tamaño.
        """
        # --- INICIO DE LA CORRECCIÓN DEL ATTRIBUTEERROR ---
        # Se obtiene el nombre del manejador desde la CLASE (type(self)) en lugar de la
        # instancia (self). El objeto 'self' es un proxy de estado y no siempre expone
        # la metadata de otros manejadores de eventos directamente. Acceder a través
        # de la clase es la forma segura y correcta.
        handler_name = type(self).set_device_type.get_event_handler_name()
        # --- FIN DE LA CORRECCIÓN DEL ATTRIBUTEERROR ---
        
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
