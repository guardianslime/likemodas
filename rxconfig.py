import reflex as rx
import os




cors_origenes = os.getenv("CORS_ALLOWED_ORIGINS", "https://full-stack-python-ibehoa7sb-nkpz01s-projects.vercel.app").split(",")

config = rx.Config(
    app_name="full_stack_python",
    db_url="postgresql://postgres:rszvQoEjlvQijlSTROgqCEDPiNdQqqmU@nozomi.proxy.rlwy.net:37918/railway",
    api_url="https://full-stack-python-production.up.railway.app",
    deploy_url="https://full-stack-python.vercel.app",
    cors_allowed_origins=[origen.strip() for origen in cors_origenes]
)