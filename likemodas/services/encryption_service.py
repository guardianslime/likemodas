import os
from cryptography.fernet import Fernet
from typing import Optional

ENCRYPTION_KEY = os.getenv("TFA_ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    raise ValueError("La variable de entorno TFA_ENCRYPTION_KEY no está configurada.")

try:
   fernet = Fernet(ENCRYPTION_KEY.encode())
except (ValueError, TypeError) as e:
    raise ValueError(f"La clave de cifrado es inválida: {e}")

def encrypt_secret(secret: str) -> str:
     if not secret:
        return ""
     encrypted_bytes = fernet.encrypt(secret.encode('utf-8'))
     return encrypted_bytes.decode('utf-8')

def decrypt_secret(encrypted_secret: str) -> Optional[str]:
     if not encrypted_secret:
       return None
     try:
       decrypted_bytes = fernet.decrypt(encrypted_secret.encode('utf-8'))
       return decrypted_bytes.decode('utf-8')
     except Exception:
         return None