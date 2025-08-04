# likemodas/ui/filter_panel.py

import reflex as rx
from reflex.event import EventSpec
# Se importa el estado unificado y final
from ..state import AppState
from ..models import Category
from ..ui.components import searchable_select
from ..data.product_options import (
    LISTA_TIPOS_ROPA, LISTA_TIPOS_ZAPATOS, LISTA_TIPOS_MOCHILAS, LISTA_TIPOS_GENERAL
)

def floating_filter_panel() -> rx.Component:
    """
    El panel de filtros flotante, ahora actualizado para usar AppState.
    """
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.hstack(
                    rx.heading("Filtros", size="6"),
                    rx.spacer(),
                    rx.button(
                        "Limpiar",
                        # Se usa AppState en lugar de SessionState
                        on_click=AppState.clear_all_filters,
                        size="1",
                        variant="soft",
                        color_scheme="gray"
                    ),
                    justify="between",
                    align_items="center",
                    width="100%"
                ),
                rx.divider(),
                
                rx.vstack(
                    rx.text("Precio", weight="bold"),
                    rx.hstack(
                        # Todas las referencias ahora apuntan a AppState
                        rx.input(placeholder="Mínimo", value=AppState.min_price, on_change=AppState.set_min_price, type="number"),
                        rx.cond(AppState.min_price != "", 
                            rx.icon_button(rx.icon("x", size=16), on_click=AppState.clear_filter("min_price"), size="1", variant="ghost")
                        ),
                        align_items="center", width="100%", spacing="2"
                    ),
                    rx.hstack(
                        rx.input(placeholder="Máximo", value=AppState.max_price, on_change=AppState.set_max_price, type="number"),
                        rx.cond(AppState.max_price != "",
                            rx.icon_button(rx.icon("x", size=16), on_click=AppState.clear_filter("max_price"), size="1", variant="ghost")
                        ),
                        align_items="center", width="100%", spacing="2"
                    ),
                    spacing="2", align_items="start", width="100%"
                ),

                rx.cond(
                    (AppState.current_category != "") & (AppState.current_category != "todos"),
                    rx.fragment(
                        rx.cond(
                            AppState.current_category == Category.ROPA.value,
                            rx.vstack(
                                rx.divider(), rx.text("Filtros de Ropa", weight="bold"),
                                rx.hstack(
                                    searchable_select(placeholder="Por tipo...", options=AppState.filtered_tipos_ropa, on_change_select=AppState.set_filter_tipo_prenda, value_select=AppState.filter_tipo_prenda, search_value=AppState.search_tipo_prenda, on_change_search=AppState.set_search_tipo_prenda, filter_name="ropa_tipo"),
                                    rx.cond(AppState.filter_tipo_prenda != "", rx.icon_button(rx.icon("x", size=16), on_click=AppState.clear_filter("filter_tipo_prenda"), size="1", variant="ghost"))
                                ),
                                rx.hstack(
                                    searchable_select(placeholder="Por color...", options=AppState.filtered_colores, on_change_select=AppState.set_filter_color, value_select=AppState.filter_color, search_value=AppState.search_color, on_change_search=AppState.set_search_color, filter_name="ropa_color"),
                                    rx.cond(AppState.filter_color != "", rx.icon_button(rx.icon("x", size=16), on_click=AppState.clear_filter("filter_color"), size="1", variant="ghost"))
                                ),
                                rx.hstack(
                                    searchable_select(placeholder="Por talla...", options=AppState.filtered_tallas_ropa, on_change_select=AppState.set_filter_talla, value_select=AppState.filter_talla, search_value=AppState.search_talla, on_change_search=AppState.set_search_talla, filter_name="ropa_talla"),
                                    rx.cond(AppState.filter_talla != "", rx.icon_button(rx.icon("x", size=16), on_click=AppState.clear_filter("filter_talla"), size="1", variant="ghost"))
                                ),
                                spacing="2", align_items="start", width="100%"
                            )
                        ),
                        rx.cond(
                            AppState.current_category == Category.CALZADO.value,
                            rx.vstack(
                                rx.divider(), rx.text("Filtros de Calzado", weight="bold"),
                                rx.hstack(
                                    searchable_select(placeholder="Por tipo...", options=AppState.filtered_tipos_zapatos, on_change_select=AppState.set_filter_tipo_zapato, value_select=AppState.filter_tipo_zapato, search_value=AppState.search_tipo_zapato, on_change_search=AppState.set_search_tipo_zapato, filter_name="calzado_tipo"),
                                    rx.cond(AppState.filter_tipo_zapato != "", rx.icon_button(rx.icon("x", size=16), on_click=AppState.clear_filter("filter_tipo_zapato"), size="1", variant="ghost"))
                                ),
                                rx.hstack(
                                    searchable_select(placeholder="Por color...", options=AppState.filtered_colores, on_change_select=AppState.set_filter_color, value_select=AppState.filter_color, search_value=AppState.search_color, on_change_search=AppState.set_search_color, filter_name="calzado_color"),
                                    rx.cond(AppState.filter_color != "", rx.icon_button(rx.icon("x", size=16), on_click=AppState.clear_filter("filter_color"), size="1", variant="ghost"))
                                ),
                                rx.hstack(
                                    searchable_select(placeholder="Por número...", options=AppState.filtered_numeros_calzado, on_change_select=AppState.set_filter_numero_calzado, value_select=AppState.filter_numero_calzado, search_value=AppState.search_numero_calzado, on_change_search=AppState.set_search_numero_calzado, filter_name="calzado_numero"),
                                    rx.cond(AppState.filter_numero_calzado != "", rx.icon_button(rx.icon("x", size=16), on_click=AppState.clear_filter("filter_numero_calzado"), size="1", variant="ghost"))
                                ),
                                spacing="2", align_items="start", width="100%"
                            )
                        ),
                        rx.cond(
                            AppState.current_category == Category.MOCHILAS.value,
                            rx.vstack(
                                rx.divider(), rx.text("Filtros de Mochilas", weight="bold"),
                                rx.hstack(
                                    searchable_select(placeholder="Por tipo...", options=AppState.filtered_tipos_mochilas, on_change_select=AppState.set_filter_tipo_mochila, value_select=AppState.filter_tipo_mochila, search_value=AppState.search_tipo_mochila, on_change_search=AppState.set_search_tipo_mochila, filter_name="mochila_tipo"),
                                    rx.cond(AppState.filter_tipo_mochila != "", rx.icon_button(rx.icon("x", size=16), on_click=AppState.clear_filter("filter_tipo_mochila"), size="1", variant="ghost"))
                                ),
                                spacing="2", align_items="start", width="100%"
                            )
                        ),
                    ),
                    rx.fragment(
                        rx.vstack(
                            rx.divider(),
                            rx.text("Filtros Generales", weight="bold"),
                            rx.hstack(
                                searchable_select(placeholder="Por tipo...", options=AppState.filtered_tipos_general, on_change_select=AppState.set_filter_tipo_general, value_select=AppState.filter_tipo_general, search_value=AppState.search_tipo_general, on_change_search=AppState.set_search_tipo_general, filter_name="general_tipo"),
                                rx.cond(AppState.filter_tipo_general != "", rx.icon_button(rx.icon("x", size=16), on_click=AppState.clear_filter("filter_tipo_general"), size="1", variant="ghost"))
                            ),
                            rx.hstack(
                                searchable_select(placeholder="Por material o tela...", options=AppState.filtered_materiales, on_change_select=AppState.set_filter_material_tela, value_select=AppState.filter_material_tela, search_value=AppState.search_material_tela, on_change_search=AppState.set_search_material_tela, filter_name="general_material"),
                                rx.cond(AppState.filter_material_tela != "", rx.icon_button(rx.icon("x", size=16), on_click=AppState.clear_filter("filter_material_tela"), size="1", variant="ghost"))
                            ),
                            rx.hstack(
                                searchable_select(placeholder="Por talla o medidas...", options=AppState.filtered_medidas_general, on_change_select=AppState.set_filter_medida_talla, value_select=AppState.filter_medida_talla, search_value=AppState.search_medida_talla, on_change_search=AppState.set_search_medida_talla, filter_name="general_medida"),
                                rx.cond(AppState.filter_medida_talla != "", rx.icon_button(rx.icon("x", size=16), on_click=AppState.clear_filter("filter_medida_talla"), size="1", variant="ghost"))
                            ),
                            rx.hstack(
                                searchable_select(placeholder="Por color...", options=AppState.filtered_colores, on_change_select=AppState.set_filter_color, value_select=AppState.filter_color, search_value=AppState.search_color, on_change_search=AppState.set_search_color, filter_name="general_color"),
                                rx.cond(AppState.filter_color != "", rx.icon_button(rx.icon("x", size=16), on_click=AppState.clear_filter("filter_color"), size="1", variant="ghost"))
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
                on_click=AppState.toggle_filters,
                cursor="pointer",
                bg=rx.color("violet", 9),
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
            AppState.show_filters,
            "translateY(-50%)",
            "translate(-280px, -50%)"
        ),
        transition="transform 0.3s ease-in-out",
        z_index=1000,
        height="auto",
    )