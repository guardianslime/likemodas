# likemodas/account/shipping_info_state.py

import reflex as rx
from typing import List, Dict
from sqlmodel import select, update

# Se importa el estado BASE, no el global
from ..auth.state import SessionState
from ..models import ShippingAddressModel
from ..data.colombia_locations import load_colombia_data

# La clase ahora hereda de SessionState
class ShippingInfoState(SessionState):
    """Gestiona las direcciones de envío del usuario."""
    
    addresses: List[ShippingAddressModel] = rx.Field(default_factory=list)
    show_form: bool = False

    colombia_data: Dict[str, List[str]] = load_colombia_data()
    city: str = ""
    neighborhood: str = ""
    search_city: str = ""
    search_neighborhood: str = ""

    @rx.var
    def cities(self) -> List[str]:
        """Devuelve una lista filtrada de ciudades."""
        if not self.search_city.strip():
            return sorted(list(self.colombia_data.keys()))
        return [c for c in self.colombia_data if self.search_city.lower() in c.lower()]

    @rx.var
    def neighborhoods(self) -> List[str]:
        """Devuelve los barrios filtrados para la ciudad seleccionada."""
        if not self.city:
            return []
        all_neighborhoods = self.colombia_data.get(self.city, [])
        if not self.search_neighborhood.strip():
            return all_neighborhoods
        return [n for n in all_neighborhoods if self.search_neighborhood.lower() in n.lower()]

    def set_city(self, city: str):
        self.city = city
        self.neighborhood = ""
        self.search_neighborhood = ""

    def set_neighborhood(self, neighborhood: str):
        self.neighborhood = neighborhood
        
    @rx.event
    def load_addresses(self):
        """Carga todas las direcciones del usuario actual."""
        if not self.authenticated_user_info:
            self.addresses = []
            return
        
        with rx.session() as session:
            self.addresses = session.exec(
                select(ShippingAddressModel)
                .where(ShippingAddressModel.userinfo_id == self.authenticated_user_info.id)
                .order_by(ShippingAddressModel.created_at.desc())
            ).all()

    @rx.event
    def add_new_address(self, form_data: dict):
        """Guarda una nueva dirección en la base de datos."""
        if not all([form_data.get("name"), form_data.get("phone"), self.city, form_data.get("address")]):
            return rx.toast.error("Por favor, completa todos los campos requeridos.")

        with rx.session() as session:
            is_first_address = len(self.addresses) == 0
            
            new_address = ShippingAddressModel(
                userinfo_id=self.authenticated_user_info.id,
                name=form_data["name"],
                phone=form_data["phone"],
                city=self.city,
                neighborhood=self.neighborhood,
                address=form_data["address"],
                is_default=is_first_address
            )
            session.add(new_address)
            session.commit()
        
        return self.load_addresses()

    @rx.event
    def set_as_default(self, address_id: int):
        """Establece una dirección como la predeterminada."""
        user_id = self.authenticated_user_info.id
        with rx.session() as session:
            session.exec(
                update(ShippingAddressModel)
                .where(ShippingAddressModel.userinfo_id == user_id)
                .values(is_default=False)
            )
            session.exec(
                update(ShippingAddressModel)
                .where(ShippingAddressModel.id == address_id)
                .values(is_default=True)
            )
            session.commit()
        
        return self.load_addresses()

    @rx.event
    def delete_address(self, address_id: int):
        """Elimina una dirección de la base de datos."""
        with rx.session() as session:
            address_to_delete = session.get(ShippingAddressModel, address_id)
            if address_to_delete:
                session.delete(address_to_delete)
                session.commit()
        
        return self.load_addresses()