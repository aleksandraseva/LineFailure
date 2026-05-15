from django.core.management.base import BaseCommand
from Lines.services.MUXParser import find_all_service
from Lines.services.parseExcel import find_connection
from Lines.services.MUXParser import remove_duplicate_routes


class Command(BaseCommand):
    help = "Fill database"

    def handle(self, *args, **kwargs):

        find_connection()
        find_all_service()
        # remove_duplicate_routes()
