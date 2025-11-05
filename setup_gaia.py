"""""
Guarda este script como setup_gaia.py en la raíz del proyecto y ejecútalo
"""

import os
import sys
import subprocess

def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    print(f"✅ {description} completado")
    return True

def setup_gaia():
    """Configurar proyecto GAIA automáticamente"""
    
    print("""
    ╔════════════════════════════════════════════╗
    ║                                            ║
    ║        🌱 GAIA SETUP AUTOMÁTICO 🌱        ║
    ║                                            ║
    ╚════════════════════════════════════════════╝
    """)
    
    # Verificar Python
    if not run_command("python --version", "Verificando Python"):
        print("Por favor instala Python 3.8 o superior")
        return
    
    # Crear directorios necesarios
    directories = ['frontend', 'media', 'ml_models', 'staticfiles', 
                   'predictions/management', 'predictions/management/commands']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Directorio creado: {directory}")
    
    # Crear archivos __init__.py
    init_files = [
        'predictions/management/__init__.py',
        'predictions/management/commands/__init__.py'
    ]
    
    for init_file in init_files:
        open(init_file, 'a').close()
        print(f"📄 Archivo creado: {init_file}")
    
    # Instalar dependencias
    if not run_command("pip install -r requirements.txt", "Instalando dependencias"):
        return
    
    # Crear migraciones
    if not run_command("python manage.py makemigrations", "Creando migraciones"):
        return
    
    # Aplicar migraciones
    if not run_command("python manage.py migrate", "Aplicando migraciones a la base de datos"):
        return
    
    # Entrenar modelo
    if not run_command("python manage.py train_model", "Entrenando modelo de Machine Learning"):
        return
    
    print("""
    ╔════════════════════════════════════════════╗
    ║                                            ║
    _         INSTALACIÓN COMPLETADA             _
    ║                                            ║
    ╚════════════════════════════════════════════╝
    
 Qué Sigue?
    
    1. Crear superusuario (administrador):
       python manage.py createsuperuser
    
    2. Iniciar el servidor:
       python manage.py runserver
    
    3. Abrir en el navegador:
       http://localhost:8000/
    
    4. Acceder al panel de administración:
       http://localhost:8000/admin/
    
    Vivelo,Sientelo,Amalo. Bienvenido a Gaia.
    """)

if __name__ == '__main__':
    setup_gaia()