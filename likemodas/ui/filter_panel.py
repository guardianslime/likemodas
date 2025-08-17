# likemodas/ui/filter_panel.py (VERSIÓN FINAL CORREGIDA)

import reflex as rx
from ..state import AppState
from ..models import Category
from ..ui.components import multi_select_component

def floating_filter_panel() -> rx.Component:
    """
    Panel de filtros con selección múltiple, lógica condicional
    y área de desplazamiento.
    """
    # --- ✨ AÑADIDO: Envolvemos el contenido en un ScrollArea ---
    filter_content = rx.scroll_area(
        rx.vstack(
            # Encabezado del panel
            rx.hstack(
                rx.heading("Filtros", size="6"),
                rx.spacer(),
                rx.button("Limpiar", on_click=AppState.clear_all_filters, size="1", variant="soft", color_scheme="gray"),
                justify="between", align_items="center", width="100%"
            ),
            rx.divider(),
            
            # Filtro de Precio
            rx.vstack(
                rx.text("Precio", weight="bold"),
                rx.input(placeholder="Mínimo", value=AppState.min_price, on_change=AppState.set_min_price, type="number"),
                rx.input(placeholder="Máximo", value=AppState.max_price, on_change=AppState.set_max_price, type="number"),
                spacing="2", align_items="start", width="100%"
            ),

            # Lógica Condicional para mostrar filtros
            rx.cond(
                (AppState.current_category != "") & (AppState.current_category != "todos"),
                # Filtros Específicos por Categoría (sin cambios)
                rx.fragment(
                    rx.cond(AppState.current_category == Category.ROPA.value, ...),
                    rx.cond(AppState.current_category == Category.CALZADO.value, ...),
                    rx.cond(AppState.current_category == Category.MOCHILAS.value, ...),
                ),
                # --- ✨ SECCIÓN CORREGIDA: Filtros Generales ---
                rx.vstack(
                    rx.divider(),
                    rx.text("Filtros Generales", weight="bold"),
                    multi_select_component(
                        placeholder="Añadir color...",
                        options=AppState.filtered_colores,
                        selected_items=AppState.filter_colors,
                        add_handler=AppState.add_filter_value,
                        remove_handler=AppState.remove_filter_value,
                        prop_name="filter_colors",
                        search_value=AppState.search_color,
                        on_change_search=AppState.set_search_color,
                        filter_name="general_color_filter",
                    ),
                    # --- ✨ AÑADIDO: Filtro de Material ---
                    multi_select_component(
                        placeholder="Añadir material...",
                        options=AppState.filtered_materiales,
                        selected_items=AppState.filter_materiales_tela,
                        add_handler=AppState.add_filter_value,
                        remove_handler=AppState.remove_filter_value,
                        prop_name="filter_materiales_tela",
                        search_value=AppState.search_material_tela,
                        on_change_search=AppState.set_search_material_tela,
                        filter_name="general_material_filter",
                    ),
                    # --- ✨ AÑADIDO: Filtro de Talla/Medida ---
                    multi_select_component(
                        placeholder="Añadir talla/medida...",
                        options=AppState.filtered_medidas_general,
                        selected_items=AppState.filter_tallas,
                        add_handler=AppState.add_filter_value,
                        remove_handler=AppState.remove_filter_value,
                        prop_name="filter_tallas",
                        search_value=AppState.search_talla,
                        on_change_search=AppState.set_search_talla,
                        filter_name="general_talla_filter",
                    ),
                    spacing="2", align_items="stretch", width="100%"
                )
            ),
            spacing="4", padding="1.5em", width="100%",
        ),
        type="auto", scrollbars="vertical", style={"height": "calc(100% - 2em)"}
    )

    return rx.box(
        rx.hstack(
            # Usamos el contenido con scroll que definimos arriba
            rx.box(filter_content, height="90vh", width="280px", bg=rx.color("gray", 2)),
            # Botón para mostrar/ocultar
            rx.box(
                rx.text("Filtros", style={"writing_mode": "vertical-rl", "transform": "rotate(180deg)", "padding": "0.5em 0.09em", "font_weight": "bold", "letter_spacing": "2px", "color": "white"}),
                on_click=AppState.toggle_filters, cursor="pointer", bg=rx.color("violet", 9),
                border_radius="0 8px 8px 0", height="120px", display="flex", align_items="center"
            ),
            align_items="center", spacing="0"
        ),
        position="fixed", top="50%", left="0",
        transform=rx.cond(AppState.show_filters, "translateY(-50%)", "translate(-280px, -50%)"),
        transition="transform 0.3s ease-in-out", z_index="1000", height="auto",
    )