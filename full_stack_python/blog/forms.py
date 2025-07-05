import reflex as rx
from .state import BlogPostState

def blog_post_form() -> rx.Component:
    """Un único formulario para crear y editar posts."""
    return rx.form(
        rx.vstack(
            rx.input(
                default_value=BlogPostState.post.title if BlogPostState.post else "",
                name="title", placeholder="Título de la publicación", required=True, width='100%'
            ),
            rx.text_area(
                value=BlogPostState.post_content, on_change=BlogPostState.set_post_content,
                placeholder='Escribe aquí tu publicación...', required=True, height='30vh', width='100%'
            ),
            rx.heading("Imágenes", size="4", margin_top="1em"),
            rx.grid(
                rx.foreach(
                    BlogPostState.image_previews, # Itera sobre la lista simple de URLs
                    lambda url: rx.box(
                        rx.image(src=url, width="100px", height="100px", object_fit="cover", border_radius="sm"),
                        rx.icon_button(
                            "trash-2", on_click=BlogPostState.delete_preview_image(url),
                            size="1", position="absolute", top="2px", right="2px",
                            color_scheme="red", variant="soft",
                        ),
                        position="relative",
                    )
                ),
                columns="5", spacing="2", width="100%"
            ),
            rx.upload(
                rx.text("Arrastra imágenes aquí o haz clic"), id="image_upload",
                accept={"image/png": [".png"], "image/jpeg": [".jpg", ".jpeg"]},
                multiple=True, max_files=10, border="2px dashed #60a5fa", padding="2em",
                on_drop=BlogPostState.handle_upload(rx.upload_files(upload_id="image_upload")),
            ),
            rx.flex(
                rx.switch(is_checked=BlogPostState.post_publish_active, on_change=BlogPostState.set_post_publish_active),
                rx.text("Publicar"),
                spacing="2", margin_top="1em",
            ),
            rx.cond(
                BlogPostState.post_publish_active,
                rx.hstack(
                    rx.input(value=BlogPostState.publish_date_str, on_change=BlogPostState.set_publish_date_str, type='date', width='100%'),
                    rx.input(value=BlogPostState.publish_time_str, on_change=BlogPostState.set_publish_time_str, type='time', width='100%'),
                    width='100%'
                ),
            ),
            rx.button("Guardar Publicación", type="submit", margin_top="1em"),
            spacing="4", align_items="start"
        ),
        on_submit=BlogPostState.handle_submit,
        reset_on_submit=True
    )