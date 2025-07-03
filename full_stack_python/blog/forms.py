# full_stack_python/blog/forms.py

import reflex as rx
from .state import BlogEditFormState, BlogAddPostFormState
# --- CORRECCIÓN ---
# Se importa el componente de subida de imágenes desde el módulo `add`.
from .add import image_upload_component

def blog_post_edit_form() -> rx.Component:
    post = BlogEditFormState.post
    return rx.form(
        rx.box(rx.input(type='hidden', name='post_id', value=post.id), display='none'),
        rx.vstack(
            rx.input(
                default_value=post.title,
                name="title",
                placeholder="Título",
                required=True,
                width='100%',
            ),
            
            rx.heading("Imagen Principal", size="5", margin_top="1em", width="100%", text_align="left"),
            # Muestra la imagen actual si existe.
            rx.cond(
                post.image_url,
                rx.vstack(
                    rx.text("Imagen Actual:"),
                    rx.image(src=post.image_url, height="10em", width="auto", border_radius="0.5em", box_shadow="md"),
                    margin_bottom="1em",
                )
            ),
            rx.text("Sube una nueva imagen para reemplazar la actual:"),
            # --- USO DEL COMPONENTE REUTILIZABLE ---
            image_upload_component(BlogEditFormState),

            rx.text_area(
                value=BlogEditFormState.post_content,
                on_change=BlogEditFormState.set_post_content,
                name='content',
                required=True,
                height='50vh',
                width='100%',
                margin_top="1em",
            ),
            rx.flex(
                rx.switch(
                    default_checked=BlogEditFormState.post_publish_active,
                    on_change=BlogEditFormState.set_post_publish_active,
                    name='publish_active',
                ),
                rx.text("Publicar Artículo"),
                spacing="2",
            ),
            rx.button("Guardar Cambios", type="submit"),
            spacing="4"
        ),
        on_submit=BlogEditFormState.handle_submit,
    )

# El formulario de añadir ya no es necesario aquí, ya que se define directamente
# en `blog_post_add_page` para mayor claridad.