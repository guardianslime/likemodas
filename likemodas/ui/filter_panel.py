# likemodas/ui/filter_panel.py

import reflex as rx
from ..auth.state import SessionState
from ..pages.category_page import CategoryPageState # Import to get current category
from ..models import Category
# Import the data lists to populate the filter selectors
from ..blog.forms import LISTA_TIPOS_ROPA, LISTA_TIPOS_ZAPATOS, LISTA_TIPOS_MOCHILAS 

def floating_filter_panel() -> rx.Component:
    """
    Un panel de filtros flotante y deslizable desde la izquierda.
    """
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.heading("Filtros", size="6", width="100%"),
                rx.divider(),
                
                # --- Price Filter (Always Visible) ---
                rx.vstack(
                    rx.text("Precio", weight="bold"),
                    rx.input(placeholder="Mínimo", value=SessionState.min_price, on_change=SessionState.set_min_price, type="number"),
                    rx.input(placeholder="Máximo", value=SessionState.max_price, on_change=SessionState.set_max_price, type="number"),
                    spacing="2", align_items="start", width="100%"
                ),

                # --- ✨ DYNAMIC FILTERS BASED ON CATEGORY ---
                # Ropa Filters
                rx.cond(
                    CategoryPageState.current_category == Category.ROPA.value,
                    rx.vstack(
                        rx.divider(),
                        rx.text("Filtros de Ropa", weight="bold"),
                        rx.select(LISTA_TIPOS_ROPA, placeholder="Filtrar por tipo...", value=SessionState.filter_tipo_prenda, on_change=SessionState.set_filter_tipo_prenda),
                        rx.input(placeholder="Filtrar por color...", value=SessionState.filter_color, on_change=SessionState.set_filter_color),
                        rx.input(placeholder="Filtrar por talla...", value=SessionState.filter_talla, on_change=SessionState.set_filter_talla),
                        spacing="2", align_items="start", width="100%"
                    )
                ),

                # Calzado Filters
                rx.cond(
                    CategoryPageState.current_category == Category.CALZADO.value,
                    rx.vstack(
                        rx.divider(),
                        rx.text("Filtros de Calzado", weight="bold"),
                        rx.select(LISTA_TIPOS_ZAPATOS, placeholder="Filtrar por tipo...", value=SessionState.filter_tipo_zapato, on_change=SessionState.set_filter_tipo_zapato),
                        rx.input(placeholder="Filtrar por color...", value=SessionState.filter_color, on_change=SessionState.set_filter_color),
                        rx.input(placeholder="Filtrar por número...", value=SessionState.filter_numero_calzado, on_change=SessionState.set_filter_numero_calzado),
                        spacing="2", align_items="start", width="100%"
                    )
                ),

                # Mochilas Filters
                rx.cond(
                    CategoryPageState.current_category == Category.MOCHILAS.value,
                    rx.vstack(
                        rx.divider(),
                        rx.text("Filtros de Mochilas", weight="bold"),
                        rx.select(LISTA_TIPOS_MOCHILAS, placeholder="Filtrar por tipo...", value=SessionState.filter_tipo_mochila, on_change=SessionState.set_filter_tipo_mochila),
                        spacing="2", align_items="start", width="100%"
                    )
                ),

                spacing="4", padding="1.5em", bg=rx.color("gray", 2),
                height="100%", width="280px",
            ),
            rx.box(
                rx.text(
                    "Filtros",
                    style={
                        "writing_mode": "vertical-rl",
                        "transform": "rotate(180deg)",
                        # --- 👇 REDUCE EL SEGUNDO VALOR DEL PADDING 👇 ---
                        "padding": "0.5em 0.09em", # Antes era "1em 0.5em"
                        "font_weight": "bold",
                        "letter_spacing": "2px",
                        "color": "white"
                    }
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
            SessionState.show_filters, # <-- CAMBIO
            "translateY(-50%)",
            "translate(-280px, -50%)"
        ),
        transition="transform 0.3s ease-in-out",
        z_index="1000",
        height="auto",
    )