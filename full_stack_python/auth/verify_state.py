# full_stack_python/auth/verify_state.py (CORREGIDO)

import reflex as rx
import reflex_local_auth # No olvides importar esto
from ..models import VerificationToken, UserInfo
from datetime import datetime
from ..auth.state import SessionState # Importa SessionState

# ✨ CAMBIO 1: Hereda de SessionState para tener contexto de la sesión
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
            db_token = session.exec(
                rx.select(VerificationToken).where(VerificationToken.token == token)
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
                session.delete(db_token) # El token es de un solo uso
                session.commit()

                # ✨ CAMBIO 2: Redirigir al login en lugar de solo cambiar el mensaje
                yield rx.toast.success("¡Cuenta verificada! Por favor, inicia sesión.")
                return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)
            
            else:
                self.message = "Error: No se encontró el usuario asociado a este token."