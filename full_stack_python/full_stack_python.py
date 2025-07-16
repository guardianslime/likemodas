import reflex as rx
import reflex_local_auth

# Importaciones de estados
from full_stack_python.auth.state import SessionState
from full_stack_python.blog.state import BlogPublicState, BlogPostState, BlogViewState
from full_stack_python.contact.state import ContactState
from full_stack_python.articles.detail import ArticleDetailState

# Importaciones de páginas
from full_stack_python import pages, navigation, contact, blog
from full_stack_python.auth.pages import my_login_page, my_register_page, my_logout_page
from full_stack_python.articles.list import articles_gallery_page
from full_stack_python.articles.detail import article_detail_page

def index() -> rx.Component:
    return pages.base_page(
        rx.cond(
            SessionState.is_authenticated,
            pages.dashboard_component(),
            pages.landing_component(),
        )
    )

app = rx.App(
    theme=rx.theme(
        appearance="dark", has_background=True, panel_background="solid",
        scaling="90%", radius="medium", accent_color="sky"
    ),
)

# --- Registro de Páginas ---
app.add_page(index)
app.add_page(my_login_page, route=reflex_local_auth.routes.LOGIN_ROUTE)
app.add_page(my_register_page, route=reflex_local_auth.routes.REGISTER_ROUTE)
app.add_page(my_logout_page, route=navigation.routes.LOGOUT_ROUTE)
app.add_page(pages.about_page, route=navigation.routes.ABOUT_US_ROUTE)
app.add_page(pages.protected_page, route="/protected/", on_load=SessionState.on_load)
app.add_page(pages.pricing_page, route=navigation.routes.PRICING_ROUTE)

# --- RUTAS DE ARTICLES CORREGIDAS ---
app.add_page(
    articles_gallery_page,
    route=navigation.routes.ARTICLE_LIST_ROUTE,
    on_load=BlogPublicState.on_load,
)
app.add_page(
    article_detail_page,
    route=f"{navigation.routes.ARTICLE_LIST_ROUTE}/[article_id]",
    on_load=ArticleDetailState.on_load,
)

# --- Rutas de Blog ---
app.add_page(
    blog.blog_post_list_page,
    route=navigation.routes.BLOG_POSTS_ROUTE,
    on_load=BlogPostState.load_posts
)
app.add_page(blog.blog_post_add_page, route=navigation.routes.BLOG_POST_ADD_ROUTE)
app.add_page(
    blog.blog_post_edit_page,
    route="/blog/[blog_id]/edit",
    on_load=BlogPostState.get_post_detail 
)
app.add_page(
    blog.blog_public_page,
    route=navigation.routes.BLOG_PUBLIC_PAGE_ROUTE,
    title="Galería pública",
    on_load=BlogPublicState.on_load
)
app.add_page(
    blog.blog_public_detail_page,
    route=f"{navigation.routes.BLOG_PUBLIC_DETAIL_ROUTE}/[blog_public_id]",
    title="Detalle de la Publicación",
    on_load=BlogViewState.on_load
)

# --- Páginas de Contacto ---
app.add_page(contact.contact_page, route=navigation.routes.CONTACT_US_ROUTE)
app.add_page(
    contact.contact_entries_list_page,
    route=navigation.routes.CONTACT_ENTRIES_ROUTE,
    on_load=ContactState.load_entries
)