import os
import json

# Ruta exacta donde Reflex busca los archivos estáticos
# NOTA: En Reflex, todo lo que está en 'assets' se copia a la raíz de la web.
target_dir = os.path.join("assets", ".well-known")
target_file = os.path.join(target_dir, "assetlinks.json")

# Tu huella SHA-256 (La tomé de tu captura anterior)
sha256 = "DB:E5:6D:DF:32:E1:99:4D:F6:C2:42:B9:DD:5C:03:17:61:E7:EC:80:AF:06:3F:2A:C5:2A:24:9E:6E:A4:FD:95"

content = [
  {
    "relation": ["delegate_permission/common.handle_all_urls"],
    "target": {
      "namespace": "android_app",
      "package_name": "com.likemodas.app",
      "sha256_cert_fingerprints": [sha256]
    }
  }
]

# Crear carpeta si no existe
if not os.path.exists(target_dir):
    os.makedirs(target_dir)
    print(f"Carpeta creada: {target_dir}")

# Crear el archivo
with open(target_file, "w") as f:
    json.dump(content, f, indent=2)

print(f"✅ Archivo creado exitosamente en: {target_file}")
print("Ahora ejecuta los comandos de git para subirlo.")