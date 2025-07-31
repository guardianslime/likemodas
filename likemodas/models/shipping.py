from sqlmodel import Field, Relationship
from datetime import datetime
import reflex as rx

from likemodas.models.user import UserInfo

class ShippingAddressModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    name: str
    phone: str
    city: str
    neighborhood: str
    address: str
    is_default: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    userinfo: "UserInfo" = Relationship(back_populates="shipping_addresses")
