import reflex as rx
from .state import BlogAddPostFormState, BlogEditFormState

def image_upload_component(State: rx.State) -> rx.Component:
    """Un componente para subir la imagen del post y mostrar una vista previa."""
    return rx.vstack(
        # El on_drop ahora está dentro del componente correcto
        rx.upload(
            rx.box(
                rx.icon(tag="cloud_upload", style={"width": "3rem", "height": "3rem"}),
                rx.text("Arrastra o haz clic para subir una imagen"),
            ),
            id="my_upload",
            border="2px dashed #ccc",
            padding="1rem",
            # 👇 --- ESTA ES LA LÍNEA QUE SE MOVIÓ AQUÍ DENTRO ---
            on_drop=State.handle_upload,
        ),
        # La vista previa de las imágenes se queda aquí
        rx.flex(
            rx.foreach(
                State.img,
                lambda image: rx.image(src=image, height="8em", width="auto"),
            ),
            spacing="2",
            margin_top="1rem",
        ),
        align="center",
        width="100%",
    )

def blog_post_add_form() -> rx.Component:
    """El formulario para AÑADIR un nuevo post."""
    return rx.form(
        rx.vstack(
            rx.input(name="title", placeholder="Título del Artículo", required=True, width="100%"),
            rx.heading("Imagen Principal", size="5", margin_top="1em"),
            image_upload_component(BlogAddPostFormState),
            rx.text_area(name="content", placeholder="Escribe tu artículo aquí...", required=True, height='50vh', width='100%'),
            rx.button("Guardar y Editar", type="submit", margin_top="1em"),
            align_items="start",
            spacing="4"
        ),
        on_submit=BlogAddPostFormState.handle_submit,
        reset_on_submit=True,
    )

def blog_post_edit_form() -> rx.Component:
    """El formulario para EDITAR un post existente."""
    return rx.form(
        rx.box(rx.input(type='hidden', name='post_id', value=BlogEditFormState.post.id), display='none'),
        rx.vstack(
            rx.input(default_value=BlogEditFormState.post.title, name="title", required=True, width='100%'),
            rx.heading("Imagen Principal", size="5", margin_top="1em"),
            rx.cond(
                BlogEditFormState.post.image_url,
                rx.image(src=BlogEditFormState.post.image_url, height="10em", width="auto", border_radius="0.5em"),
            ),
            rx.text("Sube una nueva imagen para reemplazar la actual:", margin_top="0.5em"),
            image_upload_component(BlogEditFormState),
            rx.text_area(value=BlogEditFormState.post_content, on_change=BlogEditFormState.set_post_content, name='content', required=True, height='50vh', width='100%', margin_top="1em"),
            rx.flex(
                rx.switch(is_checked=BlogEditFormState.post_publish_active, on_change=BlogEditFormState.set_post_publish_active, name='publish_active'),
                rx.text("Publicar Artículo"),
                spacing="2",
                margin_top="1em",
            ),
            rx.cond(
                BlogEditFormState.post_publish_active,
                rx.hstack(
                    rx.input(default_value=BlogEditFormState.publish_display_date, type='date', name='publish_date'),
                    rx.input(default_value=BlogEditFormState.publish_display_time, type='time', name='publish_time'),
                ),
            ),
            rx.button("Guardar Cambios", type="submit", margin_top="1em"),
            align_items="start",
            spacing="4"
        ),
        on_submit=BlogEditFormState.handle_submit,
    )