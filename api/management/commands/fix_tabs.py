from django.core.management.base import BaseCommand
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent.parent / 'views.py'

class Command(BaseCommand):
    help = 'Replace any tab characters in api/views.py with 4 spaces.'

    def handle(self, *args, **options):
        text = TARGET.read_text(encoding='utf-8')
        if '\t' not in text:
            self.stdout.write(self.style.SUCCESS('No tabs found.'))
            return
        new_text = text.replace('\t', '    ')
        TARGET.write_text(new_text, encoding='utf-8')
        self.stdout.write(self.style.SUCCESS('Tabs replaced with spaces.'))
