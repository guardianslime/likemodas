# likemodas/ui/filter_panel.py (VERSIÓN CON ANIDACIÓN CORRECTA)

import reflex as rx
from ..state import AppState
from ..models import Category
from ..ui.components import multi_select_component

def floating_filter_panel() -> rx.Component:
    """
    Panel de filtros con selección múltiple y anidación correcta de rx.cond
    para mostrar filtros específicos por categoría.
    """
    # Define los bloques de filtros por categoría para mayor claridad
    filtros_ropa = rx.vstack(
        rx.divider(), rx.text("Filtros de Ropa", weight="bold"),
        multi_select_component(
            placeholder="Añadir tipo...", options=AppState.filtered_tipos_ropa,
            selected_items=AppState.filter_tipos_prenda, add_handler=AppState.add_filter_value,
            remove_handler=AppState.remove_filter_value, prop_name="filter_tipos_prenda",
            search_value=AppState.search_tipo_prenda, on_change_search=AppState.set_search_tipo_prenda,
            filter_name="ropa_tipo_filter",
        ),
        multi_select_component(
            placeholder="Añadir talla...", options=AppState.filtered_tallas_ropa,
            selected_items=AppState.filter_tallas, add_handler=AppState.add_filter_value,
            remove_handler=AppState.remove_filter_value, prop_name="filter_tallas",
            search_value=AppState.search_talla, on_change_search=AppState.set_search_talla,
            filter_name="ropa_talla_filter",
        ),
        spacing="2", align_items="start", width="100%"
    )

    filtros_calzado = rx.vstack(
        rx.divider(), rx.text("Filtros de Calzado", weight="bold"),
        multi_select_component(
            placeholder="Añadir tipo...", options=AppState.filtered_tipos_zapatos,
            selected_items=AppState.filter_tipos_zapato, add_handler=AppState.add_filter_value,
            remove_handler=AppState.remove_filter_value, prop_name="filter_tipos_zapato",
            search_value=AppState.search_tipo_zapato, on_change_search=AppState.set_search_tipo_zapato,
            filter_name="calzado_tipo_filter",
        ),
        multi_select_component(
            placeholder="Añadir número...", options=AppState.filtered_numeros_calzado,
            selected_items=AppState.filter_numeros_calzado, add_handler=AppState.add_filter_value,
            remove_handler=AppState.remove_filter_value, prop_name="filter_numeros_calzado",
            search_value=AppState.search_numero_calzado, on_change_search=AppState.set_search_numero_calzado,
            filter_name="calzado_numero_filter",
        ),
        spacing="2", align_items="start", width="100%"
    )
    
    filtros_mochilas = rx.vstack(
        rx.divider(), rx.text("Filtros de Mochilas", weight="bold"),
        multi_select_component(
            placeholder="Añadir tipo...", options=AppState.filtered_tipos_mochilas,
            selected_items=AppState.filter_tipos_mochila, add_handler=AppState.add_filter_value,
            remove_handler=AppState.remove_filter_value, prop_name="filter_tipos_mochila",
            search_value=AppState.search_tipo_mochila, on_change_search=AppState.set_search_tipo_mochila,
            filter_name="mochila_tipo_filter",
        ),
        spacing="2", align_items="start", width="100%"
    )
    
    filtros_generales = rx.vstack(
        rx.divider(), rx.text("Filtros Generales", weight="bold"),
        multi_select_component(
            placeholder="Añadir color...", options=AppState.filtered_colores,
            selected_items=AppState.filter_colors, add_handler=AppState.add_filter_value,
            remove_handler=AppState.remove_filter_value, prop_name="filter_colors",
            search_value=AppState.search_color, on_change_search=AppState.set_search_color,
            filter_name="general_color_filter",
        ),
        # ... puedes añadir más filtros generales aquí si quieres ...
        spacing="2", align_items="stretch", width="100%"
    )
    
    filter_content = rx.scroll_area(
        rx.vstack(
            rx.hstack(
                rx.heading("Filtros", size="6"),
                rx.spacer(),
                rx.button("Limpiar", on_click=AppState.clear_all_filters, size="1", variant="soft", color_scheme="gray"),
                justify="between", align_items="center", width="100%"
            ),
            rx.divider(),
            rx.vstack(
                rx.text("Precio", weight="bold"),
                rx.input(placeholder="Mínimo", value=AppState.min_price, on_change=AppState.set_min_price, type="number"),
                rx.input(placeholder="Máximo", value=AppState.max_price, on_change=AppState.set_max_price, type="number"),
                spacing="2", align_items="start", width="100%"
            ),

            # --- ✨ CORRECCIÓN: Anidación correcta de rx.cond para if-elif-else ---
            rx.cond(
                (AppState.current_category != "") & (AppState.current_category != "todos"),
                # if: hay una categoría específica
                rx.cond(
                    AppState.current_category == Category.ROPA.value,
                    filtros_ropa,
                    # else if: no es Ropa, ¿es Calzado?
                    rx.cond(
                        AppState.current_category == Category.CALZADO.value,
                        filtros_calzado,
                        # else if: no es Calzado, ¿es Mochilas?
                        rx.cond(
                            AppState.current_category == Category.MOCHILAS.value,
                            filtros_mochilas,
                            # else: es otra categoría, no mostrar filtros específicos
                            rx.fragment()
                        )
                    )
                ),
                # else: no hay categoría específica (página de inicio)
                filtros_generales
            ),
            spacing="4", padding="1.5em", width="100%",
        ),
        type="auto", scrollbars="vertical", style={"height": "calc(100% - 2em)"}
    )

    return rx.box(
        rx.hstack(
            rx.box(filter_content, height="90vh", width="280px", bg=rx.color("gray", 2)),
            rx.box(
                rx.text("Filtros", style={"writing_mode": "vertical-rl", "transform": "rotate(180deg)", "padding": "0.5em 0.09em", "font_weight": "bold", "letter_spacing": "2px", "color": "white"}),
                on_click=AppState.toggle_filters, cursor="pointer", bg=rx.color("violet", 9),
                border_radius="0 8px 8px 0", height="120px", display="flex", align_items="center"
            ),
            align_items="center", spacing="0"
        ),
        position="fixed", top="50%", left="0",
        transform=rx.cond(AppState.show_filters, "translateY(-50%)", "translate(-280px, -50%)"),
        transition="transform 0.3s ease-in-out", z_index=1000, height="auto",
    )