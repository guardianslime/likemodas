# full_stack_python/blog/forms.py

# ... (El resto del archivo no cambia) ...

def blog_post_edit_form() -> rx.Component:
    """El formulario para EDITAR una publicación de blog existente."""
    post = BlogEditFormState.post
    return rx.form(
        rx.box(
            # --- CORRECCIÓN FINAL ---
            # Ahora el valor viene de una variable de texto simple (post_id_str),
            # lo que elimina cualquier ambigüedad para el compilador.
            rx.input(
                type='hidden', 
                name='post_id', 
                value=BlogEditFormState.post_id_str
            ),
            display='none'
        ),
        rx.vstack(
            rx.input(
                default_value=rx.cond(post, post.title, ""),
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
            rx.heading("Imágenes", size="4", margin_top="1em"),
            rx.grid(
                rx.foreach(
                    BlogEditFormState.preview_image_urls,
                    lambda url: rx.image(src=url, width="100px", height="100px", object_fit="cover", border_radius="sm")
                ),
                columns="5",
                spacing="2",
                width="100%"
            ),
            image_upload_component(),
            rx.flex(
                rx.switch(
                    is_checked=BlogEditFormState.post_publish_active,
                    on_change=BlogEditFormState.set_post_publish_active,
                    name='publish_active',
                ),
                rx.text("Publicar"),
                spacing="2",
                margin_top="1em",
            ),
            rx.cond(
                BlogEditFormState.post_publish_active,
                rx.hstack(
                    rx.input(
                        value=BlogEditFormState.publish_date_str,
                        on_change=BlogEditFormState.set_publish_date_str,
                        type='date',
                        name='publish_date',
                        width='100%'
                    ),
                    rx.input(
                        value=BlogEditFormState.publish_time_str,
                        on_change=BlogEditFormState.set_publish_time_str,
                        type='time',
                        name='publish_time',
                        width='100%'
                    ),
                    width='100%'
                ),
            ),
            rx.button("Guardar Cambios", type="submit", margin_top="1em"),
            spacing="4",
            align_items="start"
        ),
        on_submit=BlogEditFormState.handle_submit,
    )