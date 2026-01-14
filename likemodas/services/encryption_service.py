import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# Cargamos variables locales si existen
load_dotenv()

# Variable global para guardar la instancia de Fernet en memoria y no crearla mil veces
_fernet_instance = None

def _get_fernet() -> Fernet:
    """
    Obtiene o crea la instancia de encriptación.
    Esta función se llama SOLO cuando se necesita encriptar/desencriptar.
    Aquí es donde validamos que la clave exista de forma segura.
    """
    global _fernet_instance
    
    # Si ya tenemos la instancia lista, la devolvemos (eficiencia)
    if _fernet_instance is not None:
        return _fernet_instance

    # Buscamos la clave en las variables de entorno
    key = os.getenv("TFA_ENCRYPTION_KEY")
    
    # --- VALIDACIÓN DE SEGURIDAD ---
    # Si la clave no existe, lanzamos el error AHORA.
    # Esto protege tu producción: si falta la clave, la app fallará al intentar
    # proteger datos, en lugar de usar una clave insegura.
    if not key:
        raise ValueError("CRÍTICO: La variable de entorno TFA_ENCRYPTION_KEY no está configurada.")
    
    try:
        _fernet_instance = Fernet(key)
    except Exception as e:
        raise ValueError(f"CRÍTICO: La clave TFA_ENCRYPTION_KEY no es válida para Fernet. Error: {e}")
        
    return _fernet_instance

def encrypt_secret(secret: str) -> str:
    """Encripta un secreto usando la clave configurada."""
    if not secret:
        return ""
    
    f = _get_fernet() # Aquí es donde se valida la clave
    return f.encrypt(secret.encode()).decode()

def decrypt_secret(token: str) -> str:
    """Desencripta un token usando la clave configurada."""
    if not token:
        return ""
        
    f = _get_fernet() # Aquí es donde se valida la clave
    return f.decrypt(token.encode()).decode()