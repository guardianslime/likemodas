# full_stack_python/navigation/device.py (CORREGIDO)

import reflex as rx

class DeviceState(rx.State):
    is_mobile: bool = False
    is_desktop: bool = False

    def on_mount(self):
        return rx.call_script(
            """
            const width = window.innerWidth;
            // ✨ CORRECCIÓN AQUÍ: Se cambió DeviceState a device_state
            device_state.set_is_mobile(width < 768);
            device_state.set_is_desktop(width >= 768);
            """
        )