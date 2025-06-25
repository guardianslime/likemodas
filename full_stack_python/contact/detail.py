import reflex as rx 

from ..ui.base import base_page

from . import state
from .notfound import contact_post_not_found

def contact_post_detail_page() -> rx.Component:
    con_edit = True
    edit_link = rx.link("Edit", href=f"{state.ContactPostState.contact_post_edit_url}")
    edit_link_el = rx.cond(
        con_edit,
        edit_link,
    )
    my_child = rx.cond(state.ContactPostState.post, rx.vstack(
        rx.hstack(
            rx.heading(state.ContactPostState.post.title, size="9"),
            edit_link_el,
            align='end'
        ),
        # --- CORRECCIÓN ---
        # Se muestran atributos específicos como .email y .username
        # en lugar de usar el método inexistente .to_string()
        rx.text("Author Email: ", state.ContactPostState.post.userinfo.email),
        rx.text("Author Username: ", state.ContactPostState.post.userinfo.user.username),
        rx.text("Published on: ", state.ContactPostState.post.publish_date),
        rx.box(
            rx.text(
                state.ContactPostState.post.content,
                white_space='pre-wrap'
            ),
            border="1px solid #ddd",
            padding="1em",
            border_radius="8px",
            margin_top="1em",
            width="100%"
        ),
        spacing="5",
        align="center",
        min_height="85vh",
    ),
    contact_post_not_found()
    )
    return base_page(my_child)
