# privacy_page.py

import reflex as rx
from ...ui.base import base_page

# Pega el texto correspondiente de los Términos y Condiciones aquí
markdown_text = """
# Política de Privacidad de LIKEMODAS

**Fecha de última actualización:** [17 de octubre de 2025]

En LIKEMODAS, valoramos tu privacidad y nos comprometemos a proteger tus datos personales. Esta política explica qué información recopilamos y cómo la utilizamos.

### 1. Información que Recopilamos
Recopilamos los siguientes tipos de datos:
* **Datos de Registro:** Nombre de usuario, correo electrónico y contraseña (cifrada).
* **Datos de Perfil:** Número de teléfono e imagen de perfil (avatar), si decides proporcionarlos.
* **Datos de Envío:** Nombre completo, teléfono, ciudad, barrio y dirección postal para la entrega de tus compras.
* **Datos de Transacciones:** Historial de compras, productos comprados, montos, método de pago seleccionado e identificadores de transacción de nuestras pasarelas de pago (Wompi, Sistecredito). No almacenamos números de tarjetas de crédito/débito.
* **Datos de Uso:** Productos que guardas en tu lista de favoritos y comentarios que publicas.
* **Datos Técnicos:** Información de sesión para mantener tu cuenta activa y segura.

### 2. Cómo Usamos tu Información
Utilizamos tus datos para los siguientes propósitos:
* **Procesar tus Pedidos:** Para gestionar tus compras, coordinar envíos y procesar pagos.
* **Comunicación:** Para enviarte notificaciones sobre el estado de tus pedidos, respuestas de soporte y confirmaciones de cuenta.
* **Seguridad:** Para verificar tu identidad, proteger tu cuenta (incluida la Autenticación de Dos Factores) y prevenir fraudes.
* **Soporte al Cliente:** Para gestionar tus solicitudes de devolución, cambio o contacto.
* **Personalización:** Para mostrarte productos guardados y mantener la funcionalidad de tu carrito de compras.

### 3. Cómo Compartimos tu Información
No vendemos ni alquilamos tus datos personales. Compartimos información únicamente en los siguientes casos:
* **Vendedores:** Compartimos tus datos de envío con el Vendedor correspondiente para que pueda despachar tu pedido.
* **Pasarelas de Pago:** Compartimos los datos necesarios de la transacción con Wompi y Sistecredito para procesar tu pago de forma segura.
* **Obligaciones Legales:** Si es requerido por una autoridad competente bajo la ley colombiana.

### 4. Seguridad de los Datos
Tomamos medidas de seguridad para proteger tu información, incluyendo:
* **Cifrado de Contraseñas:** Las contraseñas se almacenan de forma cifrada (hashed).
* **Cifrado de Secretos 2FA:** La clave para tu autenticación de dos factores se almacena de forma cifrada.
* **Acceso Limitado:** Solo el personal autorizado (como Administradores) tiene acceso a la información para fines de gestión y soporte.

### 5. Retención de Datos y Tus Derechos (Habeas Data)
De acuerdo con la Ley 1581 de 2012 de Colombia, tienes derecho a:
* **Acceder, Conocer y Actualizar:** Puedes ver y editar la información de tu perfil y direcciones de envío en cualquier momento desde la sección "Mi Cuenta".
* **Rectificar:** Puedes corregir información personal que sea incorrecta.
* **Supresión (Cancelación):** Puedes solicitar la eliminación de tu cuenta. Al hacerlo, tus datos personales identificables (nombre de usuario, email, teléfono, direcciones) serán eliminados o anonimizados. Sin embargo, para mantener la integridad del historial de transacciones y comentarios, los registros de compras y las opiniones se conservarán de forma anónima ("Usuario Eliminado").

### 6. Política de Cookies
Utilizamos cookies técnicas y esenciales para el funcionamiento de la Plataforma, como mantener tu sesión iniciada y recordar los productos en tu carrito. Para más detalles, consulta nuestra **Política de Cookies**.

### 7. Contacto
Si tienes preguntas sobre esta política, contáctanos en: soporte@likemodas.com.
"""


# --- ✨ CORRECCIÓN AQUÍ: Renombra la función ✨ ---
def privacy_page() -> rx.Component:
    page_content = rx.box(
        rx.markdown(markdown_text),
        max_width="800px",
        margin="auto",
        padding_y="2em",
    )
    return base_page(page_content)