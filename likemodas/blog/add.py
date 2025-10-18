# likemodas/blog/add.py
# En: likemodas/blog/add.py

import reflex as rx
from rx_color_picker.color_picker import color_picker
from ..state import AppState
from ..auth.admin_auth import require_panel_access
from .forms import blog_post_add_form
from ..ui.components import star_rating_display_safe
from ..utils.formatting import format_to_cop
from typing import Dict, Any
from reflex.components.component import NoSSRComponent
import json # Importa la librería json

# --- ✨ INICIO: NUEVO COMPONENTE AUTOCONTENIDO PARA IMAGEN INTERACTIVA ✨ ---
class InteractiveImage(NoSSRComponent):
    """
    Componente que renderiza tanto la imagen como los controles de Moveable juntos,
    eliminando las condiciones de carrera y el error React #306.
    """
    library = "react-moveable"
    tag = "Moveable" # Seguiremos usando Moveable, pero de forma diferente

    # Propiedades que pasamos desde Python
    src: rx.Var[str]
    transform: rx.Var[str]
    keep_ratio: rx.Var[bool] = True

    # Evento que se dispara al final de cada acción
    on_transform_end: rx.EventHandler[lambda e: [e]]

    def _get_custom_code(self) -> str:
        # Este código JavaScript personalizado crea un componente React autocontenido
        return """
const InteractiveImage = (props) => {
  const targetRef = React.useRef(null);
  const { src, transform, on_transform_end, keep_ratio, ...moveableProps } = props;

  // Si no hay 'src', no renderizamos nada para evitar errores
  if (!src) {
    return (
        <div style={{width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
            <svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.59a2 2 0 0 1-2.83-2.83l.79-.79m.79-4.21l-4.21 4.21"/><path d="m18 5-4.21 4.21"/><path d="m19 12-1.41-1.41"/><path d="m12 19-1.41-1.41"/><path d="m5 12-1.41-1.41"/></svg>
        </div>
    );
  }

  const handleEnd = (e) => {
    if (on_transform_end && e.lastEvent) {
      on_transform_end({ transform: e.lastEvent.transform });
    }
  };

  return (
    <>
      <img
        ref={targetRef}
        src={src}
        id="moveable_target_image"
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'contain',
          transform: transform,
        }}
      />
      <Moveable
        target={targetRef}
        draggable={true}
        resizable={true}
        rotatable={true}
        keepRatio={keep_ratio}
        onDragEnd={handleEnd}
        onResizeEnd={handleEnd}
        onRotateEnd={handleEnd}
        {...moveableProps}
      />
    </>
  );
};
"""

interactive_image_editor = InteractiveImage.create
# --- ✨ FIN: NUEVO COMPONENTE ✨ ---


def post_preview() -> rx.Component:
    """
    Versión que utiliza el nuevo componente InteractiveImage.
    """
    first_image_url = rx.cond(
        (AppState.variant_groups.length() > 0) & (AppState.variant_groups[0].image_urls.length() > 0),
        AppState.variant_groups[0].image_urls[0],
        ""
    )
    
    return rx.box(
        rx.vstack(
            rx.box(
                # El contenedor principal que define el área visible
                rx.box(
                    # --- ✨ Llamada al nuevo componente autocontenido ✨ ---
                    interactive_image_editor(
                        src=rx.get_upload_url(first_image_url),
                        transform=AppState.preview_image_transform,
                        on_transform_end=AppState.set_preview_image_transform,
                        keep_ratio=True,
                    ),
                    width="100%", height="260px",
                    overflow="hidden",
                    border_top_left_radius="var(--radius-3)", border_top_right_radius="var(--radius-3)",
                    bg=rx.cond(AppState.card_theme_mode == "light", "white", rx.color("gray", 3)),
                ),
                rx.badge(
                    rx.cond(AppState.is_imported, "Importado", "Nacional"),
                    color_scheme=rx.cond(AppState.is_imported, "purple", "cyan"), variant="solid",
                    style={"position": "absolute", "top": "0.5rem", "left": "0.5rem", "z_index": "2"}
                ),
                position="relative",
            ),
            # El resto de la tarjeta no cambia
            rx.vstack(
                rx.text(
                    rx.cond(AppState.title, AppState.title, "Título del Producto"), 
                    weight="bold", size="6", no_of_lines=2, width="100%",
                    color=rx.cond(
                        AppState.use_default_style,
                        rx.cond(AppState.card_theme_mode == "light", rx.color("gray", 11), "white"),
                        AppState.live_title_color,
                    )
                ),
                star_rating_display_safe(0, 0, size=24),
                rx.text(
                    AppState.price_cop_preview, size="5", weight="medium",
                    color=rx.cond(
                         AppState.use_default_style,
                        rx.cond(AppState.card_theme_mode == "light", rx.color("gray", 9), rx.color("gray", 11)),
                        AppState.live_price_color,
                    )
                ),
                rx.spacer(),
                # Badges de envío irían aquí si están definidos
                spacing="2", align_items="start", width="100%", padding="1em", flex_grow="1",
            ),
            spacing="0", align_items="stretch", height="100%",
        ),
        width="290px", height="480px",
        bg=rx.cond(
             AppState.use_default_style,
            rx.cond(AppState.card_theme_mode == "light", "#fdfcff", "var(--gray-2)"),
            AppState.live_card_bg_color
        ),
        border="1px solid var(--gray-a6)",
        border_radius="8px", box_shadow="md",
    )

@require_panel_access
def blog_post_add_content() -> rx.Component:
    """
    Layout de la página de creación, eliminando los sliders y añadiendo el botón de reset.
    """
    return rx.grid(
        rx.vstack(
            rx.heading(
                "Crear Publicación", size="7", width="100%", text_align="left", 
                margin_bottom="0.5em", color_scheme="gray", font_weight="medium"
            ),
            blog_post_add_form(),
            width="100%", spacing="4", align_items="center",
            padding_left={"lg": "15em"}, padding_x=["1em", "2em"],
        ),
        rx.vstack(
            rx.heading("Previsualización", size="7", width="100%", text_align="left", margin_bottom="0.5em"),
            post_preview(),
            rx.vstack( 
                rx.divider(margin_y="1em"),
                rx.hstack(
                    rx.text("Personalizar Tarjeta", weight="bold", size="4"),
                    rx.spacer(),
                    rx.tooltip(
                        rx.icon_button(
                            rx.icon("rotate-ccw", size=14),
                            on_click=AppState.reset_image_styles,
                            variant="soft", size="1"
                        ),
                        content="Resetear ajustes de imagen"
                    ),
                    width="100%",
                    align="center",
                ),
                rx.text("Puedes guardar un estilo para modo claro y otro para modo oscuro.", size="2", color_scheme="gray"),
                rx.hstack(
                    rx.text("Usar estilo predeterminado del tema", size="3"),
                    rx.spacer(),
                    rx.switch(is_checked=AppState.use_default_style, on_change=AppState.set_use_default_style, size="2"),
                    width="100%", align="center",
                ),
                rx.cond(
                    ~AppState.use_default_style,
                    rx.vstack(
                        # ... (código de los popovers para colores)
                        spacing="3", width="100%", margin_top="1em"
                    ),
                ),
                spacing="3", padding="1em", border="1px dashed var(--gray-a6)",
                border_radius="md", margin_top="1.5em", align_items="stretch",
                width="290px",
            ),
            display={"initial": "none", "lg": "flex"},
            width="100%", spacing="4", position="sticky", top="2em", align_items="center",
        ),
        columns={"initial": "1", "lg": "auto auto"},
        justify="center",
        align="start",
        gap="3em",
        width="100%",
        max_width="1800px",
        padding_y="2em",
        padding_x=["1em", "2em"],
    )