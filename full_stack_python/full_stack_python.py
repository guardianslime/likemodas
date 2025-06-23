"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
import sqlalchemy
import reflex_local_auth
from reflex_local_auth.user import LocalUser 

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
@app.api.get("/db_healthz")
def db_healthz():
    try:
        print("--- [db_healthz] Iniciando prueba de conexión a la BD. ---")
        with rx.session() as session:
            print("--- [db_healthz] Sesión de BD creada. Ejecutando consulta simple. ---")
            # Hacemos una consulta muy simple que no debería fallar
            session.exec(sqlalchemy.select(LocalUser).limit(1)).first()
            print("--- [db_healthz] Consulta exitosa. La conexión a la BD funciona. ---")
        return {"status": "OK", "message": "Database connection successful."}
    except Exception as e:
        # ¡Si hay un error, lo capturamos y lo mostramos!
        print(f"!!!!!!!!!! [db_healthz] ERROR DE BASE DE DATOS: {e} !!!!!!!!!!!")
        return {"status": "ERROR", "detail": str(e)}, 500


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

