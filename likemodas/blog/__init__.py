# likemodas/blog/__init__.py (CORREGIDO)

# Importa cada función desde su archivo de origen correcto
from .add import blog_post_add_content
from .detail import blog_post_detail_content
from .list import blog_post_list_content
from .public_page import blog_public_page_content
from .detail import blog_post_detail_content
from .admin_page import blog_admin_page

# __all__ le dice a Python qué funciones están disponibles desde el paquete 'blog'
__all__ = [
    'blog_post_add_content',
    'blog_post_detail_content',
    'blog_post_list_content',
    'blog_public_page_content',
    'blog_post_detail_content',
    'blog_admin_page',
]