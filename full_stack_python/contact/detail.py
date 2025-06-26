import reflex as rx 

from ..ui.base import base_page

from . import state
from .notfound import contact_entry_not_found
# @rx.page(route="/about")
def contact_entry_detail_page() -> rx.Component:
    con_edit = True
    edit_link = rx.link("Edit", href=f"{state.ContactEntryState.contact_entry_edit_url}")
    edit_link_el = rx.cond(
        con_edit,
        edit_link,
    )
    my_child = rx.cond(state.ContactEntryState.entry, rx.vstack(
        rx.hstack(
            rx.heading(state.ContactEntryState.entry.title, size="9"),
            edit_link_el,
            align='end'
        ),
        rx.text("User info id", state.ContactEntryState.entry.userinfo_id),
        rx.text("User info: ", state.ContactEntryState.entry.userinfo.to_string()),
        rx.text("User: ", state.ContactEntryState.entry.userinfo.user.to_string()),
        rx.text(state.ContactEntryState.entry.publish_date),
        rx.text(
            state.ContactEntryState.entry.content,
            white_space='pre-wrap'
        ),
        spacing="5",
        align="center",
        min_height="85vh",
    ),
    contact_entry_not_found()
    )
    return base_page(my_child)
