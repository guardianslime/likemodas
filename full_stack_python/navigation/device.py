# full_stack_python/navigation/device.py (CÓDIGO CORREGIDO)

import reflex as rx

class NavDeviceState(rx.State):
    """Maneja el estado del dispositivo (móvil o escritorio) para la UI."""
    is_mobile: bool = False
    is_desktop: bool = False

    def on_mount(self):
        return rx.call_script(
            f"""
            const width = window.innerWidth;
            
            // ✨ CORREGIDO: Se cambió el comentario de Python (#) a JavaScript (//).
            // Se usa el nuevo nombre del estado en el script.
            if (window.nav_device_state) {{
                nav_device_state.set_is_mobile(width < 768);
                nav_device_state.set_is_desktop(width >= 768);
            }} else {{
                console.error("El objeto de estado 'nav_device_state' no fue encontrado.");
            }}
            """
        )