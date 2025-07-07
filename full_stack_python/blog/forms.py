# full_stack_python/blog/forms.py

import reflex as rx
from .state import BlogAddPostFormState, BlogPostState

def blog_post_add_form() -> rx.Component:
    # Este formulario para añadir posts no cambia.
    return rx.form(
        rx.vstack(
            rx.input(name="title", placeholder="Title", required=True, width="100%"),
            rx.text_area(name="content", placeholder="Your message", required=True, height='50vh', width='100%'),
            rx.button("Submit", type="submit"),
        ),
        on_submit=BlogAddPostFormState.handle_submit,
        reset_on_submit=True,
    )

def blog_post_edit_form() -> rx.Component:
    """Este formulario ahora usa el estado unificado BlogPostState."""
    return rx.form(
        rx.vstack(
            rx.input(name='post_id', value=BlogPostState.post.id, type='hidden'),
            rx.input(
                default_value=BlogPostState.post.title,
                name="title",
                placeholder="Title",
                width='100%',
            ),
            rx.text_area(
                value=BlogPostState.post_content,
                on_change=BlogPostState.set_post_content,
                name='content',
                height='50vh',
                width='100%',
            ),
            rx.flex(
                rx.switch(
                    is_checked=BlogPostState.post_publish_active,
                    on_change=BlogPostState.set_post_publish_active,
                    name='publish_active',
                ),
                rx.text("Publish Active"),
                spacing="2",
            ),
            rx.cond(
                BlogPostState.post_publish_active,
                rx.hstack(
                    rx.input(
                        default_value=BlogPostState.publish_display_date,
                        type='date',
                        name='publish_date',
                    ),
                    rx.input(
                        default_value=BlogPostState.publish_display_time,
                        type='time',
                        name='publish_time',
                    ),
                )
            ),
            rx.button("Guardar Cambios", type="submit"),
        ),
        # Apunta al nuevo manejador de submit para la edición
        on_submit=BlogPostState.handle_edit_submit,
    )