import json
import itertools
from django.conf import settings
from django.core.management import BaseCommand
from gdp.models import GDP


class Command(BaseCommand):
    help = 'Load GDP Data to DB'

    def handle(self, *args, **kwargs):
        if not GDP.objects.count():
            datafile = settings.BASE_DIR / 'data' / 'gdp.json'
            with open(datafile, 'r') as f:
                data = json.load(f)

            data = itertools.dropwhile(lambda x: x['Country Name'] != 'Afghanistan', data)

            gdps = []
            for d in data:
                gdps.append(GDP(
                    country = d['Country Name'],
                    country_code = d['Country Code'],
                    year = d['Year'],
                    gdp = d['Value']
                ))

            GDP.objects.bulk_create(gdps)
