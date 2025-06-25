# full_stack_python/full_stack_python.py

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


def index() -> rx.Component:
     return base_page(
          rx.cond(SessionState.is_authenticated,   
               pages.dashboard_component(),
               pages.landing_component(),          
          )          
     )

app = rx.App(
     theme=rx.theme(
          appearance="dark", 
          has_background=True, 
          panel_background="solid",
          scaling= "90%",
          radius="medium",
          accent_color="sky"
     )
)

# Añadimos la ruta /healthz directamente a la API de FastAPI.
@app.api.get("/healthz")
def healthz():
    return {"status": "OK"}


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
     route="/blog/edit/[blog_id]",
     on_load=blog.BlogPostState.get_post_detail
)

app.add_page(
    contact.contact_page,
    route=navigation.routes.CONTACT_US_ROUTE,
    # --- ARREGLO 1 ---
    # Se añade el on_load aquí para asegurar que la sesión del usuario esté cargada
    on_load=contact.state.ContactState.hydrate_session
)

app.add_page(
    contact.contact_entries_list_page,
    route=navigation.routes.CONTACT_ENTRIES_ROUTE,
    # --- ARREGLO 2 ---
    # Se añade la cadena de on_load correcta: primero carga la sesión, luego lista las entradas
    on_load=[contact.state.ContactState.hydrate_session, contact.state.ContactState.list_entries]
)