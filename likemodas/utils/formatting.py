import locale
from typing import Optional

# Configura el localismo para Colombia. Idealmente, esto se hace una vez al inicio de la app.
try:
    locale.setlocale(locale.LC_ALL, 'es_CO.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'Spanish_Colombia')
    except locale.Error:
        print("Advertencia: No se pudo establecer el localismo a es_CO.UTF-8. El formato de moneda puede ser incorrecto.")

def format_to_cop(price: Optional[float]) -> str:
    """Formatea un número flotante a una cadena de moneda COP, manejando valores nulos."""
    if price is None:
        return "$ 0"  # Devuelve un valor por defecto si el precio es nulo
    
    # Esta línea ahora es segura porque 'price' es un número real, no un rx.Var
    return locale.currency(price, grouping=True, symbol=True).split(',')[0]