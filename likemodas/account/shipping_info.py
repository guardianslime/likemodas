import reflex as rx
import reflex_local_auth
from ..ui.base import base_page
from .layout import account_layout
from .shipping_info_state import ShippingInfoState
from ..models import ShippingAddressModel
from ..ui.components import searchable_select # <-- Se importa el componente

def address_form() -> rx.Component:
    """Formulario para crear una nueva dirección con selectores de búsqueda."""
    return rx.form(
        rx.vstack(
            rx.heading("Nueva Dirección de Envío", size="6", width="100%"),
            rx.grid(
                rx.vstack(
                    rx.text("Nombre Completo*"),
                    rx.input(name="name", type="text", required=True),
                    spacing="1", align_items="start",
                ),
                rx.vstack(
                    rx.text("Teléfono de Contacto*"),
                    rx.input(name="phone", type="tel", required=True),
                    spacing="1", align_items="start",
                ),
                # --- ✨ CAMBIO: Campo de texto de Ciudad reemplazado ---
                rx.vstack(
                    rx.text("Ciudad*"),
                    searchable_select(
                        placeholder="Selecciona una ciudad...",
                        options=ShippingInfoState.cities,
                        on_change_select=ShippingInfoState.set_city,
                        value_select=ShippingInfoState.city,
                        search_value=ShippingInfoState.search_city,
                        on_change_search=ShippingInfoState.set_search_city,
                        filter_name="shipping_city_filter",
                    ),
                    spacing="1", align_items="start",
                ),
                # --- ✨ CAMBIO: Campo de texto de Barrio reemplazado ---
                rx.vstack(
                    rx.text("Barrio"),
                    searchable_select(
                        placeholder="Selecciona un barrio...",
                        options=ShippingInfoState.neighborhoods,
                        on_change_select=ShippingInfoState.set_neighborhood,
                        value_select=ShippingInfoState.neighborhood,
                        search_value=ShippingInfoState.search_neighborhood,
                        on_change_search=ShippingInfoState.set_search_neighborhood,
                        filter_name="shipping_neighborhood_filter",
                        is_disabled=~rx.Var.list(ShippingInfoState.neighborhoods).length() > 0,
                    ),
                    spacing="1", align_items="start",
                ),
                rx.vstack(
                    rx.text("Dirección de Entrega*"),
                    rx.input(name="address", type="text", required=True),
                    spacing="1", align_items="start",
                    grid_column="span 2",
                ),
                columns="2", spacing="4", width="100%",
            ),
            rx.hstack(
                rx.button("Cancelar", on_click=ShippingInfoState.toggle_form, color_scheme="gray"),
                rx.button("Guardar Dirección", type="submit", width="auto"),
                justify="end", width="100%", margin_top="1em"
            ),
            spacing="4", width="100%",
        ),
        on_submit=ShippingInfoState.add_new_address,
        reset_on_submit=True,
    )

def address_card(address: ShippingAddressModel) -> rx.Component:
    """Componente para mostrar una dirección guardada."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(address.name, weight="bold"),
                rx.spacer(),
                rx.cond(
                    address.is_default,
                    rx.badge("Predeterminada", color_scheme="green"),
                ),
                width="100%"
            ),
            rx.text(f"{address.address}, {address.neighborhood}"),
            rx.text(f"{address.city}"),
            rx.text(f"Tel: {address.phone}"),
            rx.divider(),
            rx.hstack(
                rx.button("Eliminar", on_click=ShippingInfoState.delete_address(address.id), variant="soft", color_scheme="red", size="2"),
                rx.button(
                    "Hacer Predeterminada",
                    on_click=ShippingInfoState.set_as_default(address.id),
                    is_disabled=address.is_default,
                    variant="outline",
                    size="2"
                ),
                justify="end", width="100%"
            ),
            align_items="start",
            spacing="2"
        ),
        border="1px solid #ededed",
        border_radius="md",
        padding="1em",
        width="100%"
    )

@reflex_local_auth.require_login
def shipping_info_page() -> rx.Component:
    """Página para gestionar las direcciones de envío."""
    return base_page(
        account_layout(
            rx.vstack(
                rx.heading("Mi Información para Envíos", size="7"),
                rx.text(
                    "Aquí puedes gestionar tus direcciones de envío. La dirección predeterminada se usará para tus futuras compras.",
                    margin_bottom="1.5em"
                ),
                rx.foreach(ShippingInfoState.addresses, address_card),
                rx.cond(
                    ~ShippingInfoState.show_form,
                    rx.button("Crear Nueva Dirección", on_click=ShippingInfoState.toggle_form, margin_top="2em"),
                ),
                rx.cond(
                    ShippingInfoState.show_form,
                    address_form()
                ),
                align_items="start",
                width="100%",
                max_width="700px"
            )
        )
    )