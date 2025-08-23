# likemodas/account/shipping_info.py (VERSIÓN FINAL)

import reflex as rx
import reflex_local_auth
from ..state import AppState
from ..account.layout import account_layout
from ..models import ShippingAddressModel
from ..ui.components import searchable_select
from ..ui.location_button import location_button  # <-- ✨ 1. IMPORTA EL NUEVO COMPONENTE

# Ya no necesitas la variable 'get_location_script', puedes borrarla.

def address_form() -> rx.Component:
    """Formulario para crear una nueva dirección."""
    return rx.form(
        rx.vstack(
            rx.heading("Nueva Dirección de Envío", size="6", width="100%"),
            # ... (tu rx.grid con los inputs no cambia)
            rx.grid(
                 # ...
                 grid_column="span 2",
            ),
            
            rx.box(height="1em"),
            rx.text(
                "Opcional: Para mayor precisión en la entrega, añade tu ubicación exacta.", 
                size="2", 
                color_scheme="gray",
                text_align="center",
                width="100%"
            ),

            # --- ✨ 2. REEMPLAZA EL ANTIGUO BOTÓN POR EL NUEVO COMPONENTE ✨ ---
            location_button(
                # Conectamos los event handlers del componente a los de AppState.
                on_location_success=AppState.set_location_coordinates,
                on_location_error=AppState.on_location_error,
            ),
            # --- ✨ FIN DEL REEMPLAZO ✨ ---

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