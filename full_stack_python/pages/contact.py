import reflex as rx 

from .. import navigation
from ..ui.base import base_page


class ContactState(rx.State):
    form_data: dict = {}

    def handle_submit(self, form_data: dict):
        """handle the form submit."""
        print(form_data)
        self.form_data = form_data

@rx.page(route=navigation.routes.CONTACT_US_ROUTE)
def contact_page() -> rx.Component:
    my_form = rx.form(
            rx.vstack(
                rx.input(
                   name="first_name",
                   placeholder="First name",
                   required=True,
                   tyoe= "text",
                   width="100%",
                ),
                rx.input(
                    name="last_name",
                    placeholder="Last Name",
                    type="text",
                    width="100%",
                ),
                rx.input(
                    name= "email",
                    placeholder="Your email",
                    type= "email",
                    width="100%",
                ),
                rx.text_area(
                    name="message",
                    placeholder="Your message",
                    required=True,
                    width='100%',
                ),
                rx.button("Submit", type="submit"),
            ),
            on_submit=ContactState.handle_submit,
            reset_on_submit=True,
    )
    
    my_child = rx.vstack(
            rx.heading("Contact us", size="9"),
            rx.desktop_only(my_form),
            rx.mobile_and_tablet(my_form),
            spacing="5",
            justify="center",
            align="center",
            min_height="85vh",
            id='my-child'
        )
    return base_page(my_child)