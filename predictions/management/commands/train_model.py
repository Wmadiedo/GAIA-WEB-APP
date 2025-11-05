from django.core.management.base import BaseCommand
from predictions.ml_model import ml_model

class Command(BaseCommand):
    help = 'Entrenar el modelo de predicción de cultivos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--retrain',
            action='store_true',
            help='Forzar reentrenamiento del modelo',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando entrenamiento del modelo...'))
        
        try:
            ml_model.train_model(retrain=options['retrain'])
            self.stdout.write(
                self.style.SUCCESS(' Modelo entrenado exitosamente!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f' Error entrenando modelo: {str(e)}')
            )