# full_stack_python/blog/forms.py

import reflex as rx
from .state import BlogAddPostFormState, BlogEditFormState, BlogPostState

def image_upload_component() -> rx.Component:
    return rx.vstack(
        rx.upload(
            rx.text("Arrastra una imagen aquí o haz clic para seleccionarla"),
            id="image_upload",
            accept={
                "image/png": [".png"],
                "image/jpeg": [".jpg", ".jpeg"],
                "image/gif": [".gif"],
                "image/webp": [".webp"],
            },
            max_files=1,
            border="2px dashed #60a5fa",
            padding="2em",
        ),
        rx.button(
            "Subir imagen",
            on_click=BlogPostState.handle_upload(rx.upload_files(upload_id="image_upload")),
        ),
    )

def blog_post_add_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.input(
                name="title",
                placeholder="Título",
                required=True,
                width="100%",
            ),
            rx.text_area(
                name="content",
                placeholder="Contenido de la publicación",
                required=True,
                height='30vh',
                width='100%',
            ),
            image_upload_component(),
            rx.button("Crear Publicación", type="submit"),
        ),
        on_submit=BlogAddPostFormState.handle_submit,
        reset_on_submit=True,
    )

def blog_post_edit_form() -> rx.Component:
    post = BlogEditFormState.post
    return rx.form(
        rx.box(
            rx.input(
                type='hidden',
                name='post_id',
                value=post.id
            ),
            display='none'
        ),
        rx.vstack(
            rx.input(
                default_value=post.title,
                name="title",
                placeholder="Título",
                required=True,
                width='100%',
            ),
            rx.text_area(
                value=BlogEditFormState.post_content,
                on_change=BlogEditFormState.set_post_content,
                name='content',
                placeholder='Contenido de la publicación',
                required=True,
                height='30vh',
                width='100%',
            ),
            rx.cond(
                BlogEditFormState.image_url,
                rx.image(src=BlogEditFormState.image_url, width="200px")
            ),
            image_upload_component(),
            rx.flex(
                rx.switch(
                    default_checked=BlogEditFormState.post_publish_active,
                    on_change=BlogEditFormState.set_post_publish_active,
                    name='publish_active',
                ),
                rx.text("Publicar"),
                spacing="2",
            ),
            rx.cond(
                BlogEditFormState.post_publish_active,
                rx.hstack(
                    rx.input(
                        default_value=BlogEditFormState.publish_display_date,
                        type='date',
                        name='publish_date',
                        width='100%'
                    ),
                    rx.input(
                        default_value=BlogEditFormState.publish_display_time,
                        type='time',
                        name='publish_time',
                        width='100%'
                    ),
                    width='100%'
                ),
            ),
            rx.button("Guardar Cambios", type="submit"),
        ),
        on_submit=BlogEditFormState.handle_submit,
    )