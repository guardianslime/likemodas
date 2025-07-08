import reflex as rx
from .state import BlogAddFormState, BlogEditFormState

def blog_post_add_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.input(
                name="title",
                placeholder="Título del Post",
                required=True,
                width="100%",
            ),
            rx.text_area(
                name="content",
                placeholder="Escribe tu contenido aquí...",
                required=True,
                height="40vh",
                width="100%",
            ),
            rx.button("Crear Post", type="submit"),
            spacing="4",
        ),
        on_submit=BlogAddFormState.handle_submit,
        reset_on_submit=True,
    )

def blog_post_edit_form() -> rx.Component:
    return rx.cond(
        BlogEditFormState.post,
        rx.form(
            rx.vstack(
                rx.input(
                    type="hidden",
                    name="post_id",
                    value=rx.cond(
                        BlogEditFormState.post.id,
                        BlogEditFormState.post.id,
                        ""
                    ),
                ),
                rx.input(
                    name="title",
                    default_value=rx.cond(
                        BlogEditFormState.post.title,
                        BlogEditFormState.post.title,
                        ""
                    ),
                    placeholder="Título del Post",
                    required=True,
                    width="100%",
                ),
                rx.text_area(
                    name="content",
                    value=BlogEditFormState.post_content or "",
                    on_change=BlogEditFormState.set_post_content,
                    placeholder="Escribe tu contenido aquí...",
                    required=True,
                    height="40vh",
                    width="100%",
                ),
                rx.flex(
                    rx.switch(
                        name="publish_active",
                        is_checked=BlogEditFormState.post_publish_active,
                        on_change=BlogEditFormState.set_post_publish_active,
                    ),
                    rx.text("Publicar"),
                    spacing="2",
                ),
                rx.cond(
                    BlogEditFormState.post_publish_active,
                    rx.hstack(
                        rx.input(
                            name="publish_date",
                            type="date",
                            default_value=BlogEditFormState.publish_display_date,
                        ),
                        rx.input(
                            name="publish_time",
                            type="time",
                            default_value=BlogEditFormState.publish_display_time,
                        ),
                        width="100%"
                    ),
                ),
                rx.button("Guardar Cambios", type="submit"),
                spacing="4",
            ),
            on_submit=BlogEditFormState.handle_submit,
        ),
        rx.center(rx.spinner(), height="50vh")
    )
