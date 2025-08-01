# likemodas/models/enums.py (SOLUCIÓN AL LookupError)

import enum

# ✅ SOLUCIÓN: Se usan valores en minúsculas para que coincidan con la base de datos.
# SQLAlchemy ahora entenderá que el valor 'customer' de la base de datos
# corresponde a UserRole.CUSTOMER en Python.
class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"

class PurchaseStatus(str, enum.Enum):
    PENDING = "pending_confirmation"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"

class VoteType(str, enum.Enum):
    LIKE = "like"
    DISLIKE = "dislike"

class Category(str, enum.Enum):
    ROPA = "ropa"
    CALZADO = "calzado"
    MOCHILAS = "mochilas"
    OTROS = "otros"