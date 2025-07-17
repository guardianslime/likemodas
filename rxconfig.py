import reflex as rx
import os

# --- URLs de la aplicación ---
API_URL = "https://full-stack-python-production.up.railway.app"
DEPLOY_URL = "https://full-stack-python.vercel.app"
PREVIEW_URL = "https://full-stack-python-ibehoa7sb-nkpz01s-projects.vercel.app"

# --- Lista de orígenes permitidos por defecto ---
default_origins = [
    "http://localhost:3000",
    API_URL,
    DEPLOY_URL,
    PREVIEW_URL,
]

additional_origins = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
cors_allowed_origins = list(
    {
        origen.strip()
        for origen in default_origins + additional_origins
        if origen.strip()
    }
)

config = rx.Config(
    app_name="full_stack_python",
    show_built_with_reflex=False,
    db_url="postgresql://postgres:rszvQoEjlvQijlSTROgqCEDPiNdQqqmU@nozomi.proxy.rlwy.net:37918/railway",
    api_url=API_URL,
    cors_allowed_origins=cors_allowed_origins,

    # --- ✨ LÍNEAS ESENCIALES PARA EL CARRUSEL Y TEMA ✨ ---
    stylesheets=[
        "https://unpkg.com/swiper/swiper-bundle.min.css",
    ],
    scripts=[
        "https://unpkg.com/swiper/swiper-bundle.min.js",
    ],
    theme=rx.theme(
        appearance="dark",
        has_background=True,
        panel_background="solid",
        scaling="90%",
        radius="medium",
        accent_color="sky"
    )
)
