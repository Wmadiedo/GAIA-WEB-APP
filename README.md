# GAIA-WEB-APP
Web app for cellphone &amp; computers.
INSTRUCCIONES DE INSTALACIÓN:

1. Crear entorno virtual:
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate

2. Instalar dependencias:
   pip install -r requirements.txt

3. Configurar base de datos:
   - Instalar PostgreSQL
   - Crear base de datos 'agropredict'
   - Configurar variables de entorno en .env

4. Ejecutar migraciones:
   python manage.py makemigrations
   python manage.py migrate

5. Crear superusuario:
   python manage.py createsuperuser

6. Entrenar modelo:
   python manage.py train_model

7. Ejecutar servidor:
   python manage.py runserver

ENDPOINTS PRINCIPALES:

Autenticación:
- POST /api/auth/register/ - Registro de usuario
- POST /api/auth/login/ - Inicio de sesión
- POST /api/auth/token/refresh/ - Renovar token
- GET /api/auth/profile/ - Perfil de usuario

Datasets:
- GET /api/datasets/ - Listar datasets
- POST /api/datasets/ - Crear dataset
- GET /api/datasets/{id}/ - Obtener dataset
- DELETE /api/datasets/{id}/ - Eliminar dataset

Predicciones:
- POST /api/upload/ - Subir CSV
- POST /api/predict/manual/ - Predicción manual
- POST /api/predict/csv/{dataset_id}/ - Predicción de CSV
- GET /api/predictions/ - Historial de predicciones
- GET /api/dashboard/ - Estadísticas del dashboard
- GET /api/crop-info/{crop_name}/ - Info de cultivo

Datos de Suelo:
- GET /api/soil-data/ - Listar datos de suelo
- POST /api/soil-data/ - Crear datos de suelo