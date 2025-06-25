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
    
    # El router usará la ruta dinámica /contact/[contact_id]
    post_detail_url = f"/contact/{post_id}"
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

@reflex_local_auth.require_login
def contact_post_list_page() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.heading("Contact Posts", size="5"),
            rx.link(
                rx.button("New Post"),
                # CORRECCIÓN: El enlace ahora apunta a la ruta correcta.
                href=navigation.routes.CONTACT_POST_ADD_ROUTE
            ),
            rx.foreach(state.ContactPostState.posts, contact_post_list_item)
        )
    )
