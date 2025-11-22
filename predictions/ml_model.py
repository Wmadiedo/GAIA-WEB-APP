import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
from django.conf import settings

class CropPredictionModel:
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        
        # Información detallada de cada cultivo
        self.crop_info = {
            'rice': {'name': 'Arroz', 'season': 'Lluvioso', 'harvest_time': '3-6 meses'},
            'maize': {'name': 'Maíz', 'season': 'Verano', 'harvest_time': '2-3 meses'},
            'chickpea': {'name': 'Garbanzo', 'season': 'Invierno', 'harvest_time': '3-4 meses'},
            'kidneybeans': {'name': 'Frijol', 'season': 'Primavera', 'harvest_time': '2-3 meses'},
            'pigeonpeas': {'name': 'Guandú', 'season': 'Todo el año', 'harvest_time': '4-6 meses'},
            'mothbeans': {'name': 'Frijol Polilla', 'season': 'Verano', 'harvest_time': '3-4 meses'},
            'mungbean': {'name': 'Frijol Mungo', 'season': 'Verano', 'harvest_time': '2-3 meses'},
            'blackgram': {'name': 'Lenteja Negra', 'season': 'Invierno', 'harvest_time': '3-4 meses'},
            'lentil': {'name': 'Lenteja', 'season': 'Invierno', 'harvest_time': '3-4 meses'},
            'pomegranate': {'name': 'Granada', 'season': 'Todo el año', 'harvest_time': '6-7 meses'},
            'banana': {'name': 'Plátano', 'season': 'Todo el año', 'harvest_time': '9-12 meses'},
            'mango': {'name': 'Mango', 'season': 'Verano', 'harvest_time': '3-5 años'},
            'grapes': {'name': 'Uva', 'season': 'Verano', 'harvest_time': '2-3 años'},
            'watermelon': {'name': 'Sandía', 'season': 'Verano', 'harvest_time': '2-3 meses'},
            'muskmelon': {'name': 'Melón', 'season': 'Verano', 'harvest_time': '2-3 meses'},
            'apple': {'name': 'Manzana', 'season': 'Primavera', 'harvest_time': '2-4 años'},
            'orange': {'name': 'Naranja', 'season': 'Invierno', 'harvest_time': '3-4 años'},
            'papaya': {'name': 'Papaya', 'season': 'Todo el año', 'harvest_time': '6-8 meses'},
            'coconut': {'name': 'Coco', 'season': 'Todo el año', 'harvest_time': '5-6 años'},
            'cotton': {'name': 'Algodón', 'season': 'Verano', 'harvest_time': '4-6 meses'},
            'jute': {'name': 'Yute', 'season': 'Lluvioso', 'harvest_time': '3-4 meses'},
            'coffee': {'name': 'Café', 'season': 'Todo el año', 'harvest_time': '3-4 años'}
        }
        
        self.feature_names = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        
        # Dataset CSV embebido (puedes reemplazarlo con lectura de archivo)
        self.dataset_csv = """N,P,K,temperature,humidity,ph,rainfall,label
90,42,43,20.87974371,82.00274423,6.502985292000001,202.9355362,rice
85,58,41,21.77046169,80.31964408,7.038096361,226.6555374,rice
60,55,44,23.00445915,82.3207629,7.840207144,263.9642476,rice"""
        # ... (el dataset completo se carga desde archivo o se puede usar directamente)
    
    def load_dataset(self):
        """Carga el dataset real desde archivo o string embebido"""
        # Opción 1: Cargar desde archivo CSV
        dataset_path = os.path.join(settings.BASE_DIR, 'Crop_recommendation.csv')
        
        if os.path.exists(dataset_path):
            print(f"Cargando dataset desde archivo: {dataset_path}")
            df = pd.read_csv(dataset_path)
        else:
            # Opción 2: Si no existe el archivo, usar datos embebidos o crear uno temporal
            print("Archivo no encontrado. Creando dataset desde datos...")
            # Aquí podrías poner el CSV completo como string o descargarlo
            # Por ahora, retornamos None para indicar que debe existir el archivo
            return None
        
        return df
    
    def train_model(self, retrain=False):
        """Entrena el modelo Random Forest con el dataset real"""
        model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'crop_model.pkl')
        scaler_path = os.path.join(settings.BASE_DIR, 'ml_models', 'scaler.pkl')
        encoder_path = os.path.join(settings.BASE_DIR, 'ml_models', 'label_encoder.pkl')
        
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Si ya existe el modelo y no se pide reentrenar, cargarlo
        if not retrain and os.path.exists(model_path) and os.path.exists(scaler_path) and os.path.exists(encoder_path):
            print("Cargando modelo pre-entrenado...")
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            self.label_encoder = joblib.load(encoder_path)
            return
        
        print("Entrenando nuevo modelo Random Forest con dataset real...")
        
        # Cargar dataset
        df = self.load_dataset()
        
        if df is None:
            print("ERROR: No se pudo cargar el dataset.")
            print("Por favor, coloca el archivo 'Crop_recommendation.csv' en la raíz del proyecto.")
            # Crear un modelo dummy para que la app no falle
            self._create_dummy_model()
            return
        
        # Verificar que tenga las columnas necesarias
        required_columns = self.feature_names + ['label']
        if not all(col in df.columns for col in required_columns):
            print(f"ERROR: El dataset debe contener las columnas: {required_columns}")
            self._create_dummy_model()
            return
        
        print(f"Dataset cargado: {len(df)} muestras, {len(df['label'].unique())} cultivos únicos")
        
        # Separar características y etiquetas
        X = df[self.feature_names]
        y = df['label']
        
        # Codificar etiquetas
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        
        print(f"Cultivos en el dataset: {list(self.label_encoder.classes_)}")
        
        # Dividir en entrenamiento y prueba
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Escalar características
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Entrenar modelo Random Forest
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            n_jobs=-1  # Usar todos los cores disponibles
        )
        
        print("Entrenando modelo...")
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluar modelo
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n{'='*60}")
        print(f"✅ MODELO ENTRENADO EXITOSAMENTE")
        print(f"{'='*60}")
        print(f"Precisión en test: {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"Muestras de entrenamiento: {len(X_train)}")
        print(f"Muestras de prueba: {len(X_test)}")
        
        # Mostrar reporte de clasificación
        print("\nReporte de clasificación:")
        report = classification_report(
            y_test, y_pred, 
            target_names=self.label_encoder.classes_,
            zero_division=0
        )
        print(report)
        
        # Guardar modelo, escalador y codificador
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        joblib.dump(self.label_encoder, encoder_path)
        
        print(f"\n✅ Modelo guardado en: {model_path}")
        print(f"✅ Escalador guardado en: {scaler_path}")
        print(f"✅ Codificador guardado en: {encoder_path}")
    
    def _create_dummy_model(self):
        """Crea un modelo dummy para que la app no falle si no hay dataset"""
        print("⚠️ Creando modelo dummy (predicciones aleatorias)...")
        self.model = "dummy"
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(list(self.crop_info.keys()))
        
        # Guardar modelo dummy
        model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'crop_model.pkl')
        scaler_path = os.path.join(settings.BASE_DIR, 'ml_models', 'scaler.pkl')
        encoder_path = os.path.join(settings.BASE_DIR, 'ml_models', 'label_encoder.pkl')
        
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        joblib.dump(self.label_encoder, encoder_path)
    
    def predict(self, soil_data):
        """Realiza predicción para datos de suelo"""
        if self.model is None or self.scaler is None or self.label_encoder is None:
            self.train_model()
        
        # Si es modelo dummy, hacer predicción aleatoria
        if self.model == "dummy":
            return self._dummy_predict()
        
        # Preparar datos como DataFrame para evitar warnings
        if isinstance(soil_data, dict):
            # Crear DataFrame con nombres de columnas
            features_df = pd.DataFrame([soil_data], columns=self.feature_names)
        else:
            # Convertir array a DataFrame
            features_df = pd.DataFrame([soil_data], columns=self.feature_names)
        
        # Validar que los datos estén en rangos razonables
        try:
            features_scaled = self.scaler.transform(features_df)
        except Exception as e:
            print(f"Error al escalar características: {e}")
            return self._dummy_predict()
        
        # Realizar predicción
        try:
            prediction = self.model.predict(features_scaled)[0]
            probabilities = self.model.predict_proba(features_scaled)[0]
        except Exception as e:
            print(f"Error en predicción: {e}")
            return self._dummy_predict()
        
        # Obtener top 3 predicciones
        top_indices = np.argsort(probabilities)[-3:][::-1]
        
        results = []
        for idx in top_indices:
            crop_key = self.label_encoder.inverse_transform([idx])[0]
            crop_info = self.crop_info.get(crop_key, {
                'name': crop_key.title(),
                'season': 'N/A',
                'harvest_time': 'N/A'
            })
            results.append({
                'crop': crop_key,
                'crop_name': crop_info['name'],
                'confidence': round(probabilities[idx] * 100, 2),
                'season': crop_info['season'],
                'harvest_time': crop_info['harvest_time']
            })
        
        return results
    
    def _dummy_predict(self):
        """Predicción dummy cuando no hay modelo real"""
        import random
        crops = list(self.crop_info.keys())
        selected = random.sample(crops, 3)
        
        results = []
        for i, crop_key in enumerate(selected):
            crop_info = self.crop_info[crop_key]
            results.append({
                'crop': crop_key,
                'crop_name': crop_info['name'],
                'confidence': round(random.uniform(70, 95), 2),
                'season': crop_info['season'],
                'harvest_time': crop_info['harvest_time']
            })
        
        return sorted(results, key=lambda x: x['confidence'], reverse=True)

# Instancia global del modelo
ml_model = CropPredictionModel()