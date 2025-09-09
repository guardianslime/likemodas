# likemodas/wompi_client.py
import os
import requests
from typing import Dict, Any

class WompiClient:
    def __init__(self):
        self.base_url = "https://sandbox.wompi.co/v1"  # URL de sandbox
        self.public_key = os.getenv("WOMPI_PUBLIC_KEY")
        self.private_key = os.getenv("WOMPI_PRIVATE_KEY")
        self.headers = {"Authorization": f"Bearer {self.private_key}"}

    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Método auxiliar para realizar peticiones a la API de Wompi."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(method, url, json=data, headers=self.headers)
            response.raise_for_status()  # Lanza una excepción para errores HTTP
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error en la comunicación con Wompi: {e}")
            raise

    def create_transaction(self, **kwargs: Any) -> Dict:
        """Crea una nueva transacción de pago."""
        return self._make_request("post", "transactions", data=kwargs)

# Instancia única para ser usada en toda la aplicación
wompi = WompiClient()