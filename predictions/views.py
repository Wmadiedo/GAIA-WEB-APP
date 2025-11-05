from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import models
import pandas as pd

from .models import Dataset, SoilData, Prediction
from .serializers import (
    DatasetSerializer, SoilDataSerializer, PredictionSerializer, 
    ManualPredictionSerializer
)
from .ml_model import ml_model

class DatasetViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar datasets"""
    serializer_class = DatasetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Dataset.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        dataset = serializer.save(
            user=self.request.user,
            file_size=self.request.FILES['file'].size
        )
        
        try:
            df = pd.read_csv(dataset.file.path)
            dataset.rows_count = len(df)
            dataset.save()
        except Exception as e:
            dataset.delete()
            raise serializer.ValidationError(f"Error procesando CSV: {str(e)}")

class SoilDataViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar datos de suelo"""
    serializer_class = SoilDataSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SoilData.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@api_view(['POST'])
def upload_csv(request):
    """Subir archivo CSV y procesarlo"""
    if 'file' not in request.FILES:
        return Response({'error': 'No se encontró archivo'}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    if not file.name.endswith('.csv'):
        return Response({'error': 'Solo se permiten archivos CSV'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        dataset_serializer = DatasetSerializer(data={
            'name': file.name,
            'file': file
        })
        
        if dataset_serializer.is_valid():
            dataset = dataset_serializer.save(
                user=request.user,
                file_size=file.size
            )
            
            # Leer y validar CSV
            df = pd.read_csv(dataset.file.path)
            
            required_columns = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                dataset.delete()
                return Response({
                    'error': f'Columnas faltantes: {", ".join(missing_columns)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Procesar datos y crear registros SoilData
            soil_data_records = []
            for _, row in df.iterrows():
                try:
                    soil_data = SoilData(
                        user=request.user,
                        dataset=dataset,
                        nitrogen=float(row['N']),
                        phosphorus=float(row['P']),
                        potassium=float(row['K']),
                        temperature=float(row['temperature']),
                        humidity=float(row['humidity']),
                        ph=float(row['ph']),
                        rainfall=float(row['rainfall'])
                    )
                    soil_data_records.append(soil_data)
                except (ValueError, KeyError) as e:
                    dataset.delete()
                    return Response({
                        'error': f'Error en los datos: {str(e)}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Guardar en lotes (límite de 1000 registros)
            SoilData.objects.bulk_create(soil_data_records[:1000])
            
            dataset.rows_count = len(soil_data_records)
            dataset.save()
            
            return Response({
                'message': f'CSV procesado exitosamente. {len(soil_data_records)} registros cargados.',
                'dataset_id': dataset.id,
                'rows_count': dataset.rows_count
            }, status=status.HTTP_201_CREATED)
        
        return Response(dataset_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'error': f'Error procesando archivo: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def predict_manual(request):
    """Predicción manual con datos individuales"""
    serializer = ManualPredictionSerializer(data=request.data)
    
    if serializer.is_valid():
        # Crear registro SoilData
        soil_data = SoilData.objects.create(
            user=request.user,
            **serializer.validated_data
        )
        
        # Realizar predicción
        try:
            predictions = ml_model.predict(serializer.validated_data)
            
            # Crear registro de predicción
            prediction_record = Prediction.objects.create(
                user=request.user,
                soil_data=soil_data,
                predicted_crop=predictions[0]['crop'],
                confidence_score=predictions[0]['confidence'],
                second_crop=predictions[1]['crop'] if len(predictions) > 1 else None,
                second_confidence=predictions[1]['confidence'] if len(predictions) > 1 else None,
                third_crop=predictions[2]['crop'] if len(predictions) > 2 else None,
                third_confidence=predictions[2]['confidence'] if len(predictions) > 2 else None,
                model_version='1.0'
            )
            
            return Response({
                'prediction_id': prediction_record.id,
                'predictions': predictions,
                'soil_data_id': soil_data.id,
                'message': 'Predicción realizada exitosamente'
            })
            
        except Exception as e:
            return Response({
                'error': f'Error en la predicción: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def predict_csv(request, dataset_id):
    """Predicción para dataset CSV completo"""
    dataset = get_object_or_404(Dataset, id=dataset_id, user=request.user)
    
    try:
        soil_data_records = SoilData.objects.filter(dataset=dataset)
        
        if not soil_data_records.exists():
            return Response({
                'error': 'No se encontraron datos de suelo para este dataset'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        predictions_results = []
        prediction_records = []
        
        # Realizar predicciones (límite de 100 por request)
        for soil_data in soil_data_records[:100]:
            soil_dict = {
                'N': soil_data.nitrogen,
                'P': soil_data.phosphorus,
                'K': soil_data.potassium,
                'temperature': soil_data.temperature,
                'humidity': soil_data.humidity,
                'ph': soil_data.ph,
                'rainfall': soil_data.rainfall
            }
            
            predictions = ml_model.predict(soil_dict)
            predictions_results.append({
                'soil_data_id': soil_data.id,
                'predictions': predictions
            })
            
            prediction_record = Prediction(
                user=request.user,
                dataset=dataset,
                soil_data=soil_data,
                predicted_crop=predictions[0]['crop'],
                confidence_score=predictions[0]['confidence'],
                second_crop=predictions[1]['crop'] if len(predictions) > 1 else None,
                second_confidence=predictions[1]['confidence'] if len(predictions) > 1 else None,
                third_crop=predictions[2]['crop'] if len(predictions) > 2 else None,
                third_confidence=predictions[2]['confidence'] if len(predictions) > 2 else None,
                model_version='1.0'
            )
            prediction_records.append(prediction_record)
        
        # Guardar predicciones en lotes
        Prediction.objects.bulk_create(prediction_records)
        
        return Response({
            'message': f'Predicciones completadas para {len(predictions_results)} registros',
            'dataset_id': dataset.id,
            'predictions_count': len(predictions_results),
            'predictions': predictions_results[:10]  # Mostrar solo las primeras 10
        })
        
    except Exception as e:
        return Response({
            'error': f'Error en las predicciones: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PredictionViewSet(viewsets.ReadOnlyModelViewSet):
    """Vista para consultar historial de predicciones"""
    serializer_class = PredictionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Prediction.objects.filter(user=self.request.user)
        dataset_id = self.request.query_params.get('dataset_id')
        if dataset_id:
            queryset = queryset.filter(dataset_id=dataset_id)
        return queryset

@api_view(['GET'])
def dashboard_stats(request):
    """Estadísticas del dashboard del usuario"""
    user = request.user
    
    datasets_count = Dataset.objects.filter(user=user).count()
    predictions_count = Prediction.objects.filter(user=user).count()
    soil_data_count = SoilData.objects.filter(user=user).count()
    
    # Cultivos más predichos
    top_crops = (Prediction.objects.filter(user=user)
                 .values('predicted_crop')
                 .annotate(count=models.Count('predicted_crop'))
                 .order_by('-count')[:5])
    
    # Predicciones recientes
    recent_predictions = (Prediction.objects.filter(user=user)
                         .select_related('soil_data')
                         .order_by('-created_at')[:10])
    
    recent_predictions_data = []
    for pred in recent_predictions:
        recent_predictions_data.append({
            'id': pred.id,
            'crop': pred.predicted_crop,
            'confidence': pred.confidence_score,
            'created_at': pred.created_at,
            'soil_data': {
                'nitrogen': pred.soil_data.nitrogen,
                'phosphorus': pred.soil_data.phosphorus,
                'potassium': pred.soil_data.potassium,
                'temperature': pred.soil_data.temperature,
                'humidity': pred.soil_data.humidity,
                'ph': pred.soil_data.ph,
                'rainfall': pred.soil_data.rainfall
            }
        })
    
    return Response({
        'stats': {
            'datasets_count': datasets_count,
            'predictions_count': predictions_count,
            'soil_data_count': soil_data_count
        },
        'top_crops': list(top_crops),
        'recent_predictions': recent_predictions_data
    })

@api_view(['GET'])
def crop_info(request, crop_name):
    """Información detallada de un cultivo"""
    crop_data = ml_model.crop_info.get(crop_name.lower())
    
    if not crop_data:
        return Response({
            'error': 'Cultivo no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    
    predictions_count = Prediction.objects.filter(
        user=request.user,
        predicted_crop=crop_name.lower()
    ).count()
    
    avg_confidence = (Prediction.objects.filter(
        user=request.user,
        predicted_crop=crop_name.lower()
    ).aggregate(avg_confidence=models.Avg('confidence_score'))['avg_confidence'] or 0)
    
    return Response({
        'crop_info': {
            'name': crop_data['name'],
            'season': crop_data['season'],
            'harvest_time': crop_data['harvest_time'],
            'key': crop_name.lower()
        },
        'user_stats': {
            'predictions_count': predictions_count,
            'avg_confidence': round(avg_confidence, 2)
        }
    })
