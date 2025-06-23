import reflex as rx 

from ..ui.base import base_page
from . import state
from .notfound import blog_post_not_found

# Este decorador es la clave para que la página funcione bien en Railway.
# Carga los datos del post ANTES de intentar mostrar la página.
@rx.page(route="/blog/[blog_id]", on_load=state.BlogPostState.get_post_detail)
def blog_post_detail_page() -> rx.Component:
    """Muestra la página de detalles de un solo post del blog."""
    
    # Comprueba si el usuario logueado es el dueño del post.
    # Se usa para mostrar condicionalmente el botón de "Editar".
    is_owner = (
        state.BlogPostState.is_authenticated & 
        (state.BlogPostState.post.userinfo_id == state.BlogPostState.my_userinfo_id)
    )

    # Renderiza la información del autor de forma segura,
    # mostrando un texto de "Cargando..." si los datos aún no están listos.
    user_info_display = rx.cond(
        state.BlogPostState.post.userinfo,
        rx.hstack(
            rx.avatar(fallback=state.BlogPostState.post.userinfo.user.email[0].upper() if state.BlogPostState.post.userinfo.user else "A"),
            rx.text(
                "Por ",
                rx.link(
                    state.BlogPostState.post.userinfo.user.email if state.BlogPostState.post.userinfo.user else "Usuario desconocido",
                    font_weight="bold",
                    # podrías enlazar al perfil del usuario aquí
                ),
                color_scheme="gray",
            ),
            spacing="3",
            align="center",
        ),
        rx.text("Cargando autor...", color_scheme="gray")
    )
    
    # Muestra la fecha de publicación solo si el post está activo y tiene una fecha.
    publish_date_display = rx.cond(
        state.BlogPostState.post.publish_active & state.BlogPostState.post.publish_date,
         rx.text(
            "Publicado el ",
            # Usamos strftime para un formato de fecha y hora más amigable.
            rx.text(state.BlogPostState.post.publish_date.strftime("%d de %B de %Y a las %H:%M"), as_="span"),
            color_scheme="gray",
        ),
        rx.text("No publicado", color_scheme="gray"),
    )

    # Contenido principal de la página de detalles.
    content = rx.vstack(
        rx.hstack(
            rx.heading(state.BlogPostState.post.title, size="8", text_align="left"),
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
        publish_date_display,
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

    # Envoltura final: Muestra el contenido solo si self.post tiene datos,
    # de lo contrario, muestra la página de "no encontrado".
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
