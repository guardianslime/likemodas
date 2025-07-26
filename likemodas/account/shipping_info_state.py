import reflex as rx
from typing import List, Dict
from ..auth.state import SessionState
from ..models import ShippingAddressModel
from sqlmodel import select, update
from ..data.colombia_locations import load_colombia_data # <-- Se importa la data

class ShippingInfoState(SessionState):
    """Gestiona las direcciones de envío del usuario."""
    
    addresses: List[ShippingAddressModel] = []
    show_form: bool = False

    # --- ✨ NUEVO ESTADO PARA LOS SELECTORES CON BÚSQUEDA ---
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

    # --- ✨ NUEVOS MANEJADORES DE EVENTOS ---
    def set_city(self, city: str):
        """Establece la ciudad y resetea el barrio."""
        self.city = city
        self.neighborhood = ""
        self.search_neighborhood = ""

    def set_neighborhood(self, neighborhood: str):
        self.neighborhood = neighborhood

    def set_search_city(self, query: str):
        self.search_city = query

    def set_search_neighborhood(self, query: str):
        self.search_neighborhood = query
        
    def _reset_form_fields(self):
        """Ayudante para resetear todos los campos del formulario."""
        self.show_form = False
        self.city = ""
        self.neighborhood = ""
        self.search_city = ""
        self.search_neighborhood = ""
    # --- FIN DE LAS ADICIONES ---

    @rx.event
    def toggle_form(self):
        """Muestra u oculta el formulario para añadir una nueva dirección."""
        self.show_form = not self.show_form
        # Resetea los campos si se cancela el formulario
        if not self.show_form:
            self._reset_form_fields()

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
        # --- ✨ MODIFICADO: Ahora lee ciudad y barrio desde el estado ---
        if not all([form_data.get("name"), form_data.get("phone"), self.city, form_data.get("address")]):
            return rx.toast.error("Por favor, completa todos los campos requeridos.")

        with rx.session() as session:
            is_first_address = len(self.addresses) == 0
            
            new_address = ShippingAddressModel(
                userinfo_id=self.authenticated_user_info.id,
                name=form_data["name"],
                phone=form_data["phone"],
                city=self.city,                   # <-- Usa la variable de estado
                neighborhood=self.neighborhood,  # <-- Usa la variable de estado
                address=form_data["address"],
                is_default=is_first_address
            )
            session.add(new_address)
            session.commit()
        
        self._reset_form_fields()
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