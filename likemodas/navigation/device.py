# likemodas/navigation/device.py (VERSIÓN CORRECTA)

import reflex as rx

class NavDeviceState(rx.State):
    """Maneja el estado del dispositivo (móvil o escritorio) para la UI."""
    is_mobile: bool = False
    is_desktop: bool = False

    def on_mount(self):
        """
        Ejecuta un script en el cliente cuando la página carga para revisar
        el tamaño de la ventana y actualizar el estado.
        """
        return rx.call_script(
            f"""
            const width = window.innerWidth;
            if (window.nav_device_state) {{
                nav_device_state.set_is_mobile(width < 768);
                nav_device_state.set_is_desktop(width >= 768);
            }}
            """
        )