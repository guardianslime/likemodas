# likemodas/ui/filter_panel.py

import reflex as rx
from reflex.event import EventSpec
from ..auth.state import SessionState
from ..models import Category
from ..ui.components import searchable_select
from ..data.product_options import (
    LISTA_TIPOS_ROPA, LISTA_TIPOS_ZAPATOS, LISTA_TIPOS_MOCHILAS, LISTA_TIPOS_GENERAL
)

def floating_filter_panel() -> rx.Component:
    """
    El panel de filtros flotante con todas las funcionalidades implementadas.
    """
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.heading("Filtros", size="6", width="100%"),
                rx.divider(),
                
                # --- Filtros de Precio con botón de limpiar ---
                rx.vstack(
                    rx.text("Precio", weight="bold"),
                    rx.hstack(
                        rx.input(placeholder="Mínimo", value=SessionState.min_price, on_change=SessionState.set_min_price, type="number"),
                        rx.cond(SessionState.min_price != "", 
                            rx.icon_button(rx.icon("x", size=16), on_click=SessionState.clear_filter("min_price"), size="1", variant="ghost")
                        ),
                        align_items="center", width="100%", spacing="2"
                    ),
                    rx.hstack(
                        rx.input(placeholder="Máximo", value=SessionState.max_price, on_change=SessionState.set_max_price, type="number"),
                        rx.cond(SessionState.max_price != "",
                            rx.icon_button(rx.icon("x", size=16), on_click=SessionState.clear_filter("max_price"), size="1", variant="ghost")
                        ),
                        align_items="center", width="100%", spacing="2"
                    ),
                    spacing="2", align_items="start", width="100%"
                ),

                rx.cond(
                    (SessionState.current_category != "") & (SessionState.current_category != "todos"),
                    
                    # --- FILTROS ESPECÍFICOS DE CATEGORÍA ---
                    rx.fragment(
                        rx.cond(
                            SessionState.current_category == Category.ROPA.value,
                            rx.vstack(
                                rx.divider(), rx.text("Filtros de Ropa", weight="bold"),
                                rx.hstack(
                                    searchable_select(placeholder="Por tipo...", options=SessionState.filtered_tipos_ropa, on_change_select=SessionState.set_filter_tipo_prenda, value_select=SessionState.filter_tipo_prenda, search_value=SessionState.search_tipo_prenda, on_change_search=SessionState.set_search_tipo_prenda, filter_name="ropa_tipo"),
                                    rx.cond(SessionState.filter_tipo_prenda != "", rx.icon_button(rx.icon("x", size=16), on_click=SessionState.clear_filter("filter_tipo_prenda"), size="1", variant="ghost"))
                                ),
                                rx.hstack(
                                    searchable_select(placeholder="Por color...", options=SessionState.filtered_colores, on_change_select=SessionState.set_filter_color, value_select=SessionState.filter_color, search_value=SessionState.search_color, on_change_search=SessionState.set_search_color, filter_name="ropa_color"),
                                    rx.cond(SessionState.filter_color != "", rx.icon_button(rx.icon("x", size=16), on_click=SessionState.clear_filter("filter_color"), size="1", variant="ghost"))
                                ),
                                rx.hstack(
                                    searchable_select(placeholder="Por talla...", options=SessionState.filtered_tallas_ropa, on_change_select=SessionState.set_filter_talla, value_select=SessionState.filter_talla, search_value=SessionState.search_talla, on_change_search=SessionState.set_search_talla, filter_name="ropa_talla"),
                                    rx.cond(SessionState.filter_talla != "", rx.icon_button(rx.icon("x", size=16), on_click=SessionState.clear_filter("filter_talla"), size="1", variant="ghost"))
                                ),
                                spacing="2", align_items="start", width="100%"
                            )
                        ),
                        rx.cond(
                            SessionState.current_category == Category.CALZADO.value,
                            rx.vstack(
                                rx.divider(), rx.text("Filtros de Calzado", weight="bold"),
                                rx.hstack(
                                    searchable_select(placeholder="Por tipo...", options=SessionState.filtered_tipos_zapatos, on_change_select=SessionState.set_filter_tipo_zapato, value_select=SessionState.filter_tipo_zapato, search_value=SessionState.search_tipo_zapato, on_change_search=SessionState.set_search_tipo_zapato, filter_name="calzado_tipo"),
                                    rx.cond(SessionState.filter_tipo_zapato != "", rx.icon_button(rx.icon("x", size=16), on_click=SessionState.clear_filter("filter_tipo_zapato"), size="1", variant="ghost"))
                                ),
                                rx.hstack(
                                    searchable_select(placeholder="Por color...", options=SessionState.filtered_colores, on_change_select=SessionState.set_filter_color, value_select=SessionState.filter_color, search_value=SessionState.search_color, on_change_search=SessionState.set_search_color, filter_name="calzado_color"),
                                    rx.cond(SessionState.filter_color != "", rx.icon_button(rx.icon("x", size=16), on_click=SessionState.clear_filter("filter_color"), size="1", variant="ghost"))
                                ),
                                rx.hstack(
                                    searchable_select(placeholder="Por número...", options=SessionState.filtered_numeros_calzado, on_change_select=SessionState.set_filter_numero_calzado, value_select=SessionState.filter_numero_calzado, search_value=SessionState.search_numero_calzado, on_change_search=SessionState.set_search_numero_calzado, filter_name="calzado_numero"),
                                    rx.cond(SessionState.filter_numero_calzado != "", rx.icon_button(rx.icon("x", size=16), on_click=SessionState.clear_filter("filter_numero_calzado"), size="1", variant="ghost"))
                                ),
                                spacing="2", align_items="start", width="100%"
                            )
                        ),
                        rx.cond(
                            SessionState.current_category == Category.MOCHILAS.value,
                            rx.vstack(
                                rx.divider(), rx.text("Filtros de Mochilas", weight="bold"),
                                rx.hstack(
                                    searchable_select(placeholder="Por tipo...", options=SessionState.filtered_tipos_mochilas, on_change_select=SessionState.set_filter_tipo_mochila, value_select=SessionState.filter_tipo_mochila, search_value=SessionState.search_tipo_mochila, on_change_search=SessionState.set_search_tipo_mochila, filter_name="mochila_tipo"),
                                    rx.cond(SessionState.filter_tipo_mochila != "", rx.icon_button(rx.icon("x", size=16), on_click=SessionState.clear_filter("filter_tipo_mochila"), size="1", variant="ghost"))
                                ),
                                spacing="2", align_items="start", width="100%"
                            )
                        ),
                    ),
                    
                    # --- FILTROS GENERALES ---
                    rx.fragment(
                        rx.vstack(
                            rx.divider(),
                            rx.text("Filtros Generales", weight="bold"),
                            rx.hstack(
                                searchable_select(placeholder="Por tipo...", options=SessionState.filtered_tipos_general, on_change_select=SessionState.set_filter_tipo_general, value_select=SessionState.filter_tipo_general, search_value=SessionState.search_tipo_general, on_change_search=SessionState.set_search_tipo_general, filter_name="general_tipo"),
                                rx.cond(SessionState.filter_tipo_general != "", rx.icon_button(rx.icon("x", size=16), on_click=SessionState.clear_filter("filter_tipo_general"), size="1", variant="ghost"))
                            ),
                            rx.hstack(
                                searchable_select(placeholder="Por material o tela...", options=SessionState.filtered_materiales, on_change_select=SessionState.set_filter_material_tela, value_select=SessionState.filter_material_tela, search_value=SessionState.search_material_tela, on_change_search=SessionState.set_search_material_tela, filter_name="general_material"),
                                rx.cond(SessionState.filter_material_tela != "", rx.icon_button(rx.icon("x", size=16), on_click=SessionState.clear_filter("filter_material_tela"), size="1", variant="ghost"))
                            ),
                            rx.hstack(
                                searchable_select(placeholder="Por talla o medidas...", options=SessionState.filtered_medidas_general, on_change_select=SessionState.set_filter_medida_talla, value_select=SessionState.filter_medida_talla, search_value=SessionState.search_medida_talla, on_change_search=SessionState.set_search_medida_talla, filter_name="general_medida"),
                                rx.cond(SessionState.filter_medida_talla != "", rx.icon_button(rx.icon("x", size=16), on_click=SessionState.clear_filter("filter_medida_talla"), size="1", variant="ghost"))
                            ),
                            rx.hstack(
                                searchable_select(placeholder="Por color...", options=SessionState.filtered_colores, on_change_select=SessionState.set_filter_color, value_select=SessionState.filter_color, search_value=SessionState.search_color, on_change_search=SessionState.set_search_color, filter_name="general_color"),
                                rx.cond(SessionState.filter_color != "", rx.icon_button(rx.icon("x", size=16), on_click=SessionState.clear_filter("filter_color"), size="1", variant="ghost"))
                            ),
                            spacing="2", align_items="start", width="100%"
                        )
                    )
                ),
                spacing="4", padding="1.5em", bg=rx.color("gray", 2),
                height="100%", width="280px",
            ),
            rx.box(
                rx.text(
                    "Filtros",
                    style={"writing_mode": "vertical-rl", "transform": "rotate(180deg)", "padding": "0.5em 0.09em", "font_weight": "bold", "letter_spacing": "2px", "color": "white"}
                ),
                on_click=SessionState.toggle_filters,
                cursor="pointer",
                bg=rx.color("blue", 9),
                border_radius="0 8px 8px 0",
                height="120px",
                display="flex",
                align_items="center"
            ),
            align_items="center",
            spacing="0"
        ),
        position="fixed",
        top="50%",
        left="0",
        transform=rx.cond(
            SessionState.show_filters,
            "translateY(-50%)",
            "translate(-280px, -50%)"
        ),
        transition="transform 0.3s ease-in-out",
        z_index=1000,
        height="auto",
    )