import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт данных из csv файлов в БД.'

    def handle(self, *args, **options):
        self.import_ingredients()

    def import_ingredients(self):
        file_path = 'data/ingredients.csv'

        with open(file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)

            for row in reader:
                ingredient = Ingredient.objects.create(
                    name=row[0],
                    measurement_unit=row[1]
                )
                ingredient.save()