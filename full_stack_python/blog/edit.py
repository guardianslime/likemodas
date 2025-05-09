import reflex as rx

from ..ui.base import base_page
# from . import forms

class EditExampleState(rx.State):

    def handle_submit(self, form_data):
        print(form_data)


def blog_post_edit_sample_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.hstack(
                rx.input(
                    name="title",
                    placeholder="Title",
                    required=True,
                    type='text',
                    width='100%',
                ),
                width='100%',
            ),
            rx.text_area(
                name='content',
                placeholder='Your message',
                required=True,
                height='50vh',
                width='100%',
            ),
            rx.button("Submit", type="submit"),
        ),
        on_submit=EditExampleState.handle_submit,
        reset_on_submit=True,
    )




def blog_post_edit_page() -> rx.Component:
    my_form = blog_post_edit_sample_form()
    my_child = rx.vstack(
            rx.heading("Edit Blog Post", size="9"), 
            rx.desktop_only(
                rx.box(
                    my_form,
                    width="50vw"
                )
            ),
            rx.tablet_only(
                rx.box(
                    my_form,
                    width="75vw"
                )
            ),
            rx.mobile_only(
                rx.box(
                    my_form,
                    id= "my-form-box",
                    width="85vw"
                )
            ),
            spacing="5",
            align="center",
            min_height="95vh",
        )
    
    return base_page(my_child)