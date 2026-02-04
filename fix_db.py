# fix_db.py
import reflex as rx
from sqlmodel import text
# Importamos tu estado para asegurar que la DB se inicialice
from likemodas.state import AppState 

def arreglar_base_datos():
    print("🧹 Iniciando limpieza de historial de migraciones...")
    try:
        with rx.session() as session:
            # Borramos la tabla que causa el conflicto
            session.exec(text("DROP TABLE IF EXISTS alembic_version CASCADE;"))
            session.commit()
            print("✅ ÉXITO: Tabla 'alembic_version' eliminada correctamente.")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    arreglar_base_datos()