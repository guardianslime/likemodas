import reflex as rx 
import reflex_local_auth
from .. import navigation
from ..ui.base import base_page
from ..models import ContactPostModel
from . import state

def contact_post_detail_link(child: rx.Component, post: ContactPostModel):
    if post is None:
        return rx.fragment(child)
    post_id = post.id
    if post_id is None:
        return rx.fragment(child)
    root_path = navigation.routes.CONTACT_POSTS_ROUTE
    post_detail_url = f"{root_path}/{post_id}"
    return rx.link(
        child,
        rx.heading("by ", post.userinfo.email),
        href=post_detail_url
    )

def contact_post_list_item(post: ContactPostModel):
    return rx.box(
        contact_post_detail_link(    
            rx.heading(post.title),
            post
        ),
        padding="1em"
    )

# def foreach_callback(text):
#     return rx.box(rx.text(text))

@reflex_local_auth.require_login
def contact_post_list_page() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.heading("Contact Posts", size="5"),
            rx.link(
                rx.button("New Post"),
                href=navigation.routes.CONTACT_POST_ADD_ROUTE
            ),
            # rx.foreach(["abc", "abc", "cde"], foreach_callback),
            rx.foreach(state.ContactPostState.posts, contact_post_list_item),
            spacing="5",
            align="center",
            min_height="85vh",
        )
    )