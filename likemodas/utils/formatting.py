# likemodas/utils/formatting.py

import locale

def format_to_cop(price: float) -> str:
    """
    Formatea un valor numérico a una cadena de texto en formato de pesos colombianos (COP).
    Ejemplo: 12000.50 -> "$ 12.000"
    """
    if price is None:
        return "$ 0"
    try:
        # Intentamos usar la localización colombiana para un formato perfecto.
        locale.setlocale(locale.LC_ALL, 'es_CO.UTF-8')
        # Formateamos como moneda, sin centavos.
        return locale.currency(price, grouping=True, symbol=True).split(',')[0]
    except (locale.Error, ValueError):
        # Si la localización falla, usamos un método manual seguro.
        price_int = int(price)
        return f"$ {price_int:,}".replace(",", ".")