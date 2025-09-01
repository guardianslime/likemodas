import re

def validate_password(password: str) -> list[str]:
    """
    Valida que una contraseña cumpla con los requisitos de seguridad.
    Devuelve una lista de errores. Si la lista está vacía, la contraseña es válida.
    """
    errors = []
    if len(password) < 8:
        errors.append("Debe tener al menos 8 caracteres.")
    if not re.search(r"\d", password):
        errors.append("Debe contener al menos un número.")
    if not re.search(r"[A-Z]", password):
        errors.append("Debe contener al menos una letra mayúscula.")
    
    return errors