import reflex as rx

# Asumo que estos son los imports correctos según la estructura de tu proyecto.
from ..ui.base import base_page
from . import state
from .notfound import blog_post_not_found

# --- MEJORA: Definir la ruta directamente en el decorador de la página. ---
# El uso de "[post_id]" en la ruta la convierte en una ruta dinámica.
# Por ejemplo, ahora podrás navegar a "/blog/1", "/blog/mi-primer-post", etc.
# El evento `on_load` llama al manejador `get_post` del estado para cargar
# los datos del post correspondiente antes de que la página se renderice.
@rx.page(route="/blog/[post_id]", on_load=state.BlogPostState.get_post)
def blog_post_detail_page() -> rx.Component:
    """
    Página de detalles para una única publicación del blog.
    Carga los datos del post basándose en el 'post_id' de la URL.
    """

    # --- MEJORA: Lógica para mostrar el botón de edición solo al autor del post. ---
    # Esto es más seguro y práctico que tener una variable `con_edit` estática.
    # Asume que tienes un estado `UserState` que gestiona la información del usuario logueado.
    # Deberás ajustar `state.UserState.user.id` según cómo hayas modelado tu estado de usuario.
    is_owner = (
        state.UserState.is_authenticated &
        (state.BlogPostState.post.userinfo.user.id == state.UserState.user.id)
    )

    # --- El contenido principal de la página ---
    # Este Vstack se muestra solo si el post se ha cargado correctamente.
    content = rx.vstack(
        rx.hstack(
            rx.heading(state.BlogPostState.post.title, size="9"),
            # El enlace de "Editar" ahora se muestra condicionalmente.
            rx.cond(
                is_owner,
                rx.link(
                    "Editar Post",
                    href=state.BlogPostState.blog_post_edit_url,
                    button=True, # Hace que el enlace parezca un botón.
                    color_scheme="grass",
                ),
            ),
            justify="between", # Alinea el título a la izquierda y el botón a la derecha.
            align="center",
            width="100%",
        ),
        rx.hstack(
            # --- CORRECCIÓN: Mostrar datos del usuario directamente. ---
            # En lugar de `to_string()`, accedemos a los atributos del objeto,
            # como `username`. Asumo que tu modelo de usuario tiene este atributo.
            rx.avatar(fallback=state.BlogPostState.post.userinfo.user.username[0].upper()),
            rx.text(
                "Por ",
                rx.link(
                    state.BlogPostState.post.userinfo.user.username,
                    # Podrías enlazar a una página de perfil de usuario aquí.
                    # href=f"/perfil/{state.BlogPostState.post.userinfo.user.username}"
                    font_weight="bold",
                ),
                " el ",
                rx.text(state.BlogPostState.post.publish_date, as_="span"),
                color_scheme="gray",
            ),
            spacing="3",
            align="center",
        ),
        rx.divider(),
        # --- MEJORA: Usar rx.markdown para renderizar el contenido. ---
        # Si tu contenido está en formato Markdown, este componente lo formateará
        # correctamente (párrafos, negritas, listas, etc.).
        # Si es solo texto plano, puedes usar `rx.text` como lo tenías antes.
        rx.box(
            rx.markdown(
                state.BlogPostState.post.content,
                component_map={
                    "a": lambda text, **props: rx.link(text, **props, color_scheme="grass"),
                }
            ),
            width="100%",
            padding_top="1rem",
        ),
        spacing="5",
        align="start", # Alinear el contenido a la izquierda mejora la legibilidad.
        width="100%",
        max_width="960px", # Establecer un ancho máximo es bueno para pantallas grandes.
        padding="1rem",
    )

    # --- MEJORA: Usar una variable de estado para controlar la vista. ---
    # `is_post_loaded` (que deberías añadir a tu `BlogPostState`) te permite
    # mostrar una vista de carga o de "no encontrado" de forma más limpia.
    main_component = rx.cond(
        state.BlogPostState.is_post_loaded,
        content,
        blog_post_not_found() # Tu componente para cuando el post no se encuentra.
    )

    # Envolvemos el contenido en el diseño de la página base y lo centramos.
    return base_page(
        rx.center(
            main_component,
            min_height="85vh",
        )
    )
