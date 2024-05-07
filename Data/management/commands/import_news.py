import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from Data.models import News


class Command(BaseCommand):
    help = 'Imports news data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convert date string to datetime object
                date_object = datetime.strptime(row['date'], "%Y-%m-%d")
                # Save news data to database
                News.objects.create(date=date_object, headline=row['headline'], website=row['website'])
        self.stdout.write(self.style.SUCCESS('News data imported successfully!'))

# python manage.py import_news static/data/merged_news_final.csv
