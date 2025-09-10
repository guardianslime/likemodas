# likemodas/services/wompi_validator.py
import hashlib
import json
from typing import Any, Dict, Mapping

def _get_nested_value(data: Dict[str, Any], key_path: str) -> Any:
    """Navega un diccionario usando una clave con puntos (ej. 'transaction.id')."""
    keys = key_path.split('.')
    value = data
    for key in keys:
        value = value[key]
    return value

def verify_wompi_signature(payload: bytes, headers: Mapping[str, str], secret: str) -> bool:
    """Valida la firma de un webhook de Wompi según su protocolo específico[cite: 138]."""
    try:
        event_data = json.loads(payload)
        
        # La cabecera puede variar, busca la correcta
        signature_header = headers.get("x-event-checksum") or headers.get("Wompi-Signature")
        if not signature_header:
            return False

        # Paso 1: Extraer dinámicamente las propiedades a firmar [cite: 122]
        properties_to_sign = event_data.get("signature", {}).get("properties", [])
        if not properties_to_sign:
            return False

        # Paso 2: Construir la cadena concatenando los valores en orden [cite: 124]
        concatenated_string = ""
        transaction_data = event_data.get("data", {})
        for prop_key in properties_to_sign:
            value = _get_nested_value(transaction_data, prop_key)
            concatenated_string += str(value)
            
        # Paso 3: Añadir el timestamp y el secreto [cite: 125, 126]
        timestamp = event_data.get("timestamp")
        if timestamp is None:
            return False
        
        concatenated_string += str(timestamp)
        concatenated_string += secret

        # Paso 4: Calcular el hash SHA256 [cite: 127]
        computed_hash = hashlib.sha256(concatenated_string.encode("utf-8")).hexdigest()
        
        # Paso 5: Comparación segura [cite: 128]
        return hashlib.secure_compare(signature_header, computed_hash)
        
    except (KeyError, TypeError, json.JSONDecodeError) as e:
        print(f"Error durante la validación de la firma: {e}")
        return False