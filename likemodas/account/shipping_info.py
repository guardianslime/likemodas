# likemodas/account/shipping_info.py (VERSIÓN FINAL Y COMPATIBLE)

import reflex as rx
import reflex_local_auth
from ..state import AppState
from ..account.layout import account_layout
from ..models import ShippingAddressModel
from ..ui.components import searchable_select

# --- ✨ 1. DEFINIMOS EL SCRIPT GLOBAL ✨ ---
# Este script define nuestra función, que buscará los callbacks en el objeto 'window'.
GET_LOCATION_SCRIPT = """
function getLocation() {
    if (!window.onLocationSuccess || !window.onLocationError) {
        console.error("Reflex callbacks no están definidos. El evento on_click debe definirlos.");
        return;
    }
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                // Llama al callback de éxito que definimos dinámicamente.
                window.onLocationSuccess(position.coords.latitude, position.coords.longitude);
            },
            (error) => {
                // Llama al callback de error.
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
            # --- ✨ 2. INYECTAMOS EL SCRIPT EN LA PÁGINA ✨ ---
            # Esto asegura que la función `getLocation` exista.
            rx.script(GET_LOCATION_SCRIPT),

            # ... (tu rx.grid con los inputs de texto no cambia)
            rx.grid(
                 # ... (tus inputs)
                 grid_column="span 2",
            ),
            
            rx.box(height="1em"),
            rx.text("Opcional: Para mayor precisión...", size="2", color_scheme="gray", text_align="center", width="100%"),

            # --- ✨ 3. CREAMOS EL BOTÓN CON UNA CADENA DE EVENTOS ✨ ---
            rx.button(
                rx.icon(tag="map-pin", margin_right="0.5em"),
                "Añadir mi ubicación con mapa",
                on_click=[
                    # Evento 1: Crea la función de callback de ÉXITO en la ventana global.
                    # El f-string permite que Reflex convierta el EventHandler en una función JS.
                    rx.call_script(f"window.onLocationSuccess = (lat, lon) => {{ {AppState.set_location_coordinates}(lat, lon) }}"),
                    
                    # Evento 2: Crea la función de callback de ERROR.
                    rx.call_script("window.onLocationError = () => { alert('No se pudo obtener la ubicación. Por favor, asegúrese de haber concedido los permisos.') }"),
                    
                    # Evento 3: AHORA SÍ, llama a la función principal.
                    rx.call_script("getLocation()"),
                ],
                variant="outline",
                width="100%",
            ),
            # --- ✨ FIN DE LA LÓGICA ✨ ---

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

# ... (El resto del archivo, como address_card y shipping_info_content, no necesita cambios)
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
                    href=f"https://www.google.com/maps?q={address.latitude},{address.longitude}",
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
                ~AppState.show_form,
                rx.button("Crear Nueva Dirección", on_click=AppState.toggle_form, margin_top="2em"),
            ),
            rx.cond(AppState.show_form, address_form()),
            align_items="start", width="100%", max_width="700px"
        )
    )