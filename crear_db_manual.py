import sqlite3
import os

# Nombre de la base de datos temporal
DB_NAME = "reflex_build.db"

def crear_tablas_manualmente():
    # Si existe la borramos para empezar limpio
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        
    print(f"Creando {DB_NAME} con Python puro...")
    
    # Conectamos directamente con SQLite (sin intermediarios)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Creamos la tabla 'localuser' (la que daba el error)
    # Definimos las columnas básicas que espera reflex-local-auth
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS localuser (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            enabled BOOLEAN NOT NULL DEFAULT 1
        )
    ''')
    
    # 2. Creamos la tabla 'localauthsession' (para sesiones)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS localauthsession (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_id TEXT NOT NULL,
            expiration TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES localuser(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("¡Tablas creadas exitosamente! El conflicto de versiones ha sido evitado.")

if __name__ == "__main__":
    crear_tablas_manualmente()