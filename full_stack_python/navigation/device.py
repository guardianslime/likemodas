import reflex as rx

class DeviceState(rx.State):
    is_mobile: bool = False
    is_desktop: bool = False

    def on_mount(self):
        return rx.call_script(
            """
            const width = window.innerWidth;
            DeviceState.set_is_mobile(width < 768);
            DeviceState.set_is_desktop(width >= 768);
            """
        )