# likemodas/blog/public_page.py (Corregido)

import reflex as rx
import math
from ..state import AppState, CommentData, ModalSelectorDTO
from ..ui.components import product_gallery_component
from ..ui.filter_panel import floating_filter_panel
from ..ui.skeletons import skeleton_product_detail_view, skeleton_product_gallery

def star_rating_display(rating: rx.Var[float], count: rx.Var[int]) -> rx.Component:
    """Componente para mostrar estrellas de valoración de forma robusta."""
    full_stars = rx.Var.range(rx.call_script(f"Math.floor({rating})", read_exec=True))
    has_half_star = (rating - rx.call_script(f"Math.floor({rating})", read_exec=True)) >= 0.5
    empty_stars = rx.Var.range(5 - rx.call_script(f"Math.ceil({rating})", read_exec=True))
    
    return rx.cond(
        count > 0,
        rx.hstack(
            rx.foreach(full_stars, lambda _: rx.icon("star", color="gold", size=20)),
            rx.cond(has_half_star, rx.icon("star_half", color="gold", size=20)),
            rx.foreach(empty_stars, lambda _: rx.icon("star", color=rx.color("gray", 8), size=20)),
            rx.text(f"{rating:.1f} de 5 ({count} opiniones)", size="3", color_scheme="gray", margin_left="0.5em"),
            align="center", spacing="1",
        ),
        rx.text("Aún no hay opiniones para este producto.", size="3", color_scheme="gray")
    )

def render_update_item(comment: CommentData) -> rx.Component:
    """Componente para mostrar una actualización de un comentario."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("pencil", size=16, margin_right="0.5em"),
                rx.text("Actualización:", weight="bold"),
                star_rating_display(comment.rating, 1), # <-- CORREGIDO
                rx.spacer(),
                rx.text(f"Fecha: {comment.created_at_formatted}", size="2", color_scheme="gray"),
                width="100%"
            ),
            rx.text(comment.content, margin_top="0.25em", white_space="pre-wrap"),
            align_items="start",
            spacing="1"
        ),
        padding="0.75em",
        border="1px dashed",
        border_color=rx.color("gray", 6),
        border_radius="md",
        margin_top="1em",
        margin_left="2.5em"
    )

def review_submission_form() -> rx.Component:
    """Muestra el formulario para opinar."""
    return rx.cond(
        AppState.show_review_form,
        rx.form(
            rx.vstack(
                rx.heading(rx.cond(AppState.my_review_for_product, "Actualiza tu opinión", "Deja tu opinión"), size="5"),
                rx.text("Tu valoración:"),
                rx.hstack(
                    rx.foreach(
                        rx.Var.range(5),
                        lambda i: rx.icon(
                            "star",
                            color=rx.cond(AppState.review_rating > i, "gold", rx.color("gray", 8)),
                            on_click=AppState.set_review_rating(i + 1),
                            cursor="pointer",
                            size=32
                        )
                    )
                ),
                rx.text_area(
                    name="review_content",
                    placeholder="Escribe tu opinión aquí...",
                    value=AppState.review_content,
                    on_change=AppState.set_review_content,
                    width="100%",
                ),
                rx.button(rx.cond(AppState.my_review_for_product, "Actualizar Opinión", "Enviar Opinión"), type="submit", width="100%"),
                spacing="3", padding="1.5em", border="1px solid",
                border_color=rx.color("gray", 6), border_radius="md", width="100%",
            ),
            on_submit=AppState.submit_review,
        ),
        rx.cond(
            AppState.review_limit_reached,
            rx.callout(
                "Has alcanzado el límite de actualizaciones para esta compra.",
                icon="info", margin_top="1.5em", width="100%"
            ),
            rx.fragment()
        )
    )

def render_comment_item(comment: CommentData) -> rx.Component:
    """Renderiza un comentario principal con su historial."""
    update_count = rx.cond(comment.updates, comment.updates.length(), 0)
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.avatar(fallback=comment.author_initial, size="2"),
                rx.text(comment.author_username, weight="bold"),
                rx.spacer(),
                star_rating_display(comment.rating, 1), # <-- CORREGIDO
                width="100%",
            ),
            rx.text(comment.content, margin_top="0.5em", white_space="pre-wrap"),
            rx.cond(
                comment.updates,
                rx.button(
                    rx.cond(
                        AppState.expanded_comments.get(comment.id, False),
                        "Ocultar historial",
                        rx.text("Ver historial (", rx.text(update_count, as_="span"), " actualizaciones)")
                    ),
                    on_click=AppState.toggle_comment_updates(comment.id),
                    variant="soft", size="1", margin_top="0.5em"
                )
            ),
            # --- BLOQUE DE CORRECCIÓN CRÍTICA ---
            # Se asegura de que 'comment.updates' exista antes de intentar el bucle.
            rx.cond(
                AppState.expanded_comments.get(comment.id, False),
                rx.cond(
                    comment.updates,
                    rx.foreach(comment.updates, render_update_item)
                )
            ),
            # --- FIN DE LA CORRECCIÓN ---
            rx.hstack(
                rx.text(f"Publicado: {comment.created_at_formatted}", size="2", color_scheme="gray"),
                width="100%", justify="end", spacing="1", margin_top="1em"
            ),
            align_items="start", spacing="2"
        ),
        padding="1em", border_bottom="1px solid", border_color=rx.color("gray", 4), width="100%"
    )

def product_detail_modal() -> rx.Component:
    """El diálogo modal que muestra los detalles del producto."""
    
    def _modal_image_section() -> rx.Component:
        FIXED_HEIGHT = "500px"
        return rx.vstack(
            rx.box(
                rx.cond(
                    AppState.current_modal_image_filename,
                    rx.image(
                        src=rx.get_upload_url(AppState.current_modal_image_filename),
                        alt=AppState.product_in_modal.title,
                        width="100%", height="100%", object_fit="cover",
                    ),
                    rx.box(
                        rx.icon("image_off", size=48), 
                        width="100%", height="100%", display="flex", 
                        align_items="center", justify_content="center", 
                        bg=rx.color("gray", 3)
                    ),
                ),
                position="relative", width="100%", height=FIXED_HEIGHT, 
                border_radius="var(--radius-3)", overflow="hidden",
            ),
            rx.cond(
                AppState.unique_modal_variants.length() > 1,
                rx.hstack(
                    rx.foreach(
                        AppState.unique_modal_variants,
                        lambda item: rx.box(
                            rx.image(
                                src=rx.get_upload_url(item.variant.get("image_url")),
                                width="60px", height="60px", object_fit="cover", border_radius="md"
                            ),
                            border_width=rx.cond(AppState.current_modal_image_filename == item.variant.get("image_url"), "2px", "1px"),
                            border_color=rx.cond(AppState.current_modal_image_filename == item.variant.get("image_url"), "violet", "gray"),
                            padding="2px", border_radius="lg", cursor="pointer",
                            on_click=AppState.set_modal_variant_index(item.index),
                        )
                    ),
                    spacing="3", padding="0.5em", width="100%", overflow_x="auto",
                )
            ),
            spacing="3", width="100%",
        )

    def _modal_info_section() -> rx.Component:
        return rx.vstack(
            rx.text(AppState.product_in_modal.title, size="8", font_weight="bold", text_align="left"),
            rx.text("Publicado el " + AppState.product_in_modal.created_at_formatted, size="3", color_scheme="gray", text_align="left"),
            rx.text(AppState.product_in_modal.price_cop, size="7", color_scheme="gray", text_align="left"),
            star_rating_display(AppState.product_in_modal.average_rating, AppState.product_in_modal.rating_count), # <-- CORREGIDO
            rx.hstack(
                rx.badge(
                    AppState.product_in_modal.shipping_display_text,
                    color_scheme=rx.cond(AppState.product_in_modal.shipping_cost == 0.0, "green", "gray"),
                    variant="solid", size="2"
                ),
                rx.cond(
                    AppState.product_in_modal.is_moda_completa_eligible,
                    rx.tooltip(
                        rx.badge("Moda Completa", color_scheme="violet", variant="solid", size="2"),
                        content="Este item cuenta para el envío gratis en compras sobre $200.000"
                    ),
                ),
                rx.cond(
                    AppState.product_in_modal.is_imported,
                    rx.badge("Importado", color_scheme="purple", variant="solid", size="2"),
                ),
                spacing="4", align="center", margin_y="1em",
            ),
            rx.text(AppState.product_in_modal.content, size="4", margin_top="1em", white_space="pre-wrap", text_align="left"),
            
            rx.vstack(
                rx.divider(margin_y="1em"),
                rx.heading("Características", size="4"),
                
                rx.foreach(
                    AppState.current_variant_display_attributes.items(),
                    lambda item: rx.hstack(
                        rx.text(f"{item[0]}:", weight="bold", size="3"),
                        rx.text(item[1], size="3"),
                        spacing="3",
                        align_items="center",
                        width="100%"
                    ),
                ),

                rx.foreach(
                    AppState.modal_attribute_selectors,
                    lambda selector: rx.vstack(
                        rx.text(selector.key, weight="bold", size="3"),
                        rx.segmented_control.root(
                            rx.foreach(
                                selector.options,
                                lambda option: rx.segmented_control.item(option, value=option)
                            ),
                            on_change=lambda value: AppState.set_modal_selected_attribute(selector.key, value),
                            value=selector.current_value,
                        ),
                        align_items="start",
                        width="100%",
                        spacing="2"
                    )
                ),
                align_items="start", width="100%", spacing="3", margin_top="0.5em",
            ),
            
            rx.text(
                "Publicado por: ",
                rx.link(
                    AppState.product_in_modal.seller_name,
                    href=f"/vendedor?id={AppState.product_in_modal.seller_id}",
                    color_scheme="violet", font_weight="bold",
                ),
                size="3", color_scheme="gray", margin_top="1.5em",
                text_align="left", width="100%"
            ),
            rx.spacer(),
            rx.hstack(
                rx.button("Añadir al Carrito", on_click=AppState.add_to_cart(AppState.product_in_modal.id), size="3", flex_grow="1"),
                rx.icon_button(
                    rx.cond(AppState.is_current_post_saved, rx.icon(tag="bookmark-minus"), rx.icon(tag="bookmark-plus")),
                    on_click=AppState.toggle_save_post,
                    size="3", variant="outline",
                ),
                rx.icon_button(
                    rx.icon(tag="share-2"),
                    on_click=[
                        rx.set_clipboard(AppState.base_app_url + "/?product=" + AppState.product_in_modal.id.to_string()),
                        rx.toast.success("¡Enlace para compartir copiado!")
                    ],
                    size="3", variant="outline",
                ),
                spacing="3", width="100%", margin_top="1.5em",
            ),
            align="start", height="100%",
        )
    
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.close(rx.icon_button(rx.icon("x"), variant="soft", color_scheme="gray", style={"position": "absolute", "top": "1rem", "right": "1rem"})),
            rx.cond(
                AppState.product_in_modal,
                rx.vstack(
                    rx.grid(
                        _modal_image_section(),
                        _modal_info_section(),
                        columns={"initial": "1", "md": "2"},
                        spacing="6", align_items="start", width="100%",
                    ),
                    rx.divider(margin_y="1.5em"),
                    review_submission_form(),
                    rx.cond(
                        AppState.product_comments,
                        rx.vstack(
                            rx.heading("Opiniones del Producto", size="6", margin_top="1em"),
                            rx.foreach(AppState.product_comments, render_comment_item),
                            spacing="1", width="100%", max_height="400px", overflow_y="auto"
                        )
                    )
                ),
                skeleton_product_detail_view(),
            ),
            style={"max_width": "1200px", "min_height": "600px"},
        ),
        open=AppState.show_detail_modal,
        on_open_change=AppState.close_product_detail_modal,
    )

def blog_public_page_content() -> rx.Component:
    """Página pública principal que muestra la galería y contiene el modal."""
    return rx.center(
        rx.vstack(
            floating_filter_panel(),
            rx.cond(
                AppState.is_loading,
                skeleton_product_gallery(),
                product_gallery_component(posts=AppState.displayed_posts)
            ),
            product_detail_modal(),
            spacing="6", width="100%", padding="2em", align="center"
        ),
        width="100%"
    )