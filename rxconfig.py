# Este archivo es para configurar tu entorno de DESARROLLO LOCAL.
# NO subas este archivo a Git.

# --- Clave de Cifrado 2FA ---
TFA_ENCRYPTION_KEY="H3_5P_g8KAYk5s6VtRbGiGy83nr0nP0zxTbq6D0C43Y="

# --- Conexión a la Base de Datos ---
# [MODIFICADO] Usamos SQLite para local. Comentamos la de Railway con #.
DATABASE_URL="sqlite:///reflex.db"
# DATABASE_URL="postgresql://postgres:giMZ6Ns3llgN9lB5TvMyotxB5JnSuMLlawb3ogFU2hTmrcb9qzZ2dtNk4boIvTPTG@46.224.58.236:3000/postgres"

# --- URLs de la Aplicación ---
# Para desarrollo local, estas son las URLs base.
APP_BASE_URL="http://localhost:3000"
API_URL="http://localhost:8000"

# --- Claves de WOMPI (Usa las de PRUEBAS/SANDBOX para desarrollo) ---
WOMPI_PRIVATE_KEY_ACTIVE="prv_test_1V2rwRDyicUJTKLq2k1lrXkA9479dYPO"
WOMPI_EVENTS_SECRET_ACTIVE="test_events_ubrxthRp8DPzgwM4hrVva7jQLhFnDFvV"
WOMPI_API_BASE_URL="https://sandbox.wompi.co/v1"

# --- Clave de Resend (para enviar correos) ---
RESEND_API_KEY="re_DL77enyw_2h1FSQJB5fVgUtsFZzHZDPMp"

# --- Otros Secretos de la Aplicación ---
ADMIN_REGISTRATION_KEY="0EL0YnUgV1UJNum3A4aJ"
CRON_SECRET="kR7pZ9wXv4mN3bCjF6gH8sT2"