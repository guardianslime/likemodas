# likemodas/account/shipping_info.py (VERSIÓN COMPLETA Y CORREGIDA)

import reflex as rx
import reflex_local_auth
from ..state import AppState
from ..account.layout import account_layout
from ..models import ShippingAddressModel
from ..ui.components import searchable_select

# 1. Se define el script que se inyectará en la página.
# Este script define la función `getLocation`, que buscará los callbacks en el objeto `window`.
GET_LOCATION_SCRIPT = """
function getLocation() {
    if (!window.onLocationSuccess || !window.onLocationError) {
        console.error("Reflex callbacks no están definidos.");
        return;
    }
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                // Unimos lat y lon en una sola cadena separada por coma.
                const coords_string = `${position.coords.latitude},${position.coords.longitude}`;
                window.onLocationSuccess(coords_string);
            },
            (error) => {
                window.onLocationError();
            }
        );
    } else {
        alert("La geolocalización no es soportada por este navegador.");
    }
}
"""

def address_form() -> rx.Component:
    """Formulario para crear una nueva dirección."""
    return rx.form(
        rx.vstack(
            rx.heading("Nueva Dirección de Envío", size="6", width="100%"),
            # 2. Se inyecta el script para que la función `getLocation` esté disponible.
            rx.script(GET_LOCATION_SCRIPT),

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
                rx.vstack(
                    rx.text("Ciudad*"),
                    searchable_select(
                        placeholder="Selecciona una ciudad...",
                        options=AppState.cities,
                        on_change_select=AppState.set_city,
                        value_select=AppState.city,
                        search_value=AppState.search_city,
                        on_change_search=AppState.set_search_city,
                        filter_name="shipping_city_filter",
                    ),
                    spacing="1", align_items="start",
                ),
                rx.vstack(
                    rx.text("Barrio"),
                    searchable_select(
                        placeholder="Selecciona un barrio...",
                        options=AppState.neighborhoods,
                        on_change_select=AppState.set_neighborhood,
                        value_select=AppState.neighborhood,
                        search_value=AppState.search_neighborhood,
                        on_change_search=AppState.set_search_neighborhood,
                        filter_name="shipping_neighborhood_filter",
                        is_disabled=(AppState.neighborhoods.length() == 0), # ✅ CORRECTO
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
            
            rx.box(height="1em"),
            rx.text(
                "Opcional: Para mayor precisión en la entrega, añade tu ubicación exacta.", 
                size="2", 
                color_scheme="gray",
                text_align="center",
                width="100%"
            ),

            # --- ✨ 2. MODIFICAMOS EL BOTÓN ✨ ---
            rx.button(
                rx.icon(tag="map-pin", margin_right="0.5em"),
                "Añadir mi ubicación con mapa",
                on_click=[
                    # Usamos el nuevo EventHandler 'set_location_from_string' que solo espera un argumento.
                    rx.call_script(f"window.onLocationSuccess = (coords) => {{ {AppState.set_location_from_string}(coords) }}"),
                    
                    rx.call_script("window.onLocationError = () => { alert('No se pudo obtener la ubicación. Por favor, asegúrese de haber concedido los permisos.') }"),
                    
                    rx.call_script("getLocation()"),
                ],
                variant="outline",
                width="100%",
            ),
            # --- ✨ FIN DE LA MODIFICACIÓN ✨ ---

            rx.hstack(
                rx.button("Cancelar", on_click=AppState.toggle_form, color_scheme="gray"),
                rx.button("Guardar Dirección", type="submit", width="auto"),
                justify="end", width="100%", margin_top="1em"
            ),
            spacing="4", width="100%",
        ),
        on_submit=AppState.add_new_address,
        reset_on_submit=True,
    )

def address_card(address: ShippingAddressModel) -> rx.Component:
    """Componente para mostrar una dirección guardada."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(address.name, weight="bold"),
                rx.spacer(),
                rx.cond(address.is_default, rx.badge("Predeterminada", color_scheme="green")),
                width="100%"
            ),
            rx.text(f"{address.address}, {address.neighborhood}"),
            rx.text(f"{address.city}"),
            rx.text(f"Tel: {address.phone}"),

            # Muestra un badge y un enlace si la ubicación fue guardada.
            rx.cond(
                address.latitude,
                rx.link(
                    rx.badge(
                        rx.icon(tag="check-check", size=14),
                        "Ubicación guardada. Ver en mapa.",
                        color_scheme="blue",
                        variant="soft",
                        padding_x="0.75em",
                        margin_top="0.5em",
                    ),
                    # Enlace a Google Maps con las coordenadas.
                    href=f"https://www.google.com/maps/search/?api=1&query={address.latitude},{address.longitude}",
                    is_external=True,
                )
            ),

            rx.divider(),
            rx.hstack(
                rx.button("Eliminar", on_click=lambda: AppState.delete_address(address.id), variant="soft", color_scheme="red", size="2"),
                rx.button(
                    "Hacer Predeterminada",
                    on_click=lambda: AppState.set_as_default(address.id),
                    is_disabled=address.is_default,
                    variant="outline", size="2"
                ),
                justify="end", width="100%"
            ),
            align_items="start", spacing="2"
        ),
        border="1px solid #ededed", border_radius="md", padding="1em", width="100%"
    )

@reflex_local_auth.require_login
def shipping_info_content() -> rx.Component:
    """Página para gestionar las direcciones de envío."""
    return account_layout(
        rx.vstack(
            rx.heading("Mi Información para Envíos", size="7"),
            rx.text("Aquí puedes gestionar tus direcciones de envío.", margin_bottom="1.5em"),
            rx.foreach(AppState.addresses, address_card),
            rx.cond(
                (AppState.show_form == False), # ✅ CORRECTO
                rx.button("Crear Nueva Dirección", on_click=AppState.toggle_form, margin_top="2em"),
            ),
            rx.cond(AppState.show_form, address_form()),
            align_items="start", width="100%", max_width="700px"
        )
    )