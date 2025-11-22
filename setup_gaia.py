"""Script de configuración automática para el proyecto GAIA."""
import os
import sys
import subprocess
import shutil
from pathlib import Path


class Colors:
    """Códigos ANSI para colores en terminal."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_banner():
    print(f"""
    {Colors.CYAN}{Colors.BOLD}
    ╔════════════════════════════════════════════╗
    ║                                            ║
    ║         🌍 GAIA SETUP AUTOMÁTICO           ║
    ║                                            ║
    ╚════════════════════════════════════════════╝
    {Colors.END}
    """)


def print_success(msg):
    print(f"  {Colors.GREEN}✓{Colors.END} {msg}")


def print_error(msg):
    print(f"  {Colors.RED}✗{Colors.END} {msg}")


def print_info(msg):
    print(f"  {Colors.BLUE}→{Colors.END} {msg}")


def print_section(title):
    print(f"\n{Colors.YELLOW}{'─'*50}")
    print(f"  {title}")
    print(f"{'─'*50}{Colors.END}")


def run_command(command, description, exit_on_error=True):
    """Ejecuta un comando y muestra el resultado."""
    print_section(description)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            print_error(f"Error: {result.stderr.strip()}")
            if exit_on_error:
                sys.exit(1)
            return False
        
        if result.stdout.strip():
            for line in result.stdout.strip().split('\n')[:5]:
                print_info(line)
        
        print_success(f"{description} completado")
        return True
        
    except subprocess.TimeoutExpired:
        print_error("Tiempo de espera agotado")
        return False
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        return False


def check_requirements():
    """Verifica requisitos del sistema."""
    print_section("Verificando requisitos")
    
    # Python version
    py_version = sys.version_info
    if py_version.major == 3 and 8 <= py_version.minor <= 12:
        print_success(f"Python {py_version.major}.{py_version.minor}.{py_version.micro}")
    else:
        print_error(f"Python {py_version.major}.{py_version.minor} no compatible (requiere 3.8-3.12)")
        sys.exit(1)
    
    # pip
    if shutil.which("pip") or shutil.which("pip3"):
        print_success("pip disponible")
    else:
        print_error("pip no encontrado")
        sys.exit(1)
    
    # requirements.txt
    if Path("requirements.txt").exists():
        print_success("requirements.txt encontrado")
    else:
        print_error("requirements.txt no encontrado")
        sys.exit(1)
    
    # manage.py
    if Path("manage.py").exists():
        print_success("manage.py encontrado")
    else:
        print_error("manage.py no encontrado - ¿Estás en el directorio correcto?")
        sys.exit(1)


def create_directories():
    """Crea los directorios necesarios."""
    print_section("Creando estructura de directorios")
    
    directories = [
        'frontend',
        'media',
        'ml_models',
        'staticfiles',
        'logs',
        'predictions/management/commands',
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print_success(f"Directorio: {directory}")
    
    # Archivos __init__.py
    init_files = [
        'predictions/__init__.py',
        'predictions/management/__init__.py',
        'predictions/management/commands/__init__.py',
    ]
    
    for init_file in init_files:
        Path(init_file).touch(exist_ok=True)
    
    print_success("Archivos __init__.py creados")


def create_env_file():
    """Crea archivo .env si no existe."""
    env_path = Path(".env")
    env_example = Path(".env.example")
    
    if not env_path.exists():
        if env_example.exists():
            shutil.copy(env_example, env_path)
            print_success(".env creado desde .env.example")
        else:
            env_content = """# Django
DEBUG=True
SECRET_KEY=cambiar-esta-clave-en-produccion
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos (para Docker)
DB_NAME=gaia_db
DB_USER=gaia_user
DB_PASSWORD=gaia_password
DB_HOST=db
DB_PORT=5432
"""
            env_path.write_text(env_content)
            print_success(".env creado con valores por defecto")
    else:
        print_info(".env ya existe, no se modificó")


def print_completion():
    print(f"""
    {Colors.GREEN}{Colors.BOLD}
    ╔════════════════════════════════════════════╗
    ║                                            ║
    ║       ✓ INSTALACIÓN COMPLETADA             ║
    ║                                            ║
    ╚════════════════════════════════════════════╝
    {Colors.END}
    {Colors.CYAN}¿Qué sigue?{Colors.END}
    
    1. Crear superusuario:
       {Colors.YELLOW}python manage.py createsuperuser{Colors.END}
    
    2. Iniciar el servidor:
       {Colors.YELLOW}python manage.py runserver{Colors.END}
    
    3. O con Docker:
       {Colors.YELLOW}docker-compose up --build{Colors.END}
    
    4. Abrir en el navegador:
       {Colors.BLUE}http://localhost:8000/{Colors.END}
    
    {Colors.GREEN}🌍 Vívelo, Siéntelo, Ámalo. Bienvenido a GAIA.{Colors.END}
    """)


def setup_gaia():
    """Función principal de configuración."""
    print_banner()
    
    # Verificaciones
    check_requirements()
    
    # Crear estructura
    create_directories()
    create_env_file()
    
    # Instalar dependencias
    pip_cmd = "pip3" if shutil.which("pip3") else "pip"
    run_command(
        f"{pip_cmd} install -r requirements.txt",
        "Instalando dependencias"
    )
    
    # Migraciones
    run_command(
        "python manage.py makemigrations",
        "Creando migraciones"
    )
    
    run_command(
        "python manage.py migrate",
        "Aplicando migraciones"
    )
    
    # Entrenar modelo (opcional, no detiene si falla)
    run_command(
        "python manage.py train_model",
        "Entrenando modelo ML",
        exit_on_error=False
    )
    
    # Colectar archivos estáticos
    run_command(
        "python manage.py collectstatic --noinput",
        "Recolectando archivos estáticos",
        exit_on_error=False
    )
    
    print_completion()


if __name__ == '__main__':
    try:
        setup_gaia()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Instalación cancelada por el usuario.{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Error fatal: {e}{Colors.END}")
        sys.exit(1)