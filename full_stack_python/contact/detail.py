import reflex as rx 

from ..ui.base import base_page

from . import state
from .notfound import contact_post_not_found
# @rx.page(route="/about")
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
        rx.text("User info id", state.ContactPostState.post.userinfo_id),
        rx.text("User info: ", state.ContactPostState.post.userinfo.to_string()),
        rx.text("User: ", state.ContactPostState.post.userinfo.user.to_string()),
        rx.text(state.ContactPostState.post.publish_date),
        rx.text(
            state.ContactPostState.post.content,
            white_space='pre-wrap'
        ),
        spacing="5",
        align="center",
        min_height="85vh",
    ),
    contact_post_not_found()
    )
    return base_page(my_child)
