from django.core.management.base import BaseCommand
from Lines.services import MUXParser, parseExcel, AddLine


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        print("aa")
        MUXParser.find_all_service()
        parseExcel.find_connection()
        AddLine.add_line()
