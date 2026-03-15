from Lines.services.MUXParser import *
import Lines.views.lines
from django.http import HttpResponse


def debug_parser(request):
    # find_all_service()  # ovdje stavi breakpoint u servis
    return HttpResponse("done")
