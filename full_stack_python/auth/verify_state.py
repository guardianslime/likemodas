import reflex as rx
from ..models import VerificationToken, UserInfo
from datetime import datetime

class VerifyState(rx.State):
    message: str = "Verificando tu cuenta..."
    is_verified: bool = False

    @rx.event
    def verify_token(self):
        token = self.router.page.params.get("token", "")
        if not token:
            self.message = "Error: No se proporcionó un token de verificación."
            return

        with rx.session() as session:
            # Buscar el token en la BD
            db_token = session.exec(
                rx.select(VerificationToken).where(VerificationToken.token == token)
            ).one_or_none()

            if not db_token:
                self.message = "El token de verificación no es válido o ya ha sido utilizado."
                return

            if datetime.utcnow() > db_token.expires_at:
                self.message = "El token de verificación ha expirado. Por favor, solicita uno nuevo."
                # (Aquí podrías añadir lógica para reenviar el token)
                session.delete(db_token)
                session.commit()
                return

            # Si todo está bien, verificamos al usuario
            user_info = session.get(UserInfo, db_token.userinfo_id)
            if user_info:
                user_info.is_verified = True
                session.add(user_info)

                # Eliminamos el token para que sea de un solo uso
                session.delete(db_token)
                session.commit()

                self.message = "✅ ¡Tu cuenta ha sido verificada con éxito! Ya puedes iniciar sesión."
                self.is_verified = True
            else:
                self.message = "Error: No se encontró el usuario asociado a este token."