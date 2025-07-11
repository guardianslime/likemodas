import reflex as rx

class DeviceState(rx.State):
    is_mobile: bool = False
    is_desktop: bool = False

    def on_mount(self):
        return rx.call_script(
            """
            if (window.innerWidth < 768) {
                DeviceState.set_is_mobile(true);
            } else {
                DeviceState.set_is_desktop(true);
            }
            """
        )
