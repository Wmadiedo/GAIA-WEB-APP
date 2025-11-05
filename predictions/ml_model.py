import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os
from django.conf import settings

class CropPredictionModel:
    """Modelo Random Forest para predicción de cultivos"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.crop_labels = {
            0: 'rice', 1: 'maize', 2: 'chickpea', 3: 'kidneybeans', 4: 'pigeonpeas',
            5: 'mothbeans', 6: 'mungbean', 7: 'blackgram', 8: 'lentil', 9: 'pomegranate',
            10: 'banana', 11: 'mango', 12: 'grapes', 13: 'watermelon', 14: 'muskmelon',
            15: 'apple', 16: 'orange', 17: 'papaya', 18: 'coconut', 19: 'cotton',
            20: 'jute', 21: 'coffee'
        }
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
    
    def create_synthetic_data(self, n_samples=2200):
        """Crear datos sintéticos para entrenamiento"""
        np.random.seed(42)
        data = []
        
        crop_params = {
            0: {'N': [20, 80], 'P': [5, 40], 'K': [5, 40], 'temp': [20, 30], 'hum': [80, 95], 'ph': [5.5, 7.0], 'rain': [150, 300]},
            1: {'N': [80, 120], 'P': [40, 80], 'K': [40, 80], 'temp': [18, 27], 'hum': [55, 75], 'ph': [6.0, 7.5], 'rain': [60, 120]},
            2: {'N': [40, 80], 'P': [60, 80], 'K': [80, 120], 'temp': [17, 25], 'hum': [10, 40], 'ph': [6.0, 7.5], 'rain': [15, 45]},
        }
        
        samples_per_crop = n_samples // len(self.crop_labels)
        for crop_id in range(len(self.crop_labels)):
            params = crop_params.get(crop_id, {
                'N': [20, 140], 'P': [5, 145], 'K': [5, 205], 
                'temp': [8.8, 43.7], 'hum': [14, 99], 
                'ph': [3.5, 9.9], 'rain': [20, 298]
            })
            
            for _ in range(samples_per_crop):
                sample = [
                    np.random.uniform(params['N'][0], params['N'][1]),
                    np.random.uniform(params['P'][0], params['P'][1]),
                    np.random.uniform(params['K'][0], params['K'][1]),
                    np.random.uniform(params['temp'][0], params['temp'][1]),
                    np.random.uniform(params['hum'][0], params['hum'][1]),
                    np.random.uniform(params['ph'][0], params['ph'][1]),
                    np.random.uniform(params['rain'][0], params['rain'][1])
                ]
                sample.append(crop_id)
                data.append(sample)
        
        columns = self.feature_names + ['label']
        return pd.DataFrame(data, columns=columns)
    
    def train_model(self, retrain=False):
        """Entrenar el modelo Random Forest"""
        model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'crop_model.pkl')
        scaler_path = os.path.join(settings.BASE_DIR, 'ml_models', 'scaler.pkl')
        
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        if not retrain and os.path.exists(model_path) and os.path.exists(scaler_path):
            print("Cargando modelo pre-entrenado...")
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            return
        
        print("Entrenando nuevo modelo Random Forest...")
        
        df = self.create_synthetic_data()
        X = df[self.feature_names]
        y = df['label']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        from sklearn.metrics import accuracy_score
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Precisión del modelo: {accuracy:.4f}")
        
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        print("Modelo guardado exitosamente.")
    
    def predict(self, soil_data):
        """Realizar predicción"""
        if self.model is None or self.scaler is None:
            self.train_model()
        
        if isinstance(soil_data, dict):
            features = [soil_data[feature] for feature in self.feature_names]
            features = np.array(features).reshape(1, -1)
        else:
            features = np.array(soil_data).reshape(1, -1)
        
        features_scaled = self.scaler.transform(features)
        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]
        
        top_indices = np.argsort(probabilities)[-3:][::-1]
        
        results = []
        for idx in top_indices:
            crop_key = self.crop_labels[idx]
            crop_info = self.crop_info.get(crop_key, {'name': crop_key.title()})
            results.append({
                'crop': crop_key,
                'crop_name': crop_info['name'],
                'confidence': round(probabilities[idx] * 100, 2),
                'season': crop_info.get('season', 'N/A'),
                'harvest_time': crop_info.get('harvest_time', 'N/A')
            })
        
        return results

# Instancia global del modelo
ml_model = CropPredictionModel()