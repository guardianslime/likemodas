# likemodas/account/shipping_info.py (CORREGIDO)

import reflex as rx
import reflex_local_auth
from ..state import AppState
from ..account.layout import account_layout
from ..models import ShippingAddressModel
from ..ui.components import searchable_select

# --- ✨ INICIO: CÓDIGO JAVASCRIPT ✨ ---
# Este script se llamará desde el botón. Pide la ubicación y llama a un EventHandler de Reflex.
get_location_script = """
if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
        (position) => {
            reflex.call_event(
                "set_location_coordinates",
                [position.coords.latitude, position.coords.longitude]
            );
        },
        (error) => {
            alert("No se pudo obtener la ubicación. Por favor, asegúrate de haber concedido los permisos.");
        }
    );
} else {
    alert("La geolocalización no es soportada por este navegador.");
}
"""
# --- ✨ FIN: CÓDIGO JAVASCRIPT ✨ ---


def address_form() -> rx.Component:
    """Formulario para crear una nueva dirección."""
    return rx.form(
        rx.vstack(
            rx.heading("Nueva Dirección de Envío", size="6", width="100%"),
            # ... (tu rx.grid con los inputs no cambia)
            rx.grid(
                # ... (todos tus rx.vstack para nombre, teléfono, ciudad, etc.)
                grid_column="span 2",
            ),

            # --- ✨ INICIO DE LA MODIFICACIÓN ✨ ---
            rx.box(height="1em"),
            rx.text(
                "Opcional: Para mayor precisión en la entrega, añade tu ubicación exacta.", 
                size="2", 
                color_scheme="gray",
                text_align="center",
                width="100%"
            ),
            rx.button(
                rx.icon(tag="map-pin", margin_right="0.5em"),
                "Añadir mi ubicación con mapa",
                # Llamamos al script de JavaScript al hacer clic.
                on_click=rx.call_script(get_location_script),
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

            # --- ✨ INICIO DE LA MODIFICACIÓN ✨ ---
            # Muestra un badge y un enlace si la ubicación fue guardada.
            rx.cond(
                address.latitude,
                rx.link(
                    rx.badge(
                        rx.icon(tag="check-circle", size=14), # <-- ASÍ QUEDA CORREGIDO
                        "Ubicación guardada. Ver en mapa.",
                        color_scheme="blue",
                        variant="soft",
                        padding_x="0.75em",
                        margin_top="0.5em",
                    ),
                    # Enlace a Google Maps con las coordenadas.
                    href=f"https://www.google.com/maps?q={address.latitude},{address.longitude}",
                    is_external=True,
                )
            ),
            # --- ✨ FIN DE LA MODIFICACIÓN ✨ ---

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
                ~AppState.show_form,
                rx.button("Crear Nueva Dirección", on_click=AppState.toggle_form, margin_top="2em"),
            ),
            rx.cond(AppState.show_form, address_form()),
            align_items="start", width="100%", max_width="700px"
        )
    )