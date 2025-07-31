# likemodas/models/enums.py (ARCHIVO CORREGIDO)

import enum

# ✅ SOLUCIÓN: Se usan valores en minúsculas para que coincidan con la base de datos.
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