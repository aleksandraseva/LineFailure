from django.core.management.base import BaseCommand
from Lines.services.MUXParser import find_all_service


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        print("aa")
        find_all_service()
