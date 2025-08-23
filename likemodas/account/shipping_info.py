# likemodas/account/shipping_info.py (VERSIÓN FINAL)

import reflex as rx
import reflex_local_auth
from ..state import AppState
from ..account.layout import account_layout
from ..models import ShippingAddressModel
from ..ui.components import searchable_select
# ELIMINA la siguiente línea, ya no existe:
# from ..ui.location_button import location_button

def address_form() -> rx.Component:
    """Formulario para crear una nueva dirección."""
    return rx.form(
        rx.vstack(
            rx.heading("Nueva Dirección de Envío", size="6", width="100%"),
            # ... (el rx.grid con los inputs de texto no cambia)
            
            rx.box(height="1em"),
            rx.text(
                "Opcional: Para mayor precisión en la entrega, añade tu ubicación exacta.", 
                size="2", 
                color_scheme="gray",
                text_align="center",
                width="100%"
            ),

            # --- ✨ INICIO DEL CAMBIO FINAL ✨ ---
            # Reemplazamos el componente `location_button` por un `rx.button` normal.
            rx.button(
                rx.icon(tag="map-pin", margin_right="0.5em"),
                "Añadir mi ubicación con mapa",
                # El on_click ahora llama a nuestro nuevo handler en AppState.
                on_click=AppState.request_location_script,
                variant="outline",
                width="100%",
            ),
            # --- ✨ FIN DEL CAMBIO FINAL ✨ ---

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
                        rx.icon(tag="check-check", size=14), # <-- ✨ SOLUCIÓN FINAL ✨
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