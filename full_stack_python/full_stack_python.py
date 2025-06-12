"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
import reflex_local_auth

from rxconfig import config
from .ui.base import base_page

from .auth.pages import(
     my_login_page,
     my_register_page,
     my_logout_page
)
from .auth.state import SessionState


from .articles.detail import article_detail_page
from .articles.list import article_public_list_page, article_public_list_component
from .articles.state import ArticlePublicState

from . import blog, contact, navigation, pages

class State(rx.State):

    label = "Welcome to Reflex"

    def handle_title_input_change(self, val):
         self.label = val

    def did_click(self):
        print("hello world did click")
        return rx.redirect(navigation.routes.ABOUT_US_ROUTE)

def index() -> rx.Component:
     # my_user_obj = SessionState.authenticated_user_info
     my_child = rx.vstack(
          rx.heading("Welcome to SaaS", size="9"),
          rx.link(
               rx.button("about us"),
               href=navigation.routes.ABOUT_US_ROUTE
          ),
          rx.divider(),
          rx.heading("Recent Articles", size="5"),
          article_public_list_component(columns=1, limit=1),
          spacing="5",
          justify="center",
          align="center",
          # text_align="center",
          min_height="85vh",
          id="my-child"
     )
     return base_page(my_child)



app = rx.App()
app.add_page(index,
          on_load=ArticlePublicState.load_posts
     )
# reflex_local_auth,pages
app.add_page(
     my_login_page,
     route=reflex_local_auth.routes.LOGIN_ROUTE,
     title="login",
)
app.add_page(
     my_register_page,
     route=reflex_local_auth.routes.REGISTER_ROUTE,
     title="Register",
)

app.add_page(
     my_logout_page,
     route=navigation.routes.LOGOUT_ROUTE,
     title="Logout"
)

#my pages
app.add_page(pages.about_page,
             route=navigation.routes.ABOUT_US_ROUTE)

app.add_page(
     pages.protected_page,
     route="/protected/",
     on_load=SessionState.on_load
)

app.add_page(
     article_public_list_page,
     route=navigation.routes.ARTICLE_LIST_ROUTE,
     on_load=ArticlePublicState.load_posts
)

app.add_page(
    article_detail_page,
    route=f"{navigation.routes.ARTICLE_LIST_ROUTE}/[article_id]",
    on_load=ArticlePublicState.get_post_detail
)

app.add_page(
    blog.blog_post_list_page,
    route=navigation.routes.BLOG_POSTS_ROUTE,
    on_load=blog.BlogPostState.load_posts

)

app.add_page(
     blog.blog_post_add_page,
     route=navigation.routes.BLOG_POST_ADD_ROUTE,
)

app.add_page(
     blog.blog_post_detail_page,
     route="/blog/[blog_id]",
     on_load=blog.BlogPostState.get_post_detail
)

app.add_page(
     blog.blog_post_edit_page,
     route="/blog/[blog_id]/edit",
     on_load=blog.BlogPostState.get_post_detail
)

app.add_page(contact.contact_page, route=navigation.routes.CONTACT_US_ROUTE)
app.add_page(
    contact.contact_entries_list_page,
    route=navigation.routes.CONTACT_ENTRIES_ROUTE,
    on_load=contact.ContactState.list_entries
)
app.add_page(pages.pricing_page, route=navigation.routes.PRICING_ROUTE)

