import reflex as rx 

from ..ui.base import base_page
from . import state
from .notfound import blog_post_not_found

@rx.page(route="/blog/[blog_id]", on_load=state.BlogPostState.get_post_detail)
def blog_post_detail_page() -> rx.Component:
    """
    Muestra la página de detalles de un solo post del blog.
    CORREGIDO para usar solo herramientas de Reflex en la UI.
    """
    
    is_owner = (
        state.BlogPostState.is_authenticated & 
        (state.BlogPostState.post.userinfo_id == state.BlogPostState.my_userinfo_id)
    )

    # CORRECCIÓN: Lógica condicional usando rx.cond para evitar errores de tipo.
    user_info_display = rx.cond(
        state.BlogPostState.post.userinfo,
        rx.hstack(
            # Se usa el primer caracter del email como fallback. No se usa .upper().
            rx.avatar(fallback=state.BlogPostState.post.userinfo.email[0]),
            rx.text(
                "Por ",
                rx.link(
                    state.BlogPostState.post.userinfo.email,
                    font_weight="bold",
                ),
                color_scheme="gray",
            ),
            spacing="3",
            align="center",
        ),
        rx.text("Cargando autor...", color_scheme="gray")
    )

    # CORRECCIÓN: Lógica para mostrar la fecha de publicación.
    publish_date_display = rx.cond(
        state.BlogPostState.post.publish_active & state.BlogPostState.post.publish_date,
         rx.text(
            "Publicado el: ",
            # No se puede usar .strftime(). Usamos .to_string() sin argumentos.
            rx.text(state.BlogPostState.post.publish_date.to_string(), as_="span"),
            color_scheme="gray",
        ),
        rx.text("No publicado", color_scheme="gray"),
    )

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
