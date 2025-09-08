# rxconfig.py (VERSIÓN FINAL Y CORRECTA)

import reflex as rx
import os

# La URL pública donde vivirá tu aplicación en Railway.
RAILWAY_PUBLIC_URL = "https://full-stack-python-production.up.railway.app"

# La URL final para tus usuarios.
PRODUCTION_DOMAIN = "https://www.likemodas.com"

# La URL de Vercel (opcional, pero bueno tenerla para CORS).
VERCEL_PREVIEW_URL = "https://full-stack-python.vercel.app"

# --- ✨ INICIO DE LA MODIFICACIÓN: TEMA DE DISEÑO MEJORADO ✨ ---
config = rx.Config(
    app_name="likemodas",
    show_built_with_reflex=False,
    
    # URLs de despliegue
    api_url=RAILWAY_PUBLIC_URL,
    deploy_url=PRODUCTION_DOMAIN,
    
    # Orígenes permitidos para CORS
    cors_allowed_origins=[
        "http://localhost:3000",
        PRODUCTION_DOMAIN,
        VERCEL_PREVIEW_URL,
    ],
    
    db_url="postgresql://postgres:rszvQoEjlvQijlSTROgqCEDPiNdQqqmU@nozomi.proxy.rlwy.net:37918/railway",
    
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],

    # Se define un tema estético con "violet" como color de acento.
    # Esto afectará a botones, switches, insignias y otros componentes.
    theme=rx.theme(
        appearance="light", # El modo por defecto ahora es claro.
        has_background=True,
        radius="medium",
        accent_color="violet", # 💜 El color principal para elementos interactivos.
        panel_background="translucent", # Paneles con un fondo sutil.
    ),
)
# --- ✨ FIN DE LA MODIFICACIÓN ✨ ---