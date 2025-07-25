# likemodas/ui/filter_panel.py

import reflex as rx
from ..auth.state import SessionState
from ..models import Category
from ..data.product_options import (
    LISTA_TIPOS_ROPA, LISTA_TIPOS_ZAPATOS, LISTA_TIPOS_MOCHILAS, LISTA_TIPOS_GENERAL
)

# --- ✨ FUNCIÓN CORREGIDA ---
# Se cambió la sintaxis de opt["label"] a opt.label
def build_searchable_select(
    placeholder: str,
    current_value_var: rx.Var[str],
    options_var: rx.Var[list],
    search_term_var: rx.Var[str],
    on_search_change,
    on_value_change
) -> rx.Component:
    """
    Crea un componente de selección con búsqueda usando un Popover.
    """
    return rx.popover.root(
        rx.popover.trigger(
            rx.button(
                rx.cond(current_value_var, current_value_var, placeholder),
                rx.icon(tag="chevron-down"),
                variant="outline",
                justify="space-between",
                width="100%",
                text_align="left"
            )
        ),
        rx.popover.content(
            rx.vstack(
                rx.input(
                    placeholder="Buscar...",
                    value=search_term_var,
                    on_change=on_search_change,
                ),
                rx.scroll_area(
                    rx.vstack(
                        rx.foreach(
                            options_var,
                            lambda opt: rx.popover.close(
                                rx.button(
                                    opt.label,  # <-- CORRECCIÓN AQUÍ
                                    on_click=on_value_change(opt.value), # <-- CORRECCIÓN AQUÍ
                                    variant="ghost",
                                    width="100%",
                                    text_align="left"
                                )
                            )
                        ),
                        width="100%"
                    ),
                    max_height="200px",
                    width="100%"
                ),
                spacing="2",
                width="100%"
            ),
            width="100%",
            padding="0.5em"
        )
    )

def floating_filter_panel() -> rx.Component:
    """Un panel de filtros dinámico con selectores de búsqueda personalizados."""
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.heading("Filtros", size="6", width="100%"),
                rx.divider(),
                rx.vstack(
                    rx.text("Precio", weight="bold"),
                    rx.input(placeholder="Mínimo", value=SessionState.min_price, on_change=SessionState.set_min_price, type="number"),
                    rx.input(placeholder="Máximo", value=SessionState.max_price, on_change=SessionState.set_max_price, type="number"),
                    spacing="2", align_items="start", width="100%"
                ),
                rx.cond(
                    (SessionState.current_category != "") & (SessionState.current_category != "todos"),
                    # --- Filtros Específicos ---
                    rx.fragment(
                        rx.cond(
                            SessionState.current_category == Category.ROPA.value,
                            rx.vstack(
                                rx.divider(), rx.text("Filtros de Ropa", weight="bold"),
                                build_searchable_select("Filtrar por tipo...", SessionState.filter_tipo_prenda, LISTA_TIPOS_ROPA, SessionState.tipo_prenda_search, SessionState.set_tipo_prenda_search, SessionState.set_filter_tipo_prenda),
                                build_searchable_select("Filtrar por color...", SessionState.filter_color, SessionState.filtered_available_colors, SessionState.color_search, SessionState.set_color_search, SessionState.set_filter_color),
                                build_searchable_select("Filtrar por talla...", SessionState.filter_talla, SessionState.filtered_available_tallas, SessionState.talla_search, SessionState.set_talla_search, SessionState.set_filter_talla),
                                spacing="2", align_items="start", width="100%"
                            )
                        ),
                        # Agrega aquí las otras categorías si lo necesitas
                    ),
                    # --- Filtros Generales ---
                    rx.fragment(
                        rx.vstack(
                            rx.divider(),
                            rx.text("Filtros Generales", weight="bold"),
                            build_searchable_select("Filtrar por tipo...", SessionState.filter_tipo_general, LISTA_TIPOS_GENERAL, SessionState.tipo_general_search, SessionState.set_tipo_general_search, SessionState.set_filter_tipo_general),
                            build_searchable_select("Material o tela...", SessionState.filter_material_tela, SessionState.filtered_general_materials, SessionState.material_tela_search, SessionState.set_material_tela_search, SessionState.set_filter_material_tela),
                            build_searchable_select("Talla o medidas...", SessionState.filter_medida_talla, SessionState.filtered_general_sizes, SessionState.medida_talla_search, SessionState.set_medida_talla_search, SessionState.set_filter_medida_talla),
                            build_searchable_select("Color...", SessionState.filter_color, SessionState.filtered_general_colors, SessionState.color_search, SessionState.set_color_search, SessionState.set_filter_color),
                            spacing="2", align_items="start", width="100%"
                        )
                    )
                ),
                spacing="4", padding="1.5em", bg=rx.color("gray", 2),
                height="100%", width="280px",
            ),
            # El resto del componente no cambia...
            rx.box(
                rx.text("Filtros", style={"writing_mode": "vertical-rl", "transform": "rotate(180deg)", "padding": "0.5em 0.09em", "font_weight": "bold", "letter_spacing": "2px", "color": "white"}),
                on_click=SessionState.toggle_filters, cursor="pointer", bg=rx.color("blue", 9), border_radius="0 8px 8px 0", height="120px", display="flex", align_items="center"
            ),
            align_items="center", spacing="0"
        ),
        position="fixed", top="50%", left="0",
        transform=rx.cond(SessionState.show_filters, "translateY(-50%)", "translate(-280px, -50%)"),
        transition="transform 0.3s ease-in-out", z_index="1000", height="auto",
    )