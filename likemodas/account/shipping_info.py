# likemodas/account/shipping_info.py (CORREGIDO CON ALTERNATIVA GRATUITA)

import reflex as rx
import reflex_local_auth
from ..state import AppState
from ..account.layout import account_layout
from ..models import ShippingAddressModel
from ..ui.components import searchable_select
from .. import navigation # Asegúrate de que esta importación exista

def address_form() -> rx.Component:
    """Formulario para crear una nueva dirección, con campos para coordenadas manuales."""
    return rx.form(
        rx.vstack(
            rx.heading("Nueva Dirección de Envío", size="6", width="100%"),
            
            # --- SECCIÓN PARA OBTENER COORDENADAS (ALTERNATIVA GRATUITA) ---
            rx.box(
                rx.vstack(
                    rx.text("Para mayor precisión en el envío (opcional):", size="3", weight="medium"),
                    rx.link(
                        rx.button(
                            "1. Abrir mapa y copiar coordenadas", 
                            rx.icon("map", margin_left="0.5em"), 
                            width="100%",
                            variant="outline",
                            color_scheme="gray",
                        ),
                        href="/map-selector",
                        is_external=True, # Abre el mapa en una nueva pestaña
                    ),
                    rx.hstack(
                        rx.input(
                            placeholder="2. Pega la Latitud aquí", 
                            value=AppState.manual_latitude,
                            on_change=AppState.set_manual_latitude,
                        ),
                        rx.input(
                            placeholder="3. Pega la Longitud aquí",
                            value=AppState.manual_longitude,
                            on_change=AppState.set_manual_longitude,
                        ),
                        width="100%",
                        spacing="3",
                    ),
                    spacing="2",
                    width="100%",
                ),
                width="100%",
                border="1px solid",
                border_color=rx.color("gray", 6),
                padding="1em",
                border_radius="md",
                margin_y="1em",
            ),
            
            # --- RESTO DEL FORMULARIO DE DIRECCIÓN ---
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
                        is_disabled=~AppState.neighborhoods,
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
                # --- AÑADE UN BADGE SI LA UBICACIÓN ESTÁ GUARDADA ---
                rx.cond(
                    address.latitude,
                    rx.badge(
                        rx.hstack(rx.icon("map-pin", size=12), rx.text("Ubicación Guardada")),
                        color_scheme="blue", variant="soft"
                    ),
                ),
                rx.cond(address.is_default, rx.badge("Predeterminada", color_scheme="green")),
                width="100%", spacing="2"
            ),
            rx.text(f"{address.address}, {address.neighborhood}"),
            rx.text(f"{address.city}"),
            rx.text(f"Tel: {address.phone}"),
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
        border="1px solid", 
        border_color=rx.color("gray", 6), 
        border_radius="md", 
        padding="1em", 
        width="100%"
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
