# full_stack_python/auth/state.py
import reflex as rx
from sqlmodel import select
from ..models import User
from ..navigation import routes
import bcrypt

class AuthState(rx.State):
    """
    The authentication state for the app.
    """
    user: User | None = None

    @rx.var
    def is_logged_in(self) -> bool:
        """
        Check if the user is logged in.
        """
        return self.user is not None

    def _set_auth_token(self, token: str):
        """
        Set the authentication token.
        """
        self.set_cookie("auth_token", token, same_site="lax")

    def logout(self):
        """
        Log the user out.
        """
        self.user = None
        self._set_auth_token("")

    def check_login(self):
        """
        Check if the user is logged in.
        """
        if not self.is_logged_in and self.router.page.path != routes.LOGIN:
            auth_token = self.get_cookie("auth_token")
            if auth_token:
                with rx.session() as session:
                    self.user = session.exec(
                        select(User).where(User.password_hash == auth_token)
                    ).first()
                    if self.user:
                        return
            # The user is not logged in, so redirect to the login page.
            if self.router.page.path not in [
                routes.LOGIN,
                routes.REGISTER,
                "/",
            ] and not self.router.page.path.startswith("/blog"):
                return rx.redirect(routes.LOGIN)

    def _login(self, user: User):
        """
        Log the user in.
        """
        self.user = user
        self._set_auth_token(self.user.password_hash)

    def login(self, form_data) -> rx.event.EventSpec:
        """
        Login a user.
        """
        with rx.session() as session:
            user = session.exec(
                select(User).where(User.username == form_data["username"])
            ).first()
            if user and bcrypt.checkpw(
                form_data["password"].encode("utf-8"), user.password_hash.encode("utf-8")
            ):
                self._login(user)
                return rx.redirect(self.router.page.path or routes.HOME)
            else:
                return rx.window_alert("Invalid username or password.")

    def register(self, form_data) -> rx.event.EventSpec:
        """
        Register a new user.
        """
        if form_data["password"] != form_data["confirm_password"]:
            return rx.window_alert("Passwords do not match.")
        
        password_hash = bcrypt.hashpw(
            form_data["password"].encode("utf-8"), bcrypt.gensalt()
        )
        with rx.session() as session:
            if session.exec(
                select(User).where(User.username == form_data["username"])
            ).first():
                return rx.window_alert("Username already exists.")
            
            user = User(
                username=form_data["username"],
                password_hash=password_hash.decode("utf-8"),
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        self._login(user)
        return rx.redirect(routes.HOME)