# cookies_page.py

import reflex as rx
from ...ui.base import base_page

# Pega el texto correspondiente de los Términos y Condiciones aquí
markdown_text = """
# Política de Cookies de LIKEMODAS

**Fecha de última actualización:** [17 de octubre de 2025]

Este sitio web, www.likemodas.com ("Plataforma"), utiliza cookies para mejorar tu experiencia de usuario.

### 1. ¿Qué son las Cookies?
Una cookie es un pequeño archivo de texto que un sitio web guarda en tu ordenador o dispositivo móvil cuando lo visitas.

### 2. ¿Qué Cookies Utilizamos?
En LIKEMODAS, utilizamos únicamente cookies **esenciales y técnicas**. Estas cookies son estrictamente necesarias para el funcionamiento de la Plataforma y no se pueden desactivar en nuestros sistemas. Incluyen:

* **Cookies de Sesión (`session_id`):** Esta cookie es fundamental para identificarte una vez que has iniciado sesión. Nos permite saber quién eres mientras navegas por las diferentes páginas, manteniendo tu cuenta segura y activa. Sin esta cookie, tendrías que iniciar sesión en cada página.
* **Cookies de Funcionalidad del Carrito:** Utilizamos el almacenamiento local de tu navegador (una tecnología similar a las cookies) para guardar los productos que añades a tu carrito de compras. Esto asegura que tus productos no se pierdan si cierras la pestaña y vuelves más tarde.

No utilizamos cookies de marketing, publicidad o análisis de terceros.

### 3. Cómo Gestionar las Cookies
Aunque no puedes desactivar nuestras cookies esenciales sin afectar el funcionamiento del sitio, puedes configurar tu navegador para que las bloquee o te avise sobre ellas. Consulta la sección de ayuda de tu navegador para saber cómo hacerlo. Ten en cuenta que si bloqueas estas cookies, partes del sitio como el inicio de sesión o el carrito de compras no funcionarán.

### 4. Contacto
Si tienes preguntas sobre nuestra Política de Cookies, contáctanos en: soporte@likemodas.com.
"""


# --- ✨ CORRECCIÓN AQUÍ: Renombra la función ✨ ---
def cookies_page() -> rx.Component:
    page_content = rx.box(
        rx.markdown(markdown_text),
        max_width="800px",
        margin="auto",
        padding_y="2em",
    )
    return base_page(page_content)