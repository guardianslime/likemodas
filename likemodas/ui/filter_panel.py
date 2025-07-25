# likemodas/ui/filter_panel.py

import reflex as rx
from reflex.event import EventSpec
from ..auth.state import SessionState
from ..models import Category
from ..data.product_options import (
    LISTA_TIPOS_ROPA, LISTA_TIPOS_ZAPATOS, LISTA_TIPOS_MOCHILAS, LISTA_TIPOS_GENERAL
)

def _searchable_select(
    placeholder: str, 
    options: rx.Var[list[str]], 
    on_change_select: EventSpec,
    value_select: rx.Var[str],
    search_value: rx.Var[str],
    on_change_search: EventSpec,
    filter_name: str, # Nombre único para este filtro
) -> rx.Component:
    """
    Un componente de selección personalizado, construido desde cero para
    garantizar el control total sobre el diseño y la expansión.
    """
    is_open = SessionState.open_filter_name == filter_name

    return rx.box(
        # El botón que abre/cierra el menú
        rx.button(
            rx.cond(value_select, value_select, placeholder),
            rx.icon(tag="chevron-down"),
            on_click=SessionState.toggle_filter_dropdown(filter_name),
            variant="outline",
            width="100%",
            justify_content="space-between",
            color_scheme="gray",
        ),
        # El contenido del menú, que se muestra condicionalmente
        rx.cond(
            is_open,
            rx.vstack(
                rx.input(
                    placeholder="Buscar...",
                    value=search_value,
                    on_change=on_change_search,
                ),
                rx.scroll_area(
                    rx.vstack(
                        rx.foreach(
                            options,
                            lambda option: rx.button(
                                option,
                                # Al hacer clic, se selecciona y se cierra el menú
                                on_click=[
                                    lambda: on_change_select(option),
                                    SessionState.toggle_filter_dropdown(filter_name)
                                ],
                                width="100%",
                                variant="soft", 
                                color_scheme="gray",
                                justify_content="start"
                            )
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    max_height="200px",
                    width="100%",
                    type="auto",
                    scrollbars="vertical",
                ),
                # Estilo de la caja del menú
                spacing="2",
                padding="0.75em",
                bg=rx.color("gray", 3),
                border="1px solid",
                border_color=rx.color("gray", 7),
                border_radius="md",
                # Posicionamiento absoluto para que flote sobre el contenido
                position="absolute",
                top="105%", # Justo debajo del botón
                width="100%",
                z_index=10,
            )
        ),
        # El contenedor principal necesita ser relativo para el posicionamiento absoluto del hijo
        position="relative",
        width="100%",
    )


def floating_filter_panel() -> rx.Component:
    """
    El panel de filtros flotante, ahora usando el nuevo componente de selección.
    """
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
                    
                    rx.fragment(
                        rx.cond(
                            SessionState.current_category == Category.ROPA.value,
                            rx.vstack(
                                rx.divider(), rx.text("Filtros de Ropa", weight="bold"),
                                _searchable_select(
                                    placeholder="Filtrar por tipo...",
                                    options=SessionState.filtered_tipos_ropa,
                                    on_change_select=SessionState.set_filter_tipo_prenda,
                                    value_select=SessionState.filter_tipo_prenda,
                                    search_value=SessionState.search_tipo_prenda,
                                    on_change_search=SessionState.set_search_tipo_prenda,
                                    filter_name="ropa_tipo" # Se asigna un nombre único
                                ),
                                rx.input(placeholder="Filtrar por color...", value=SessionState.filter_color, on_change=SessionState.set_filter_color),
                                rx.input(placeholder="Filtrar por talla...", value=SessionState.filter_talla, on_change=SessionState.set_filter_talla),
                                spacing="2", align_items="start", width="100%"
                            )
                        ),
                        rx.cond(
                            SessionState.current_category == Category.CALZADO.value,
                            rx.vstack(
                                rx.divider(), rx.text("Filtros de Calzado", weight="bold"),
                                _searchable_select(
                                    placeholder="Filtrar por tipo...",
                                    options=SessionState.filtered_tipos_zapatos,
                                    on_change_select=SessionState.set_filter_tipo_zapato,
                                    value_select=SessionState.filter_tipo_zapato,
                                    search_value=SessionState.search_tipo_zapato,
                                    on_change_search=SessionState.set_search_tipo_zapato,
                                    filter_name="calzado_tipo" # Nombre único
                                ),
                                rx.input(placeholder="Filtrar por color...", value=SessionState.filter_color, on_change=SessionState.set_filter_color),
                                rx.input(placeholder="Filtrar por número...", value=SessionState.filter_numero_calzado, on_change=SessionState.set_filter_numero_calzado),
                                spacing="2", align_items="start", width="100%"
                            )
                        ),
                        rx.cond(
                            SessionState.current_category == Category.MOCHILAS.value,
                            rx.vstack(
                                rx.divider(), rx.text("Filtros de Mochilas", weight="bold"),
                                _searchable_select(
                                    placeholder="Filtrar por tipo...",
                                    options=SessionState.filtered_tipos_mochilas,
                                    on_change_select=SessionState.set_filter_tipo_mochila,
                                    value_select=SessionState.filter_tipo_mochila,
                                    search_value=SessionState.search_tipo_mochila,
                                    on_change_search=SessionState.set_search_tipo_mochila,
                                    filter_name="mochila_tipo" # Nombre único
                                ),
                                spacing="2", align_items="start", width="100%"
                            )
                        ),
                    ),
                    
                    rx.fragment(
                        rx.vstack(
                            rx.divider(),
                            rx.text("Filtros Generales", weight="bold"),
                            _searchable_select(
                                placeholder="Filtrar por tipo...",
                                options=SessionState.filtered_tipos_general,
                                on_change_select=SessionState.set_filter_tipo_general,
                                value_select=SessionState.filter_tipo_general,
                                search_value=SessionState.search_tipo_general,
                                on_change_search=SessionState.set_search_tipo_general,
                                filter_name="general_tipo" # Nombre único
                            ),
                            rx.input(placeholder="Material o tela...", value=SessionState.filter_material_tela, on_change=SessionState.set_filter_material_tela),
                            rx.input(placeholder="Talla o medidas...", value=SessionState.filter_medida_talla, on_change=SessionState.set_filter_medida_talla),
                            rx.input(placeholder="Color...", value=SessionState.filter_color, on_change=SessionState.set_filter_color),
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