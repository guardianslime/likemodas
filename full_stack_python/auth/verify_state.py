import reflex as rx
import reflex_local_auth
import sqlmodel  # ✨ 1. AÑADE ESTA IMPORTACIÓN
from ..models import VerificationToken, UserInfo
from datetime import datetime
from ..auth.state import SessionState

class VerifyState(SessionState): 
    message: str = "Verificando tu cuenta..."
    is_verified: bool = False

    @rx.event
    def verify_token(self):
        token = self.router.page.params.get("token", "")
        if not token:
            self.message = "Error: No se proporcionó un token de verificación."
            return

        with rx.session() as session:
            # ✨ 2. CORRIGE rx.select a sqlmodel.select
            db_token = session.exec(
                sqlmodel.select(VerificationToken).where(VerificationToken.token == token)
            ).one_or_none()

            if not db_token or datetime.utcnow() > db_token.expires_at:
                self.message = "El token de verificación es inválido o ha expirado."
                if db_token:
                    session.delete(db_token)
                    session.commit()
                return

            user_info = session.get(UserInfo, db_token.userinfo_id)
            if user_info:
                user_info.is_verified = True
                session.add(user_info)
                session.delete(db_token)
                session.commit()

                yield rx.toast.success("¡Cuenta verificada! Por favor, inicia sesión.")
                return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)
            
            else:
                self.message = "Error: No se encontró el usuario asociado a este token."