import reflex as rx 

from ..ui.base import base_page

from . import state

# @rx.page(route="/about")
def blog_post_detail_page() -> rx.Component:
    con_edit = True
    edit_link = rx.link("Edit", href=f"/blog"(state.
    BlogPostState.blog_post_id)'/edit')
    edit_link_el = rx.cond(
        con_edit,
        edit_link,
    )
    my_child = rx.vstack(
            rx.heading(state.BlogPostState.post.title, size="9"),
            edit_link_el,
            rx.text(
                state.BlogPostState.post.content,
            ),
            spacing="5",
            align="center",
            min_height="85vh",
        )
    return base_page(my_child)