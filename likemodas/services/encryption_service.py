# likemodas/services/encryption_service.py

# likemodas/services/encryption_service.py

import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from typing import Optional

# Cargamos variables locales si existen (útil para desarrollo local)
load_dotenv()

# Variable global para guardar la instancia de Fernet en memoria
# Se inicia en None y solo se llena cuando se usa por primera vez.
_fernet_instance = None

def _get_fernet() -> Fernet:
    """
    Obtiene o crea la instancia de encriptación.
    Esta función se llama SOLO cuando se intenta encriptar/desencriptar.
    Aquí es donde validamos que la clave exista de forma segura.
    """
    global _fernet_instance
    
    # Si ya tenemos la instancia lista, la usamos (eficiencia)
    if _fernet_instance is not None:
        return _fernet_instance

    # Buscamos la clave en las variables de entorno AHORA
    key = os.getenv("TFA_ENCRYPTION_KEY")
    
    # --- VALIDACIÓN DE SEGURIDAD ---
    # Si la clave no existe, lanzamos el error AHORA.
    # Esto protege tu producción: si falta la clave, la app fallará al intentar
    # proteger datos, en lugar de usar una clave insegura.
    if not key:
        raise ValueError("CRÍTICO: La variable de entorno TFA_ENCRYPTION_KEY no está configurada.")
    
    try:
        _fernet_instance = Fernet(key.encode())
    except Exception as e:
        raise ValueError(f"CRÍTICO: La clave TFA_ENCRYPTION_KEY no es válida. Error: {e}")
        
    return _fernet_instance

def encrypt_secret(secret: str) -> str:
    """Encripta un secreto usando la clave configurada."""
    if not secret:
        return ""
    
    # Llamamos a _get_fernet() aquí. Si estamos en 'reflex export',
    # esta línea NUNCA se ejecuta, por lo tanto no pide la clave.
    f = _get_fernet() 
    encrypted_bytes = f.encrypt(secret.encode('utf-8'))
    return encrypted_bytes.decode('utf-8')

def decrypt_secret(encrypted_secret: str) -> Optional[str]:
    """Desencripta un token usando la clave configurada."""
    if not encrypted_secret:
        return None
        
    try:
        f = _get_fernet()
        decrypted_bytes = f.decrypt(encrypted_secret.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')
    except Exception:
        # Si falla la desencriptación (clave incorrecta o data corrupta), retornamos None
        return None