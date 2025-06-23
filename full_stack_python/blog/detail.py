import reflex as rx 

from ..ui.base import base_page
from . import state
from .notfound import blog_post_not_found

# --- MEJORA: Añadir la ruta dinámica y la carga de datos en el decorador ---
# Esto es crucial para que la página funcione cuando accedes a la URL directamente.
@rx.page(route="/blog/[blog_id]", on_load=state.BlogPostState.get_post_detail)
def blog_post_detail_page() -> rx.Component:
    
    # --- MEJORA: Lógica para mostrar el botón de edición solo si el post pertenece al usuario logueado ---
    is_owner = (
        state.BlogPostState.is_authenticated & 
        (state.BlogPostState.post.userinfo_id == state.BlogPostState.my_userinfo_id)
    )

    # --- CORRECCIÓN: Usar rx.cond para renderizar de forma segura la información del usuario ---
    user_info_display = rx.cond(
        state.BlogPostState.post.userinfo,
        # Si userinfo existe, muestra los detalles
        rx.hstack(
            rx.avatar(fallback=state.BlogPostState.post.userinfo.user.email[0].upper() if state.BlogPostState.post.userinfo.user else "A"),
            rx.text(
                "Por ",
                rx.link(
                    state.BlogPostState.post.userinfo.user.email if state.BlogPostState.post.userinfo.user else "Usuario desconocido",
                    font_weight="bold",
                ),
                color_scheme="gray",
            ),
            spacing="3",
            align="center",
        ),
        # Si no, muestra un texto alternativo
        rx.text("Cargando autor...", color_scheme="gray")
    )

    content = rx.vstack(
        rx.hstack(
            rx.heading(state.BlogPostState.post.title, size="8", text_align="left"),
            # Mostrar el botón de editar solo al propietario
            rx.cond(
                is_owner,
                rx.link(
                    rx.button("Editar Post", color_scheme="grass"),
                    href=state.BlogPostState.blog_post_edit_url,
                ),
            ),
            justify="between",
            align="start",
            width="100%",
        ),
        user_info_display,
        rx.text(
            "Publicado el: ",
            # Formatear la fecha para que sea más legible
            rx.text(
                state.BlogPostState.post.publish_date.to_string(
                    locale="es-ES", 
                    date_style="full", 
                    time_style="short"
                ), 
                as_="span"
            ),
            color_scheme="gray",
        ),
        rx.divider(width="100%"),
        rx.box(
            rx.markdown(
                state.BlogPostState.post.content,
                component_map={
                    "a": lambda text, **props: rx.link(text, **props, color_scheme="grass"),
                }
            ),
            padding_top="1rem",
            width="100%",
            align="start",
        ),
        spacing="5",
        align="start",
        width="100%",
        max_width="960px",
        padding="1rem",
    )

    # Vista principal que muestra el contenido solo si el post se ha cargado
    main_component = rx.cond(
        state.BlogPostState.post, 
        content,
        blog_post_not_found()
    )
    
    return base_page(
        rx.center(
            main_component,
            min_height="85vh",
        )
    )
