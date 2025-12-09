# likemodas/blog/public_page.py

import reflex as rx
from ..state import AppState, CommentData
from ..ui.components import product_gallery_component, star_rating_display_safe
from ..ui.filter_panel import floating_filter_panel
from ..ui.skeletons import skeleton_product_detail_view, skeleton_product_gallery
from ..ui.reputation_icon import reputation_icon
from ..ui.vote_buttons import vote_buttons
from ..ui.seller_score import seller_score_stars
from ..models import UserReputation
from ..ui.custom_carousel import carousel


# --- NUEVA FUNCIÓN: Renderiza un item del historial (Hijo) ---
def render_update_item(update: CommentData) -> rx.Component:
    """Renderiza una actualización de opinión (versión anterior o nueva)."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("history", size=16, color_scheme="gray"),
                rx.text("Versión del historial", size="1", weight="bold", color_scheme="gray"),
                rx.spacer(),
                rx.text(update.created_at_formatted, size="1", color_scheme="gray"),
                width="100%",
                align="center"
            ),
            rx.divider(margin_y="0.5em"),
            rx.hstack(
                star_rating_display_safe(update.rating, 0, size=14),
                width="100%"
            ),
            rx.text(update.content, size="2", margin_top="0.25em", color_scheme="gray"),
            align_items="start", spacing="1"
        ),
        padding="0.75em",
        margin_top="0.5em",
        margin_left="1.5em", # Sangría para indicar jerarquía
        border_left="2px solid var(--gray-6)", # Línea vertical visual
        bg=rx.color("gray", 2),
        border_radius="0 8px 8px 0",
        width="95%"
    )

# --- FUNCIÓN MODIFICADA: Renderiza el comentario principal ---
def render_comment_item(comment: CommentData) -> rx.Component:
    # Calculamos cuántas actualizaciones tiene
    update_count = rx.cond(comment.updates, comment.updates.length(), 0)
    
    # Mapa de coronas para reputación
    crown_map_var = rx.Var.create({
        UserReputation.WOOD.value: "🪵",
        UserReputation.COPPER.value: "🥉",
        UserReputation.SILVER.value: "🥈",
        UserReputation.GOLD.value: "🥇",
        UserReputation.DIAMOND.value: "💎",
    })
    
    fallback_str = rx.cond(
        crown_map_var.contains(comment.author_reputation),
        crown_map_var[comment.author_reputation],
        comment.author_initial
    )
    
    return rx.card(
        rx.vstack(
            # --- Cabecera del Comentario ---
            rx.hstack(
                rx.avatar(
                    src=rx.cond(
                        comment.author_avatar_url != "",
                        rx.get_upload_url(comment.author_avatar_url),
                        ""
                    ), 
                    fallback=fallback_str, 
                    size="3",
                    radius="full"
                ),
                rx.vstack(
                    rx.text(comment.author_username, weight="bold", size="3"),
                    rx.text(f"Publicado: {comment.created_at_formatted}", size="1", color_scheme="gray"),
                    spacing="0", align_items="start"
                ),
                rx.spacer(),
                star_rating_display_safe(comment.rating, 0, size=20),
                align="center",
                width="100%",
            ),
            
            rx.divider(margin_y="0.5em"),
            
            # --- Contenido Principal ---
            rx.text(comment.content, size="3", white_space="pre-wrap"),
            
            # --- Botones de Voto y Botón de Historial ---
            rx.hstack(
                vote_buttons(
                    comment.id,
                    comment.likes,
                    comment.dislikes,
                    comment.user_vote,
                ),
                rx.spacer(),
                
                # Botón para mostrar/ocultar historial (Solo si hay updates)
                rx.cond(
                    comment.updates,
                    rx.button(
                        rx.hstack(
                            rx.icon("chevron-down"),
                            rx.text("Ver historial (", update_count, ")")
                        ),
                        # Necesitamos un estado para expandir/colapsar. 
                        # Usaremos un diccionario en AppState: expanded_comments = {id: bool}
                        on_click=AppState.toggle_comment_updates(comment.id),
                        variant="ghost", 
                        size="1",
                        color_scheme="violet"
                    )
                ),
                width="100%",
                align="center",
                margin_top="0.5em",
            ),

            # --- Zona de Actualizaciones (Historial) ---
            # Se muestra solo si el ID está en el diccionario de expandidos
            rx.cond(
                AppState.is_comment_expanded(comment.id),
                rx.vstack(
                    rx.foreach(
                        comment.updates,
                        render_update_item # Llamamos a la nueva función
                    ),
                    width="100%",
                    align_items="stretch"
                )
            ),
            
            align_items="stretch", 
            width="100%"
        ),
        width="100%",
        margin_bottom="1em"
    )

def review_submission_form() -> rx.Component:
    """Formulario para dejar o actualizar opinión."""
    return rx.cond(
        AppState.show_review_form,
        rx.card(
            rx.form(
                rx.vstack(
                    rx.heading(
                        rx.cond(AppState.my_review_for_product, "Actualiza tu opinión", "Deja tu opinión"), 
                        size="4"
                    ),
                    rx.text("Tu valoración:", size="2", weight="medium"),
                    rx.hstack(
                        rx.foreach(
                            rx.Var.range(5),
                            lambda i: rx.icon(
                                "star", 
                                color=rx.cond(AppState.review_rating > i, "gold", rx.color("gray", 8)),
                                on_click=AppState.set_review_rating(i + 1), 
                                cursor="pointer", 
                                size=28,
                                style={"fill": rx.cond(AppState.review_rating > i, "gold", "none")}
                            )
                        ),
                        spacing="1"
                    ),
                    rx.text_area(
                        name="review_content", 
                        placeholder="Cuéntanos qué te pareció el producto...", 
                        value=AppState.review_content,
                        on_change=AppState.set_review_content, 
                        width="100%",
                        min_height="80px"
                    ),
                    rx.button(
                        rx.cond(AppState.my_review_for_product, "Actualizar Opinión", "Publicar Opinión"), 
                        type="submit", 
                        width="100%", 
                        color_scheme="violet"
                    ),
                    spacing="3",
                    width="100%",
                ),
                on_submit=AppState.submit_review,
            )
        ),
        # Mensaje si ya alcanzó el límite
        rx.cond(
            AppState.review_limit_reached,
            rx.callout(
                "Has alcanzado el límite de 3 opiniones (original + 2 actualizaciones) para esta compra.",
                icon="info",
                color_scheme="orange",
                width="100%"
            ),
        )
    )

def product_detail_modal(is_for_direct_sale: bool = False) -> rx.Component:
    
    def _modal_image_section() -> rx.Component:
        def _manual_thumbnails() -> rx.Component:
            """
            [VERSIÓN CORREGIDA]
            Muestra las miniaturas de las variantes, aplicando un estilo
            atenuado y deshabilitando el clic si el grupo está agotado.
            """
            return rx.hstack(
                rx.foreach(
                    # 1. Cambiamos la fuente de datos a la nueva propiedad
                    AppState.modal_thumbnails_with_stock,
                    
                    # 2. 'thumb_data' es ahora un objeto ModalThumbnailData
                    lambda thumb_data: rx.box(
                        rx.image(
                            src=rx.get_upload_url(thumb_data.image_url),
                            height="60px", width="60px", object_fit="cover", border_radius="var(--radius-3)",
                        ),
                        # 3. Usamos 'visual_index' para saber cuál está activo
                        border_width=rx.cond(AppState.modal_selected_variant_index == thumb_data.visual_index, "3px", "1px"),
                        border_color=rx.cond(AppState.modal_selected_variant_index == thumb_data.visual_index, "var(--accent-9)", "var(--gray-a6)"),
                        padding="2px", border_radius="var(--radius-4)",
                        
                        # --- INICIO DE LA CORRECCIÓN VISUAL ---
                        # 4. Aplicamos opacidad si está agotado
                        opacity=rx.cond(thumb_data.is_out_of_stock, 0.4, 1.0),
                        # 5. Cambiamos el cursor si está agotado
                        cursor=rx.cond(thumb_data.is_out_of_stock, "not-allowed", "pointer"),
                        # --- FIN DE LA CORRECCIÓN VISUAL ---
                        
                        # 6. Solo permitimos el clic si NO está agotado
                        on_click=rx.cond(
                            ~thumb_data.is_out_of_stock,
                            AppState.set_modal_variant_index(thumb_data.visual_index),
                            None # No hace nada si está agotado
                        ),
                    )
                ),
                spacing="3", padding="0.5em", width="100%", overflow_x="auto", margin_top="0.5rem",
            )

        return rx.vstack(
            carousel(
                rx.foreach(
                    AppState.modal_image_urls,
                    lambda image_url, index: rx.box(
                        rx.image(
                            src=rx.get_upload_url(image_url),
                            alt=AppState.product_in_modal.title,
                            width="100%",
                            height="100%",
                            object_fit="contain",
                        ),
                        on_click=AppState.open_lightbox(index),
                        cursor="pointer",
                        height={"base": "350px", "md": "500px"},
                    ),
                ),
                key=AppState.modal_carousel_key,
                show_thumbs=False,
                show_arrows=AppState.modal_image_urls.length() > 1,
                show_indicators=AppState.modal_image_urls.length() > 1,
                show_status=False,
                infinite_loop=True,
                emulate_touch=True,
                width="100%",
            ),
            rx.cond(
                AppState.unique_modal_variants.length() > 1,
                _manual_thumbnails(),
            ),
            spacing="2",
            width="100%",
            position="relative",
        )

    def _modal_info_section() -> rx.Component:
        return rx.vstack(
            rx.text(AppState.product_in_modal.title, size="8", font_weight="bold", text_align="left"),
            rx.text("Publicado el " + AppState.product_in_modal.created_at_formatted, size="3", color_scheme="gray", text_align="left"),
            rx.text(AppState.product_in_modal.price_cop, size="7", color_scheme="gray", text_align="left"),
            star_rating_display_safe(AppState.product_in_modal.average_rating, AppState.product_in_modal.rating_count, size=32),
            
            rx.flex(
                rx.badge(AppState.product_in_modal.shipping_display_text, variant="solid", size="2"),
                rx.cond(
                    AppState.product_in_modal.combines_shipping,
                    rx.tooltip(
                        rx.badge("Envío Combinado", color_scheme="teal", variant="solid", size="2"),
                        content=AppState.product_in_modal.envio_combinado_tooltip_text
                    ),
                ),
                rx.cond(
                    AppState.product_in_modal.is_moda_completa_eligible,
                    rx.tooltip(
                        rx.badge("Moda Completa", color_scheme="violet", variant="solid", size="2"),
                        content=AppState.product_in_modal.moda_completa_tooltip_text
                    ),
                ),
                rx.cond(
                    AppState.product_in_modal.is_imported,
                    rx.badge("Importado", color_scheme="purple", variant="solid", size="2"),
                ),
                spacing="3",
                align="center",
                wrap="wrap",
                margin_y="1em",
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
                ## Este es el rx.foreach que debemos cambiar:
                rx.foreach(
                    AppState.modal_attribute_selectors,
                    lambda selector: rx.vstack(
                        rx.text(selector.key, weight="bold", size="3"),
                        rx.segmented_control.root(
                            rx.foreach(
                                selector.options,
                                # --- INICIO DE LA CORRECCIÓN VISUAL ---
                                # Ahora 'option' es un DTO, no un string
                                lambda option: rx.segmented_control.item(
                                    option.value, # El texto a mostrar
                                    value=option.value, # El valor
                                    disabled=option.disabled, # La lógica de deshabilitar
                                    
                                    # Añadimos estos estilos para que se vea gris/atenuado
                                    style={
                                        "opacity": rx.cond(option.disabled, 0.4, 1.0),
                                        "cursor": rx.cond(option.disabled, "not-allowed", "pointer"),
                                        "color": rx.cond(option.disabled, "var(--gray-a9)", "inherit"),
                                    }
                                )
                                # --- FIN DE LA CORRECCIÓN VISUAL ---
                            ),
                            on_change=lambda value: AppState.set_modal_selected_attribute(selector.key, value),
                            value=selector.current_value,
                        ),
                        align_items="start", width="100%", spacing="2"
                    )
                ),
            ),
            rx.text(
                "Publicado por: ",
                rx.hover_card.root(
                    rx.hover_card.trigger(
                        rx.link(
                            AppState.product_in_modal.seller_name,
                            href=f"/vendedor?id={AppState.product_in_modal.seller_id}",
                            color_scheme="violet", font_weight="bold",
                        )
                    ),
                    rx.hover_card.content(
                        rx.vstack(
                            rx.text("Puntuación del Vendedor"),
                            seller_score_stars(AppState.product_in_modal.seller_score),
                            align="center",
                            spacing="2"
                        ),
                        padding="0.75em",
                    ),
                ),
                size="3", color_scheme="gray", margin_top="1.5em",
                text_align="left", width="100%"
            ),
            rx.cond(
                AppState.product_in_modal.seller_city,
                rx.hstack(
                    rx.icon("map-pin", size=16, color_scheme="gray"),
                    rx.text(
                        "Desde: ",
                        rx.text.strong(AppState.product_in_modal.seller_city),
                        size="3",
                        color_scheme="gray"
                    ),
                    spacing="2",
                    align="center",
                    margin_top="0.5em",
                )
            ),
            rx.spacer(),
            rx.hstack(
                rx.button(
                    "Añadir al Carrito",
                    on_click=rx.cond(
                        is_for_direct_sale,
                        AppState.add_to_direct_sale_cart(AppState.product_in_modal.id),
                        AppState.add_to_cart(AppState.product_in_modal.id)
                    ),
                    size="3",
                    flex_grow="1",
                    color_scheme="violet"
                ),
                rx.icon_button(
                    rx.cond(AppState.is_current_post_saved, rx.icon(tag="bookmark-minus"), rx.icon(tag="bookmark-plus")),
                    on_click=AppState.toggle_save_post,
                    size="3",
                    variant="outline",
                    color_scheme="violet",
                ),
                rx.icon_button(
                    rx.icon(tag="share-2"),
                    on_click=[
                        rx.set_clipboard(AppState.base_app_url + "/?product=" + AppState.product_in_modal.id.to_string()),
                        rx.toast.success("¡Enlace para compartir copiado!")
                    ],
                    size="3",
                    variant="outline",
                    color_scheme="violet",
                ),
                spacing="3", width="100%", margin_top="1.5em",
            ),
            align="start", height="100%",
        )

    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.close(rx.icon_button(rx.icon("x"), variant="soft", color_scheme="gray", style={"position": "absolute", "top": "1rem", "right": "1rem", "z_index": "10"})),
            rx.cond(
                AppState.product_in_modal,
                rx.vstack(
                    rx.grid(
                        _modal_image_section(), # Usando la función interna (asegurate de tenerla)
                        _modal_info_section(),  # Usando la función interna
                        columns={"initial": "1", "md": "2"},
                        spacing="6",
                        align_items="start",
                        width="100%",
                    ),
                    rx.divider(margin_y="1.5em"),
                    
                    # --- SECCIÓN DE OPINIONES ACTUALIZADA ---
                    rx.heading("Opiniones de Clientes", size="5", width="100%"),
                    rx.vstack(
                        review_submission_form(), # Formulario condicional
                        
                        rx.cond(
                            AppState.product_comments,
                            rx.vstack(
                                rx.foreach(AppState.product_comments, render_comment_item), # Lista renderizada
                                width="100%", spacing="4"
                            ),
                            rx.center(
                                rx.text("Aún no hay opiniones. ¡Sé el primero!", color_scheme="gray"),
                                padding="2em", width="100%"
                            )
                        ),
                        width="100%", spacing="4"
                    ),
                    # ----------------------------------------
                ),
                skeleton_product_detail_view(),
            ),
            max_width="1000px",
            width="100%"
        ),
        open=AppState.show_detail_modal,
        on_open_change=AppState.close_product_detail_modal,
    )

def public_qr_scanner_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Buscar Producto por QR"),
            rx.dialog.description(
                "Usa la cámara de tu celular para escanear el código y ver los detalles del producto."
            ),
            rx.vstack(
                rx.upload(
                    rx.button(
                        rx.hstack(rx.icon("camera"), rx.text("Escanear con la Cámara")),
                        size="3", width="100%", height="5em", color_scheme="violet",
                    ),
                    id="public_qr_camera",
                    capture="environment",
                    on_drop=[
                        AppState.set_show_public_qr_scanner_modal(False), 
                        AppState.handle_public_qr_scan(rx.upload_files("public_qr_camera"))
                    ],
                    width="100%",
                ),
                rx.upload(
                    rx.button(
                        rx.hstack(rx.icon("image"), rx.text("Subir desde Galería")),
                        size="3", width="100%", height="5em", variant="outline",
                    ),
                    id="public_qr_gallery",
                    on_drop=[
                        AppState.set_show_public_qr_scanner_modal(False),
                        AppState.handle_public_qr_scan(rx.upload_files("public_qr_gallery"))
                    ],
                    width="100%",
                ),
                spacing="4", width="100%", margin_y="1em",
            ),
            rx.flex(
                rx.dialog.close(rx.button("Cancelar", variant="soft", color_scheme="gray")),
                justify="end", margin_top="1em",
            ),
        ),
        open=AppState.show_public_qr_scanner_modal,
        on_open_change=AppState.set_show_public_qr_scanner_modal,
    )

def lightbox_modal() -> rx.Component:
    """
    [VERSIÓN SIMPLIFICADA] Lightbox que usa una variable computada para el fondo.
    """
    # ... (los controles no cambian) ...
    controls = rx.box(
        rx.hstack(
            rx.icon_button(rx.cond(AppState.is_lightbox_locked, rx.icon("lock"), rx.icon("lock-open")), on_click=AppState.toggle_lightbox_lock, variant="ghost", color_scheme="gray", size="2"),
            rx.icon_button(rx.icon("zoom-out"), on_click=AppState.zoom_out, variant="ghost", color_scheme="gray", size="2", display=["none", "none", "flex"]),
            rx.icon_button(rx.icon("zoom-in"), on_click=AppState.zoom_in, variant="ghost", color_scheme="gray", size="2", display=["none", "none", "flex"]),
            rx.dialog.close(rx.icon_button(rx.icon("x"), variant="ghost", color_scheme="gray", size="2")),
            spacing="2",
        ),
        padding_x="0.5rem", padding_y="0.3rem",
        bg=rx.color_mode_cond("rgba(255, 255, 255, 0.6)", "rgba(0, 0, 0, 0.4)"),
        border_radius="full", position="absolute", top="1.5rem", right="1.5rem",
        z_index="1500", style={"backdrop_filter": "blur(8px)"},
    )

    # --- ✨ Obtiene la tupla de configuración del estado ✨ ---
    bg_settings = AppState.lightbox_background_settings

    return rx.dialog.root(
        rx.dialog.content(
            controls,
            rx.center(
                carousel(
                    rx.foreach(
                        AppState.modal_image_urls,
                        lambda image_url, index:
                            rx.box(
                                rx.image(
                                    src=rx.get_upload_url(image_url), alt=AppState.product_in_modal.title,
                                    max_height="90vh", max_width="90vw", object_fit="contain",
                                    transition="transform 0.2s ease-out", transform=f"scale({AppState.lightbox_zoom_level})",
                                ),
                                overflow="auto", height="100%", width="100%", display="flex",
                                align_items="center", justify_content="center",
                            ),
                    ),
                    selected_item=AppState.lightbox_start_index,
                    swipeable=~AppState.is_lightbox_locked, show_arrows=~AppState.is_lightbox_locked,
                    show_indicators=False, show_thumbs=False, show_status=False,
                    infinite_loop=True, use_keyboard_arrows=True,
                    width="100%", style={"& .thumbs-wrapper": {"display": "none"}},
                ),
                width="100%", height="100%",
                
                # --- ✨ ESTA ES LA APLICACIÓN DE LA CORRECCIÓN ✨ ---
                # bg_settings[0] será "white" o "black" (para modo claro)
                # bg_settings[1] será "white" o "black" (para modo oscuro)
                bg=rx.color_mode_cond(
                    light=bg_settings[0], 
                    dark=bg_settings[1]   
                ),
                # --- ✨ FIN ✨ ---
            ),
            # Estilos del content no cambian
            style={
                "position": "fixed", "inset": "0", "width": "auto", "height": "auto",
                "max_width": "none", "padding": "0", "margin": "0", "border_radius": "0",
                "background_color": "rgba(0, 0, 0, 0.5)",
                "backdrop_filter": "blur(4px)",
            },
        ),
        open=AppState.is_lightbox_open,
        on_open_change=AppState.close_lightbox,
    )

def blog_public_page_content() -> rx.Component:
    main_content = rx.center(
        rx.vstack(
            rx.cond(
                AppState.is_loading,
                skeleton_product_gallery(),
                product_gallery_component(posts=AppState.displayed_posts)
            ),
            spacing="6", width="100%", padding="2em", align="center"
        ),
        width="100%"
    )

    return rx.fragment(
        floating_filter_panel(),
        main_content,
        product_detail_modal(is_for_direct_sale=False),
        public_qr_scanner_modal(),
        lightbox_modal(),
    )