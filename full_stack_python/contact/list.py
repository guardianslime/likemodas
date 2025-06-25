import reflex as rx 
import reflex_local_auth
from .. import navigation
from ..ui.base import base_page
from ..models import ContactEntryModel
from . import state

def contact_entry_detail_link(child: rx.Component, entry: ContactEntryModel):
    if entry is None:
        return rx.fragment(child)
    entry_id = entry.id
    if entry_id is None:
        return rx.fragment(child)
    
    # El router usará la ruta dinámica /contact/[contact_id]
    entry_detail_url = f"/contact/{entry_id}"
    return rx.link(
        child,
        rx.heading("by ", entry.userinfo.email),
        href=entry_detail_url
    )

def contact_entry_list_item(entry: ContactEntryModel):
    return rx.box(
        contact_entry_detail_link(    
            rx.heading(entry.title),
            entry
        ),
        padding="1em"
    )

@reflex_local_auth.require_login
def contact_entry_list_page() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.heading("Contact Entrys", size="5"),
            rx.link(
                rx.button("New Entry"),
                # CORRECCIÓN: El enlace ahora apunta a la ruta correcta.
                href=navigation.routes.CONTACT_POST_ADD_ROUTE
            ),
            rx.foreach(state.ContactEntryState.entrys, contact_entry_list_item)
        )
    )
