import reflex as rx
import reflex_local_auth
import bcrypt
import sqlmodel
from datetime import datetime
from ..models import PasswordResetToken, LocalUser
from ..auth.state import SessionState

class ResetPasswordState(SessionState):
    token: str = ""
    is_token_valid: bool = False
    message: str = ""
    password: str = ""
    confirm_password: str = ""

    def on_load_check_token(self):
        self.token = self.router.page.params.get("token", "")
        if not self.token:
            self.message = "Enlace no válido. Falta el token."
            self.is_token_valid = False
            return

        with rx.session() as session:
            db_token = session.exec(
                sqlmodel.select(PasswordResetToken).where(PasswordResetToken.token == self.token)
            ).one_or_none()

            if not db_token or datetime.utcnow() > db_token.expires_at:
                self.message = "El enlace de reseteo es inválido o ha expirado."
                self.is_token_valid = False
                if db_token:
                    session.delete(db_token)
                    session.commit()
                return

            self.is_token_valid = True

    def handle_reset_password(self):
        if not self.is_token_valid:
            self.message = "Token no válido. Por favor, solicita un nuevo enlace."
            return

        if self.password != self.confirm_password:
            self.message = "Las contraseñas no coinciden."
            return
        
        if len(self.password) < 4:
            self.message = "La contraseña es demasiado corta."
            return

        with rx.session() as session:
            db_token = session.exec(
                sqlmodel.select(PasswordResetToken).where(PasswordResetToken.token == self.token)
            ).one_or_none()

            if not db_token:
                self.message = "El token ha expirado o ya fue utilizado."
                return
            
            user = session.get(LocalUser, db_token.user_id)
            if user:
                hashed_password = bcrypt.hashpw(self.password.encode("utf-8"), bcrypt.gensalt())
                
                # ✨ CAMBIO CRÍTICO: Elimina .decode("utf-8") para guardar los bytes directamente
                user.password_hash = hashed_password
                
                session.add(user)
                session.delete(db_token)
                session.commit()

                yield rx.toast.success("¡Contraseña actualizada con éxito!")
                return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)