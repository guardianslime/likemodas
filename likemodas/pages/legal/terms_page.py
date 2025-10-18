# terms_page.py

import reflex as rx
from ...ui.base import base_page

# Pega el texto correspondiente de los Términos y Condiciones aquí
markdown_text = """
# Términos y Condiciones de LIKEMODAS

**Fecha de última actualización:** [17 de octubre de 2025]

Bienvenido a LIKEMODAS. Estos Términos y Condiciones ("Términos") rigen el uso de nuestro sitio web, www.likemodas.com ("Plataforma"), y los servicios ofrecidos. Al registrarte o utilizar nuestra Plataforma, aceptas cumplir con estos Términos.

### 1. Definiciones
* **Plataforma:** El sitio web de e-commerce LIKEMODAS.
* **Usuario:** Cualquier persona que se registra en la Plataforma. Incluye Compradores, Vendedores y Empleados.
* **Comprador:** Un Usuario que realiza compras de productos en la Plataforma.
* **Vendedor:** Un Usuario autorizado para listar, gestionar y vender productos a través de la Plataforma.
* **Empleado:** Un Usuario vinculado a un Vendedor para gestionar sus productos y ventas en su nombre.

### 2. Cuentas de Usuario
* **Registro:** Para acceder a la mayoría de las funcionalidades, debes crear una cuenta proporcionando un nombre de usuario, un correo electrónico válido (@gmail.com) y una contraseña. Eres responsable de mantener la confidencialidad de tu contraseña.
* **Veracidad:** Te comprometes a proporcionar información veraz y actualizada.
* **Seguridad:** Ofrecemos Autenticación de Dos Factores (2FA) como una capa de seguridad adicional, la cual recomendamos activar.
* **Terminación:** Nos reservamos el derecho de suspender o eliminar cuentas (`vetar`) que violen estos Términos, participen en actividades fraudulentas o infrinjan la ley.

### 3. Proceso de Compra
* **Precios y Pagos:** Los precios de los productos son establecidos por los Vendedores y se muestran en Pesos Colombianos (COP). El precio puede o no incluir el IVA, lo cual se especifica en la publicación del producto.
* **Métodos de Pago:** Aceptamos pagos a través de nuestras pasarelas aliadas (Wompi, Sistecredito) y pago Contra Entrega. Al usar pasarelas de pago de terceros, también estás sujeto a sus términos y condiciones.
* **Pago Contra Entrega:** Este servicio solo está disponible si la ciudad de origen de **todos los productos** en tu carrito coincide con la ciudad de tu dirección de envío. De lo contrario, esta opción no será viable para la finalización de la compra.

### 4. Envíos
* **Costo de Envío:** El costo se calcula dinámicamente basado en la ubicación de origen del Vendedor y la dirección de envío del Comprador. El costo base se muestra en la página del producto y el costo final se calcula en el carrito.
* **Envío Combinado:** Algunos productos permiten ser agrupados en un solo envío, sujeto a un límite de artículos por paquete, definido por el Vendedor.
* **Moda Completa (Envío Gratis):** Los Vendedores pueden ofrecer envío gratuito para compras que superen un determinado valor en productos marcados como "Moda Completa". El umbral es definido por cada Vendedor.
* **Tiempos de Entrega:** Los tiempos de entrega son estimados y comunicados por el Vendedor una vez que el pedido es despachado.

### 5. Política de Devoluciones y Cambios
* **Solicitudes:** Si deseas solicitar una devolución o cambio por un producto defectuoso, incorrecto o que no cumple con las características, debes iniciar una solicitud a través de la sección "Mis Compras" en tu perfil.
* **Proceso:** Se abrirá un ticket de soporte para que te comuniques directamente con el Vendedor y gestionen el caso.
* **Costos de Devolución:** En caso de devolución del pedido, el costo del envío para el retorno del producto deberá ser cubierto por el Comprador.

### 6. Roles de Vendedor y Empleado
* **Responsabilidad del Vendedor:** Cada Vendedor es el único responsable de la calidad, autenticidad, gestión de inventario y envío de sus productos. LIKEMODAS actúa como un intermediario tecnológico.
* **Gestión de Empleados:** Un Vendedor puede autorizar a otros Usuarios (Empleados) para que gestionen su inventario y ventas. El Vendedor es responsable final de todas las acciones realizadas por sus Empleados en la Plataforma.

### 7. Contenido Generado por el Usuario
* **Opiniones y Calificaciones:** Al dejar un comentario o calificación sobre un producto, otorgas a LIKEMODAS una licencia no exclusiva y global para usar, mostrar y distribuir dicho contenido en la Plataforma.
* **Conducta:** No se permite contenido ofensivo, fraudulento, o que infrinja los derechos de autor. Nos reservamos el derecho de moderar o eliminar cualquier contenido que viole estas normas.

### 8. Legislación Aplicable
Estos Términos se regirán e interpretarán de acuerdo con las leyes de la República de Colombia.

### 9. Contacto
Para cualquier pregunta sobre estos Términos, puedes contactarnos a través de: soporte@likemodas.com.
"""


def terms_page() -> rx.Component:
    # 2. Crea el contenido de la página en una variable.
    page_content = rx.box(
        rx.markdown(markdown_text),
        max_width="800px",
        margin="auto",
        padding_y="2em",
    )
    
    # 3. Devuelve el contenido envuelto en la función base_page().
    return base_page(page_content)