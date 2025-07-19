import os
import resend
from dotenv import load_dotenv

# Carga las variables de entorno (para desarrollo local)
load_dotenv()

# Configura Resend con la API Key
resend.api_key = os.getenv("RESEND_API_KEY")
APP_BASE_URL = os.getenv("APP_BASE_URL")

def send_verification_email(recipient_email: str, token: str):
    """Envía un correo de verificación al usuario usando Resend."""

    if not resend.api_key or not APP_BASE_URL:
        print("Error: Falta la variable de entorno RESEND_API_KEY o APP_BASE_URL.")
        return

    verification_link = f"{APP_BASE_URL}/verify-email?token={token}"

    # Este es el contenido HTML del correo. Puedes diseñarlo como quieras.
    html_content = f"""
    <html>
    <body>
        <div style="font-family: Arial, sans-serif; text-align: center; padding: 20px;">
            <h2>¡Bienvenido a Likemodas!</h2>
            <p>Gracias por registrarte. Por favor, haz clic en el siguiente botón para verificar tu dirección de correo electrónico.</p>
            <a href="{verification_link}" 
               style="background-color: #007bff; color: white; padding: 15px 25px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; font-size: 16px;">
               Verificar mi Correo
            </a>
            <p style="margin-top: 20px;">Si no te registraste, por favor ignora este correo.</p>
        </div>
    </body>
    </html>
    """

    try:
        params = {
            "from": "Verificación Likemodas <verify@mail.likemodas.com>", # Resend requiere este remitente en el plan gratuito
            "to": [recipient_email],
            "subject": "Verifica tu cuenta en Likemodas",
            "html": html_content,
        }
        email = resend.Emails.send(params)
        print(f"✅ Correo de verificación enviado a {recipient_email} vía Resend. ID: {email['id']}")
    except Exception as e:
        print(f"❌ ERROR al enviar el correo con Resend: {e}")