import reflex as rx
from ..auth.admin_auth import require_admin
from ..state import AppState
from .notfound import blog_post_not_found

def _image_section() -> rx.Component:
    """Muestra las imágenes del post del admin usando el carrusel nativo."""
    FIXED_HEIGHT = "500px"

    # --- USANDO EL CARRUSEL NATIVO Y SEGURO ---
    native_carousel = rx.box(
        rx.image(
            src=rx.get_upload_url(AppState.current_image_url),
            alt=AppState.post.title,
            width="100%",
            height="100%",
            object_fit="cover",
        ),
        rx.button(
            rx.icon(tag="chevron-left"),
            on_click=AppState.prev_image,
            position="absolute", top="50%", left="0.5rem",
            transform="translateY(-50%)", variant="soft", color_scheme="gray",
        ),
        rx.button(
            rx.icon(tag="chevron-right"),
            on_click=AppState.next_image,
            position="absolute", top="50%", right="0.5rem",
            transform="translateY(-50%)", variant="soft", color_scheme="gray",
        ),
        position="relative", width="100%", height=FIXED_HEIGHT,
        border_radius="var(--radius-3)", overflow="hidden",
    )

    placeholder_component = rx.box(
        rx.vstack(
            rx.icon("image_off", size=48, color=rx.color("gray", 8)),
            rx.text("Sin imagen disponible"),
            align="center", justify="center"
        ),
        width="100%", height=FIXED_HEIGHT, bg=rx.color("gray", 3),
        border_radius="var(--radius-3)", display="flex",
    )

    return rx.box(
        rx.cond(
            AppState.post & AppState.post.image_urls,
            native_carousel,
            placeholder_component
        ),
        width="100%", max_width="800px", margin="auto", padding_y="1em"
    )

def _info_section() -> rx.Component:
    """Muestra la info del post del admin."""
    return rx.vstack(
        rx.text(AppState.post.title, size="7", font_weight="bold"),
        rx.text(AppState.post.price_cop, size="6", color="gray"),
        rx.text(AppState.post.content, size="4", margin_top="1em", white_space="pre-wrap"),
        rx.spacer(),
        rx.hstack(
            rx.button(rx.cond(AppState.post.publish_active, "Despublicar", "Publicar"), on_click=AppState.toggle_publish_status(AppState.post.id)),
            rx.link(rx.button("Editar Post", variant="soft"), href=AppState.blog_post_edit_url),
            rx.button("Eliminar Post", color_scheme="red", on_click=AppState.delete_post(AppState.post.id)),
            spacing="4", margin_top="2em"
        ),
        padding="1em", align="start", width="100%",
    )

@require_admin
def blog_post_detail_content() -> rx.Component:
    """Página que muestra el detalle de un post del admin."""
    return rx.center(
        rx.vstack(
            rx.heading("Detalle de mi Publicación", size="8", margin_bottom="1em"),
            rx.cond(
                AppState.post,
                rx.grid(_image_section(), _info_section(), columns="2", spacing="4", align_items="start", width="100%", max_width="1120px"),
                blog_post_not_found()
            ),
            spacing="6", width="100%", padding="2em", align="center",
        ),
        width="100%",
    )