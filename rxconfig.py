# rxconfig.py (SOLUCIÓN)

import reflex as rx
from reflex.plugins import SitemapPlugin

# La lógica de CORS se puede simplificar o eliminar si no es estrictamente necesaria.
# Para Railway, a menudo no se necesita una configuración de CORS tan compleja.
config = rx.Config(
    app_name="likemodas",
    db_url="postgresql://postgres:rszvQoEjlvQijlSTROgqCEDPiNdQqqmU@nozomi.proxy.rlwy.net:37918/railway",
    # Eliminamos api_url para que Reflex lo gestione automáticamente.
    plugins=[
        SitemapPlugin(),
    ],
)