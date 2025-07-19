import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

# Cargar las variables de entorno del archivo .env
load_dotenv()

def send_verification_email(recipient_email: str, token: str):
    """Envía un correo de verificación al usuario."""
    
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    EMAIL_HOST = os.getenv("EMAIL_HOST")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
    APP_BASE_URL = os.getenv("APP_BASE_URL")

    if not all([EMAIL_USER, EMAIL_PASSWORD, EMAIL_HOST, APP_BASE_URL]):
        print("Error: Faltan variables de entorno para el envío de correo.")
        return

    # Construir el enlace de verificación
    verification_link = f"{APP_BASE_URL}/verify-email?token={token}"

    # Crear el mensaje del correo
    msg = EmailMessage()
    msg['Subject'] = "Verifica tu cuenta en Likemodas"
    msg['From'] = EMAIL_USER
    msg['To'] = recipient_email

    # Contenido del correo en HTML
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
            <p style="margin-top: 20px;">Si no puedes hacer clic en el botón, copia y pega el siguiente enlace en tu navegador:</p>
            <p><a href="{verification_link}">{verification_link}</a></p>
            <p style="font-size: 12px; color: #888;">Si no te registraste, por favor ignora este correo.</p>
        </div>
    </body>
    </html>
    """
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(html_content)

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print(f"Correo de verificación enviado a {recipient_email}")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")