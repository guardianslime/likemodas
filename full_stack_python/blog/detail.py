import reflex as rx 

from ..ui.base import base_page

from . import state

# @rx.page(route="/about")
def blog_post_detail_page() -> rx.Component:
    con_edit = True
    edit_link = rx.link("Edit", href=f"/{state.
    BlogPostState.blog_post_edit_url}")
    edit_link_el = rx.cond(
        con_edit,
        edit_link,
    )
    my_child = rx.vstack(
        rx.hstack(
            rx.heading(state.BlogPostState.post.title, size="9"),
            edit_link_el,
            align='end'
        ),
        rx.text("User info id", state.BlogPostState.post.userinfo_id),
        rx.text(state.BlogPostState.post.publish_date),
        rx.text(
            state.BlogPostState.post.content,
            white_space='pre-wrap'
        ),
        spacing="5",
        align="center",
        min_height="85vh",
    )
    return base_page(my_child)