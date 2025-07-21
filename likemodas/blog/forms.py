import reflex as rx
from .state import BlogAddFormState, BlogEditFormState

def blog_post_add_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.input(
                placeholder="Nombre del producto",
                value=BlogAddFormState.title,
                on_change=BlogAddFormState.set_title,
                required=True,
            ),
            rx.input(
                placeholder="Precio",
                type="number",
                value=str(BlogAddFormState.price),
                on_change=BlogAddFormState.set_price_from_input,
                required=True,
            ),
            rx.text_area(
                placeholder="Descripción del producto",
                value=BlogAddFormState.content,
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
            rx.hstack(
                rx.button(
                    "Subir", 
                    on_click=BlogAddFormState.submit,
                    variant="soft", # Estilo más suave para la acción secundaria
                ),
                rx.button(
                    "Publicar Ahora", 
                    on_click=BlogAddFormState.submit_and_publish, 
                    color_scheme="green"
                ),
                spacing="4",
                width="100%",
                justify="end" # Alinea los botones a la derecha
            ),
            # --- FIN DE LA MODIFICACIÓN ---
            
            spacing="4",
        ),
        width="100%",
        max_width="600px",
        padding="2em",
    )

def blog_post_edit_form() -> rx.Component:
    return rx.cond(
        BlogEditFormState.post,
        rx.form(
            rx.vstack(
                # ID oculto
                rx.input(
                    type="hidden",
                    name="post_id",
                    value=rx.cond(
                        BlogEditFormState.post.id,
                        BlogEditFormState.post.id,
                        ""
                    ),
                ),
                # Título
                rx.input(
                    name="title",
                    value=rx.cond(
                        BlogEditFormState.post.title,
                        BlogEditFormState.post.title,
                        ""
                    ),
                    placeholder="Título del Post",
                    required=True,
                    width="100%",
                ),
                # Precio (CORREGIDO)
                rx.input(
                    name="price",
                    value=BlogEditFormState.price_str,
                    on_change=BlogEditFormState.set_price,
                    placeholder="Precio",
                    required=True,
                    width="100%",
                ),
                # Contenido
                rx.text_area(
                    name="content",
                    value=rx.cond(
                        BlogEditFormState.post_content != "",
                        BlogEditFormState.post_content,
                        ""
                    ),
                    on_change=BlogEditFormState.set_post_content,
                    placeholder="Escribe tu contenido aquí...",
                    required=True,
                    height="40vh",
                    width="100%",
                ),
                # Switch para publicar
                rx.flex(
                    rx.switch(
                        name="publish_active",
                        is_checked=BlogEditFormState.post_publish_active,
                        on_change=BlogEditFormState.set_post_publish_active,
                    ),
                    rx.text("Publicar"),
                    spacing="2",
                ),
                # Campos de fecha y hora si se publica
                rx.cond(
                    BlogEditFormState.post_publish_active,
                    rx.hstack(
                        rx.input(
                            name="publish_date",
                            type="date",           
                        ),
                        rx.input(
                            name="publish_time",
                            type="time",
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