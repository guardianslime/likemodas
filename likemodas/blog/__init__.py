# likemodas/blog/__init__.py (CORREGIDO SEGÚN TU CAPTURA DE PANTALLA)

# Asumiendo que las funciones de admin (list, detail, edit) están en admin_page.py
from .admin_page import blog_post_list_content, blog_post_detail_content, blog_post_edit_content
from .add import blog_post_add_content
from .public_page import blog_public_page_content
from .detail import blog_public_detail_content

# La lista __all__ exporta los nombres para que puedan ser importados desde "likemodas.blog"
__all__ = [
    'blog_post_list_content',
    'blog_post_detail_content',
    'blog_post_edit_content',
    'blog_post_add_content',
    'blog_public_page_content',
    'blog_public_detail_content',
]