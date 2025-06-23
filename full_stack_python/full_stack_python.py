# -----------------------------------------------------------------
# full_stack_python/full_stack_python.py (Archivo Principal)
# -----------------------------------------------------------------
# ¡CORRECIÓN! Este archivo incluye la ruta de diagnóstico /db_healthz
# que es CRUCIAL para verificar la conexión a tu base de datos.
# -----------------------------------------------------------------

"""Punto de entrada principal de la aplicación Reflex."""

import reflex as rx
import sqlalchemy
import reflex_local_auth
from reflex_local_auth.user import LocalUser

from rxconfig import config
from .ui.base import base_page

from .auth.pages import (
    my_login_page,
    my_register_page,
    my_logout_page
)
from .auth.state import SessionState

from .articles.detail import article_detail_page
from .articles.list import article_public_list_page
from .articles.state import ArticlePublicState

from . import blog, contact, navigation, pages

def index() -> rx.Component:
    """Página de inicio que muestra el dashboard si está autenticado, o la landing page si no."""
    return base_page(
        rx.cond(
            SessionState.is_authenticated,
            pages.dashboard_component(),
            pages.landing_component(),
        )
    )

# Configuración principal de la aplicación Reflex
app = rx.App(
    theme=rx.theme(
        appearance="dark",
        has_background=True,
        panel_background="solid",
        scaling="90%",
        radius="medium",
        accent_color="sky"
    )
)

# --- RUTA DE DIAGNÓSTICO DE LA BASE DE DATOS ---
# ¡IMPORTANTE! Esta es tu herramienta más valiosa para depurar.
# Si la aplicación sigue fallando, visita https://<tu-url-de-railway>/db_healthz
# El mensaje de error que aparezca allí te dirá EXACTAMENTE qué está mal
# con tu variable de entorno DATABASE_URL.
@app.api.get("/db_healthz")
def db_healthz():
    """Verifica el estado de la conexión a la base de datos."""
    try:
        # Imprimimos en los logs para saber que se está ejecutando la prueba
        print("--- [db_healthz] Iniciando prueba de conexión a la BD. ---")
        with rx.session() as session:
            # Ejecutamos la consulta más simple posible, no depende de tus modelos.
            # Si esto falla, el problema es 100% la conexión.
            session.exec(sqlalchemy.text("SELECT 1"))
        # Si llegamos aquí, la conexión fue exitosa.
        print("--- [db_healthz] ¡Prueba de conexión a la BD EXITOSA! ---")
        return {"status": "OK", "message": "La conexión a la base de datos es exitosa."}
    except Exception as e:
        # Si algo falla, capturamos el error real y lo mostramos.
        # ESTE ES EL ERROR QUE NECESITAS VER.
        print(f"!!!!!!!!!! [db_healthz] PRUEBA DE CONEXIÓN FALLIDA: {e} !!!!!!!!!!!")
        return {"status": "ERROR", "detail": str(e)}, 500

# --- Definición de las páginas de la aplicación ---

app.add_page(index, on_load=ArticlePublicState.load_posts)

# Páginas de autenticación de reflex_local_auth
app.add_page(
    my_login_page,
    route=reflex_local_auth.routes.LOGIN_ROUTE,
    title="Login",
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

# Páginas personalizadas
app.add_page(pages.about_page, route=navigation.routes.ABOUT_US_ROUTE)

app.add_page(
    pages.protected_page,
    route="/protected/",
    on_load=SessionState.on_load  # ¡IMPORTANTE! Usa el on_load del SessionState corregido
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

```python
# -----------------------------------------------------------------
# full_stack_python/models.py (Modelos de Base de Datos)
# -----------------------------------------------------------------
# ¡CORRECIÓN! Se han arreglado las relaciones entre tablas y la
# nulidad de los campos, que eran una causa muy probable de los fallos.
# -----------------------------------------------------------------

from typing import Optional, List
from datetime import datetime
import reflex as rx
from reflex_local_auth.user import LocalUser

import sqlalchemy
from sqlmodel import Field, Relationship

from . import utils

class UserInfo(rx.Model, table=True):
    """Información extendida del usuario."""
    email: str
    user_id: int = Field(foreign_key='localuser.id')
    user: Optional[LocalUser] = Relationship() # Hacemos explícito que puede ser opcional
    
    posts: List['BlogPostModel'] = Relationship(back_populates='userinfo')
    contact_entries: List['ContactEntryModel'] = Relationship(back_populates='userinfo')
    
    created_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sqlalchemy.func.now()},
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"onupdate": sqlalchemy.func.now(), "server_default": sqlalchemy.func.now()},
        nullable=False
    )

class BlogPostModel(rx.Model, table=True):
    """Modelo para las publicaciones del blog."""
    # ¡CORRECIÓN! Se hace obligatorio que un post tenga un autor, eliminando `default=None`.
    # Un post sin autor no tiene sentido y podía causar errores.
    userinfo_id: int = Field(foreign_key="userinfo.id")
    # ¡CORRECIÓN! La relación con el autor ahora no es opcional, lo que es más coherente.
    userinfo: UserInfo = Relationship(back_populates="posts")
    
    title: str
    content: str
    
    created_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sqlalchemy.func.now()},
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"onupdate": sqlalchemy.func.now(), "server_default": sqlalchemy.func.now()},
        nullable=False
    )
    publish_active: bool = False
    publish_date: Optional[datetime] = Field( # Hacemos explícito que es Opcional
        default=None,
        sa_type=sqlalchemy.DateTime(timezone=True),
        nullable=True
    )

class ContactEntryModel(rx.Model, table=True):
    """Modelo para las entradas del formulario de contacto."""
    # ¡CORRECCIÓN! Se elimina el campo `user_id` que era redundante y podía causar conflictos.
    # La relación se maneja de forma única y clara a través de `userinfo_id`.
    
    # ¡CORRECIÓN! Se hace el tipo explícitamente Opcional para mayor claridad.
    # Un contacto puede ser de un usuario no registrado.
    userinfo_id: Optional[int] = Field(default=None, foreign_key="userinfo.id")
    userinfo: Optional['UserInfo'] = Relationship(back_populates="contact_entries")
    
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    message: str
    
    created_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sqlalchemy.func.now()},
        nullable=False
    )

```python
# -----------------------------------------------------------------
# full_stack_python/auth/state.py (Estado de Sesión)
# -----------------------------------------------------------------
# ¡CORRECIÓN! Se ha refactorizado completamente el SessionState para
# ser mucho más eficiente y estable. Ya no hace consultas a la base
# de datos en cada renderizado.
# -----------------------------------------------------------------

import reflex as rx
import reflex_local_auth
import sqlmodel

from ..models import UserInfo

class SessionState(reflex_local_auth.LocalAuthState):
    """
    Estado de la sesión del usuario.
    
    ¡CORRECCIÓN IMPORTANTE!
    El patrón correcto es cargar los datos de la base de datos UNA VEZ en un
    manejador de eventos (on_load) y guardarlos en una variable de estado normal.
    Las variables computadas (@rx.var) solo deben leer de otras variables de estado,
    NO hacer operaciones lentas como consultas a la BD.
    """
    
    # 1. Variable de estado para guardar la información del usuario una vez cargada.
    # NO es @rx.var, es una variable de estado simple.
    user_info: Optional[UserInfo] = None

    # 2. Variable computada que SIMPLEMENTE devuelve el estado. Es instantánea y segura.
    @rx.var
    def authenticated_user_info(self) -> Optional[UserInfo]:
        return self.user_info

    @rx.var
    def my_userinfo_id(self) -> Optional[int]:
        if self.user_info is None:
            return None
        return self.user_info.id

    @rx.var
    def my_user_id(self) -> Optional[int]:
        if self.authenticated_user.id < 0:
            return None
        return self.authenticated_user.id

    @rx.var
    def authenticated_username(self) -> Optional[str]:
        if self.authenticated_user.id < 0:
            return None
        return self.authenticated_user.username

    # 3. Evento on_load que carga los datos desde la BD de forma controlada.
    # Se ejecuta una vez al cargar una página protegida.
    def on_load(self):
        """
        Verifica la autenticación y carga los datos del usuario si es necesario.
        """
        if not self.is_authenticated:
            return reflex_local_auth.LoginState.redir
        
        # Solo consultamos la BD si no hemos cargado los datos previamente
        # y si el usuario está realmente autenticado (id >= 0).
        if self.user_info is None and self.authenticated_user.id >= 0:
            try:
                print(f"--- SessionState: Cargando UserInfo para user_id: {self.authenticated_user.id} ---")
                with rx.session() as session:
                    result = session.exec(
                        sqlmodel.select(UserInfo).where(
                            UserInfo.user_id == self.authenticated_user.id
                        )
                    ).one_or_none()
                    
                    # Guardamos el resultado (sea el usuario o None) en la variable de estado.
                    self.user_info = result
                    print(f"--- SessionState: Carga de UserInfo completada. Resultado: {'Encontrado' if result else 'No Encontrado'} ---")
            except Exception as e:
                print(f"!!!!!!!!!! SessionState: ERROR al cargar UserInfo: {e} !!!!!!!!!!!")

    def perform_logout(self):
        """Cierra la sesión del usuario y limpia el estado."""
        # Al hacer logout, limpiamos la información del usuario que teníamos guardada.
        self.user_info = None
        self.do_logout()
        return rx.redirect("/")

class MyRegisterState(reflex_local_auth.RegistrationState):
    """Estado para manejar el registro de un nuevo usuario."""

    def handle_registration_email(self, form_data: dict):
        """Maneja el registro y crea la entrada UserInfo asociada."""
        username = form_data.get("username")
        password = form_data.get("password")
        
        # Validación de campos
        validation_errors = self._validate_fields(
            username, password, form_data.get("confirm_password")
        )
        if validation_errors:
            return validation_errors
        
        # Registro del usuario base
        if not self._register_user(username, password):
            return # self.error_message ya está establecido por _register_user

        # Si el registro fue exitoso, creamos el UserInfo
        if self.new_user_id >= 0:
            try:
                with rx.session() as session:
                    session.add(
                        UserInfo(
                            email=form_data.get("email", ""),
                            user_id=self.new_user_id,
                        )
                    )
                    session.commit()
                return type(self).successful_registration
            except Exception as e:
                print(f"!!!!!!!!!! MyRegisterState: ERROR al crear UserInfo: {e} !!!!!!!!!!!")
                # Aquí podrías querer eliminar el LocalUser que acabas de crear para consistencia
                self.error_message = "No se pudo crear el perfil de usuario. Intente de nuevo."
                return

