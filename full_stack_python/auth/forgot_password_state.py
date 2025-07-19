import reflex as rx
import secrets
import sqlmodel  # ✨ 1. AÑADE ESTA IMPORTACIÓN
from datetime import datetime, timedelta
from ..models import UserInfo, PasswordResetToken
from ..services.email_service import send_password_reset_email

class ForgotPasswordState(rx.State):
    email: str = ""
    message: str = ""
    is_success: bool = False

    def handle_submit(self):
        if not self.email:
            self.message = "Por favor, introduce tu correo electrónico."
            self.is_success = False
            return

        with rx.session() as session:
            # ✨ 2. CORRIGE rx.select a sqlmodel.select
            user_info = session.exec(
                sqlmodel.select(UserInfo).where(UserInfo.email == self.email)
            ).one_or_none()

            if user_info:
                # Genera un token seguro
                token_str = secrets.token_urlsafe(32)
                expires = datetime.utcnow() + timedelta(hours=1) # El token dura 1 hora

                # Guarda el token en la base de datos
                reset_token = PasswordResetToken(
                    token=token_str,
                    user_id=user_info.user_id,
                    expires_at=expires
                )
                session.add(reset_token)
                session.commit()

                # Envía el correo
                send_password_reset_email(
                    recipient_email=self.email,
                    token=token_str
                )

            # Por seguridad, siempre muestra un mensaje de éxito,
            # incluso si el correo no existe.
            self.message = "Si una cuenta con ese correo existe, hemos enviado un enlace para restablecer la contraseña."
            self.is_success = True