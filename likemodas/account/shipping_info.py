# likemodas/account/shipping_info.py (CORREGIDO)

import reflex as rx
import reflex_local_auth
from ..state import AppState
from ..account.layout import account_layout
from ..models import ShippingAddressModel
from ..ui.components import searchable_select

def address_form() -> rx.Component:
    """Formulario rediseñado para crear una dirección, ahora responsivo."""
    return rx.form(
        rx.vstack(
            rx.heading("Nueva Dirección", size="6", width="100%"),
            rx.grid(
                rx.vstack(rx.text("Nombre Completo*"), rx.input(name="name", required=True), spacing="1", align_items="stretch"),
                rx.vstack(rx.text("Teléfono*"), rx.input(name="phone", required=True), spacing="1", align_items="stretch"),
                rx.vstack(rx.text("Ciudad*"), searchable_select(placeholder="Selecciona una ciudad...", options=AppState.cities, on_change_select=AppState.set_city, value_select=AppState.city, search_value=AppState.search_city, on_change_search=AppState.set_search_city, filter_name="shipping_city_filter"), spacing="1", align_items="stretch"),
                rx.vstack(rx.text("Barrio"), searchable_select(placeholder="Selecciona un barrio...", options=AppState.neighborhoods, on_change_select=AppState.set_neighborhood, value_select=AppState.neighborhood, search_value=AppState.search_neighborhood, on_change_search=AppState.set_search_neighborhood, filter_name="shipping_neighborhood_filter", is_disabled=~AppState.neighborhoods), spacing="1", align_items="stretch"),
                rx.vstack(rx.text("Dirección* (Calle, Carrera, Apto, etc.)"), rx.input(name="address", required=True), spacing="1", align_items="stretch", grid_column={"initial": "span 1", "md": "span 2"}),
                columns={"initial": "1", "md": "2"},
                spacing="4", width="100%",
            ),
            rx.hstack(rx.button("Cancelar", on_click=AppState.toggle_form, color_scheme="gray", variant="soft"), rx.button("Guardar Dirección", type="submit", color_scheme="violet"), justify="end", width="100%", margin_top="1.5em"),
            spacing="5", width="100%",
        ),
        on_submit=AppState.add_new_address,
        reset_on_submit=True,
    )

def address_card(address: ShippingAddressModel) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(rx.text(address.name, weight="bold", size="5"), rx.spacer(), rx.cond(address.is_default, rx.badge("Predeterminada", color_scheme="green")), width="100%"),
            rx.divider(),
            rx.text(f"{address.address}, {address.neighborhood}", size="3", color_scheme="gray"),
            rx.text(f"{address.city}", size="3", color_scheme="gray"),
            rx.text(f"Tel: {address.phone}", size="3", color_scheme="gray"),
            rx.hstack(rx.button("Eliminar", on_click=lambda: AppState.delete_address(address.id), variant="soft", color_scheme="red", size="1"), rx.spacer(), rx.button("Hacer Predeterminada", on_click=lambda: AppState.set_as_default(address.id), is_disabled=address.is_default, variant="outline", size="1", color_scheme="violet"), justify="end", width="100%", margin_top="1em"),
            align_items="start", spacing="3", width="100%",
        )
    )

@reflex_local_auth.require_login
def shipping_info_content() -> rx.Component:
    """Página para gestionar las direcciones de envío, con diseño mejorado."""
    # --- INICIO DE LA CORRECCIÓN DE LAYOUT ---
    page_content = rx.vstack(
        rx.heading("Mi Información para Envíos", size="8"),
        rx.text("Aquí puedes gestionar tus direcciones para agilizar tus compras.", color_scheme="gray", size="4"),
        rx.divider(margin_y="1.5em"),
        rx.cond(
            AppState.show_form,
            address_form(),
            rx.vstack(
                rx.cond(
                    AppState.addresses,
                    rx.grid(
                        rx.foreach(AppState.addresses, address_card),
                        columns={"initial": "1", "md": "2"},
                        spacing="5",
                        width="100%",
                    ),
                    rx.center(
                        rx.text("Aún no tienes direcciones guardadas."),
                        padding_y="3em",
                    )
                ),
                rx.button("Añadir Nueva Dirección", on_click=AppState.toggle_form, margin_top="2em", color_scheme="violet", size="3"),
                align_items="start",
                width="100%",
            )
        ),
        align="center",
        width="100%",
        max_width="1200px",
        spacing="5",
    )
    # --- FIN DE LA CORRECCIÓN DE LAYOUT ---
    return account_layout(page_content) 