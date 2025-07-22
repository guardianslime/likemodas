# likemodas/account/shipping_info_state.py

import reflex as rx
from typing import List
from ..auth.state import SessionState
from ..models import ShippingAddressModel
from sqlmodel import select, update

class ShippingInfoState(SessionState):
    """Gestiona las direcciones de envío del usuario."""
    
    # Lista para mostrar las direcciones guardadas
    addresses: List[ShippingAddressModel] = []
    
    # Un interruptor para mostrar/ocultar el formulario de nueva dirección
    show_form: bool = False

    @rx.event
    def toggle_form(self):
        """Muestra u oculta el formulario para añadir una nueva dirección."""
        self.show_form = not self.show_form

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
        # Validación simple
        if not all([form_data.get("name"), form_data.get("phone"), form_data.get("city"), form_data.get("address")]):
            return rx.toast.error("Por favor, completa todos los campos requeridos.")

        with rx.session() as session:
            # Si es la primera dirección, se establece como predeterminada
            is_first_address = len(self.addresses) == 0
            
            new_address = ShippingAddressModel(
                userinfo_id=self.authenticated_user_info.id,
                name=form_data["name"],
                phone=form_data["phone"],
                city=form_data["city"],
                neighborhood=form_data.get("neighborhood", ""),
                address=form_data["address"],
                is_default=is_first_address
            )
            session.add(new_address)
            session.commit()
        
        self.show_form = False # Oculta el formulario después de enviar
        return self.load_addresses() # Recarga la lista

    @rx.event
    def set_as_default(self, address_id: int):
        """Establece una dirección como la predeterminada."""
        user_id = self.authenticated_user_info.id
        with rx.session() as session:
            # 1. Quita la marca de 'default' de todas las demás direcciones del usuario
            session.exec(
                update(ShippingAddressModel)
                .where(ShippingAddressModel.userinfo_id == user_id)
                .values(is_default=False)
            )
            # 2. Establece la dirección seleccionada como la nueva predeterminada
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