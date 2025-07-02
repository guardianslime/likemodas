import reflex as rx 


from .state import (
    BlogAddPostFormState,
    BlogEditFormState
)

# --- AÑADE ESTE COMPONENTE REUTILIZABLE ---
def image_upload_component(State: rx.State) -> rx.Component:
    """Un componente para subir la imagen del post y mostrar una vista previa."""
    return rx.vstack(
        rx.upload.root(
            rx.box(
                rx.icon(
                    tag="cloud_upload",
                    style={"width": "3rem", "height": "3rem", "color": "#2563eb", "marginBottom": "0.75rem"},
                ),
                rx.hstack(
                    rx.text("Click to upload", style={"fontWeight": "bold", "color": "#1d4ed8"}),
                    " or drag and drop",
                    style={"fontSize": "0.875rem", "color": "#4b5563"},
                ),
                rx.text(
                    "SVG, PNG, JPG or GIF (MAX. 5MB)",
                    style={"fontSize": "0.75rem", "color": "#6b7280", "marginTop": "0.25rem"},
                ),
                style={
                    "display": "flex", "flexDirection": "column", "alignItems": "center",
                    "justifyContent": "center", "padding": "1.5rem", "textAlign": "center",
                },
            ),
            id="my_upload",
            style={
                "maxWidth": "24rem", "height": "16rem", "borderWidth": "2px", "borderStyle": "dashed",
                "borderColor": "#60a5fa", "borderRadius": "0.75rem", "cursor": "pointer",
            },
            on_drop=State.handle_upload(rx.upload.files()),
        ),
        # Vista previa de la imagen que se está subiendo
        rx.flex(
            rx.foreach(
                State.img,
                lambda image: rx.image(src=image, height="8em", width="auto", border_radius="0.5em"),
            ),
            spacing="2",
            margin_top="1rem",
        ),
        align="center",
        spacing="4",
        width="100%",
    )
# ---------------------------------------------



def blog_post_add_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.input(
                name="title",
                placeholder="Título del Artículo",
                required=True,
                width="100%",
            ),
            rx.heading("Imagen Principal", size="5", margin_top="1em"),
            image_upload_component(BlogAddPostFormState), # <-- AÑADE ESTO
            rx.text_area(
                name="content",
                placeholder="Escribe tu artículo aquí...",
                required=True,
                height='50vh',
                width='100%',
                margin_top="1em",
            ),
            rx.button("Guardar y Editar", type="submit", margin_top="1em"),
        ),
        on_submit=BlogAddPostFormState.handle_submit,
        reset_on_submit=True,
    )


from .state import BlogEditFormState

def blog_post_edit_form() -> rx.Component:
    post = BlogEditFormState.post
    title = post.title
    publish_active = post.publish_active
    post_content = BlogEditFormState.post_content
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
            
            rx.heading("Imagen Principal", size="5", margin_top="1em"),
            # Muestra la imagen actual si existe
            rx.cond(
                post.image_url,
                rx.vstack(
                    rx.text("Imagen Actual:"),
                    rx.image(src=post.image_url, height="10em", width="auto", border_radius="0.5em"),
                    margin_bottom="1em",
                )
            ),
            rx.text("Sube una nueva imagen para reemplazar la actual:"),
            image_upload_component(BlogEditFormState), # <-- AÑADE ESTO

            rx.text_area(
                value=BlogEditFormState.post_content,
                on_change=BlogEditFormState.set_post_content,
                name='content',
                required=True,
                height='50vh',
                width='100%',
                margin_top="1em",
            ),
            # ... (resto de los campos como el switch de publicación y la fecha) ...
            rx.flex(
                rx.switch(
                    default_checked=BlogEditFormState.post_publish_active,
                    on_change=BlogEditFormState.set_post_publish_active,
                    name='publish_active',
                ),
                rx.text("Publicar Artículo"),
                spacing="2",
            ),
            # ...
            rx.button("Guardar Cambios", type="submit"),
            spacing="4"
        ),
        on_submit=BlogEditFormState.handle_submit,
    )
