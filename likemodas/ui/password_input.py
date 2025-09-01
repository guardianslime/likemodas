import reflex as rx

class PasswordInputState(rx.State):
    show_password: bool = False

    def toggle_password_visibility(self):
        self.show_password = not self.show_password

def password_input(
    **props,
) -> rx.Component:
    return rx.vstack(
        rx.input(
            type=rx.cond(PasswordInputState.show_password, "text", "password"),
            **props,
        ),
        rx.icon(
            tag="eye",  # Puedes usar otro icono de tu preferencia
            on_click=PasswordInputState.toggle_password_visibility,
            cursor="pointer",
            align_self="flex-end",
            margin_top="-2.5em",
            margin_right="0.5em",
        ),
        align_items="stretch",
    )

