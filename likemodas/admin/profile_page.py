import reflex as rx
from ..state import AppState
from ..auth.admin_auth import require_admin
from ..ui.components import searchable_select

@require_admin
def seller_profile_page() -> rx.Component:
    """Página para que el vendedor (admin) configure su ubicación de origen."""
    return rx.container(
        rx.vstack(
            rx.heading("Mi Ubicación de Origen", size="7"),
            rx.text(
                "Establece el barrio y la dirección desde donde envías tus productos. ",
                "El costo de envío se calculará a partir de esta ubicación.",
                margin_bottom="1.5em"
            ),
            rx.form(
                rx.vstack(
                    rx.text("Mi Barrio*", weight="bold"),
                    searchable_select(
                        placeholder="Selecciona tu barrio...",
                        options=AppState.filtered_seller_barrios,
                        on_change_select=AppState.set_seller_profile_barrio,
                        value_select=AppState.seller_profile_barrio,
                        search_value=AppState.search_seller_barrio,
                        on_change_search=AppState.set_search_seller_barrio,
                        filter_name="seller_barrio_filter",
                    ),
                    rx.text("Mi Dirección*", weight="bold", margin_top="1em"),
                    rx.input(
                        name="seller_address",
                        placeholder="Ej: Calle 5 # 10-20",
                        value=AppState.seller_profile_address,
                        on_change=AppState.set_seller_profile_address,
                        required=True
                    ),
                    rx.button("Guardar Mi Ubicación", type="submit", margin_top="2em", color_scheme="violet"),
                    spacing="3",
                    align_items="stretch"
                ),
                on_submit=AppState.save_seller_profile,
            ),
            align="stretch",
            width="100%",
            max_width="600px",
        ),
        padding_top="2em",
        min_height="85vh",
    )