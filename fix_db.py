# fix_db.py
import reflex as rx
from sqlmodel import text

def arreglar_base_datos():
    print("🧹 Iniciando limpieza de historial de migraciones...")
    try:
        with rx.session() as session:
            # Quitamos 'CASCADE' para que funcione en SQLite (Local) y Postgres
            session.exec(text("DROP TABLE IF EXISTS alembic_version"))
            session.commit()
            print("✅ ÉXITO: Tabla 'alembic_version' eliminada correctamente.")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    arreglar_base_datos()