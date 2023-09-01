import csv
import os

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        if Ingredient.objects.exists():
            print("Данные уже загружены...выход!")
            return
        print("Загрузка Ingredients данных")

        csv_file_path = os.path.join(
            settings.BASE_DIR, "data", "ingredients.csv")

        try:
            with open(csv_file_path, "r", encoding="utf-8") as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    db = Ingredient(
                        name=row["name"],
                        measurement_unit=row["measurement_unit"]
                    )
                    db.save()
                print("Ingredients импортированы.")
        except FileNotFoundError:
            print("CSV file не найден.")
        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")
