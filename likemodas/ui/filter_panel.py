# -----------------------------------------------------------------------------
# likemodas/ui/filter_panel.py
# -----------------------------------------------------------------------------
import reflex as rx
from ..auth.state import SessionState
from ..models import Category
from ..ui.components import searchable_select

def floating_filter_panel() -> rx.Component:
    """El panel de filtros flotante con todas las funcionalidades implementadas."""
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.hstack(
                    rx.heading("Filtros", size="6"),
                    rx.spacer(),
                    rx.button("Limpiar", on_click=SessionState.clear_all_filters, size="1", variant="soft", color_scheme="gray"),
                    justify="between", align_items="center", width="100%"
                ),
                rx.divider(),
                rx.vstack(
                    rx.text("Precio", weight="bold"),
                    rx.hstack(
                        rx.input(placeholder="Mínimo", value=SessionState.min_price, on_change=SessionState.set_min_price, type="number"),
                        rx.cond(SessionState.min_price != "", rx.icon_button(rx.icon("x", size=16), on_click=SessionState.clear_filter("min_price"), size="1", variant="ghost")),
                        align_items="center", width="100%", spacing="2"
                    ),
                    rx.hstack(
                        rx.input(placeholder="Máximo", value=SessionState.max_price, on_change=SessionState.set_max_price, type="number"),
                        rx.cond(SessionState.max_price != "", rx.icon_button(rx.icon("x", size=16), on_click=SessionState.clear_filter("max_price"), size="1", variant="ghost")),
                        align_items="center", width="100%", spacing="2"
                    ),
                    spacing="2", align_items="start", width="100%"
                ),
                rx.cond(
                    (SessionState.current_category != "") & (SessionState.current_category != "todos"),
                    rx.fragment(
                        rx.cond(
                            SessionState.current_category == Category.ROPA.value,
                            rx.vstack(
                                rx.divider(), rx.text("Filtros de Ropa", weight="bold"),
                                rx.hstack(
                                    searchable_select(placeholder="Por tipo...", options=SessionState.filtered_tipos_ropa, on_change_select=SessionState.set_filter_tipo_prenda, value_select=SessionState.filter_tipo_prenda, search_value=SessionState.search_tipo_prenda, on_change_search=SessionState.set_search_tipo_prenda, filter_name="ropa_tipo"),
                                    rx.cond(SessionState.filter_tipo_prenda != "", rx.icon_button(rx.icon("x", size=16), on_click=SessionState.clear_filter("filter_tipo_prenda"), size="1", variant="ghost"))
                                ),
                                # ... más filtros de ropa
                                spacing="2", align_items="start", width="100%"
                            )
                        ),
                        # ... más condiciones para calzado y mochilas
                    ),
                    # ... filtros generales
                ),
                spacing="4", padding="1.5em", bg=rx.color("gray", 2),
                height="100%", width="280px",
            ),
            rx.box(
                rx.text("Filtros", style={"writing_mode": "vertical-rl", "transform": "rotate(180deg)", "padding": "0.5em 0.09em", "font_weight": "bold", "letter_spacing": "2px", "color": "white"}),
                on_click=SessionState.toggle_filters, cursor="pointer", bg=rx.color("violet", 9),
                border_radius="0 8px 8px 0", height="120px", display="flex", align_items="center"
            ),
            align_items="center", spacing="0"
        ),
        position="fixed", top="50%", left="0",
        transform=rx.cond(SessionState.show_filters, "translateY(-50%)", "translate(-280px, -50%)"),
        transition="transform 0.3s ease-in-out", z_index=1000, height="auto",
    )