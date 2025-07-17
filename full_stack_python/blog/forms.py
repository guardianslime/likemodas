import reflex as rx
from .state import BlogAddFormState, BlogEditFormState

def blog_post_add_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.input(
                placeholder="Nombre del producto",
                name="title",
                on_change=BlogAddFormState.set_title,
                required=True,
            ),
            rx.input(
                placeholder="Precio",
                name="price",
                type="number",
                on_change=BlogAddFormState.set_price_from_input,
                required=True,
            ),
            rx.text_area(
                placeholder="Descripción del producto",
                name="content",
                on_change=BlogAddFormState.set_content,
                required=True,
            ),
            rx.upload(
                rx.text("Subir imágenes del producto"),
                id="blog_upload",
                multiple=True,
                max_files=5,
                accept={"image/*": [".jpg", ".png", ".jpeg", ".webp"]},
                on_drop=BlogAddFormState.handle_upload(rx.upload_files("blog_upload")),
            ),
            rx.cond(
                BlogAddFormState.temp_images,
                rx.hstack(
                    rx.foreach(
                        BlogAddFormState.temp_images,
                        lambda img: rx.box(
                            rx.image(src=rx.get_upload_url(img), width="100px"),
                            rx.icon(
                                tag="trash",
                                on_click=BlogAddFormState.remove_image(img),
                                color="red.500",
                            ),
                            style={"position": "relative", "margin": "0.5em"},
                        ),
                    )
                )
            ),
            rx.button("Publicar", type="submit", color_scheme="green"),
            spacing="4",
        ),
        on_submit=BlogAddFormState.submit,
        width="100%",
        max_width="600px",
        padding="2em",
    )

def blog_post_edit_form() -> rx.Component:
    return rx.cond(
        BlogEditFormState.post,
        rx.form(
            rx.vstack(
                # --- ✨ CORRECCIONES EN TODO EL FORMULARIO ✨ ---
                # Cada campo ahora está vinculado a su propia variable de estado
                rx.input(
                    name="title",
                    value=BlogEditFormState.form_title,
                    on_change=BlogEditFormState.set_form_title,
                    placeholder="Título del Post",
                    required=True, width="100%",
                ),
                rx.input(
                    name="price",
                    value=BlogEditFormState.form_price_str,
                    on_change=BlogEditFormState.set_form_price_str,
                    placeholder="Precio",
                    required=True, width="100%",
                ),
                rx.text_area(
                    name="content",
                    value=BlogEditFormState.form_content,
                    on_change=BlogEditFormState.set_form_content,
                    placeholder="Escribe tu contenido aquí...",
                    required=True, height="40vh", width="100%",
                ),
                rx.flex(
                    rx.switch(
                        is_checked=BlogEditFormState.form_publish_active,
                        on_change=BlogEditFormState.set_form_publish_active,
                    ),
                    rx.text("Publicar"),
                    spacing="2",
                ),
                rx.cond(
                    BlogEditFormState.form_publish_active,
                    rx.hstack(
                        rx.input(
                            type="date",
                            value=BlogEditFormState.form_publish_date_str,
                            on_change=BlogEditFormState.set_form_publish_date_str,
                        ),
                        rx.input(
                            type="time",
                            value=BlogEditFormState.form_publish_time_str,
                            on_change=BlogEditFormState.set_form_publish_time_str,
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